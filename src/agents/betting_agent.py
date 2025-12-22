from src.models.bankroll_manager import BankrollManager
from src.models.probability_model import ProbabilityModel
from src.services.football_api import FootballAPI
from src.services.odds_api import OddsAPI
from typing import List, Dict

class BettingAgent:
    """Agente principal que orquestra análises e sugestões"""
    
    def __init__(self, current_bankroll: float):
        self.bankroll_manager = BankrollManager(current_bankroll)
        self.probability_model = ProbabilityModel()
        self.football_api = FootballAPI()
        self.odds_api = OddsAPI()
    
    def analyze_today_opportunities(self) -> List[Dict]:
        """Analisa todas oportunidades do dia"""
        print("🔍 Buscando jogos de hoje...")
        
        # Verifica se tem API configurada
        api_key = self.football_api.api_key
        if not api_key or api_key == 'your_api_key_here':
            print("⚠️  API não configurada. Usando dados simulados para teste...")
            from src.utils.mock_data import get_mock_matches, get_mock_odds
            matches = get_mock_matches()
            odds_data = get_mock_odds()
        else:
            matches = self.football_api.get_today_matches()
            if not matches:
                return []
            odds_data = self.odds_api.get_odds_for_match()
        
        print(f"📊 Encontrados {len(matches)} jogos")
        print("💰 Analisando odds...")
        
        opportunities = []
        phase_info = self.bankroll_manager.get_phase_info()
        
        for match in matches:
            match_odds = self._find_match_odds(match, odds_data)
            
            if not match_odds:
                continue
            
            # Analisa cada mercado
            opps = self._analyze_match_markets(match, match_odds, phase_info)
            opportunities.extend(opps)
        
        # Ordena por EV
        opportunities.sort(key=lambda x: x['ev'], reverse=True)
        
        return opportunities
    
    def _find_match_odds(self, match: Dict, odds_data: List[Dict]) -> Dict:
        """Encontra odds para o jogo específico"""
        for odds in odds_data:
            if (odds['home_team'].lower() in match['home_team'].lower() or
                odds['away_team'].lower() in match['away_team'].lower()):
                return odds
        return {}
    
    def _analyze_match_markets(self, match: Dict, odds: Dict, phase_info: Dict) -> List[Dict]:
        """Analisa mercados disponíveis do jogo"""
        opportunities = []
        markets = odds.get('markets', {})
        
        # Simula stats (em produção viria da API)
        home_stats = {'avg_scored': 1.8, 'avg_conceded': 1.2}
        away_stats = {'avg_scored': 1.5, 'avg_conceded': 1.3}
        
        # Analisa Over 2.5
        if 'over_2.5' in markets:
            opp = self._analyze_over_under(match, odds, home_stats, away_stats, 
                                          2.5, markets['over_2.5'], phase_info)
            if opp:
                opportunities.append(opp)
        
        # Analisa BTTS
        if 'btts_yes' in markets:
            opp = self._analyze_btts(match, odds, home_stats, away_stats, 
                                    markets['btts_yes'], phase_info)
            if opp:
                opportunities.append(opp)
        
        return opportunities
    
    def _analyze_over_under(self, match: Dict, odds: Dict, home_stats: Dict, 
                           away_stats: Dict, line: float, market_odds: float, 
                           phase_info: Dict) -> Dict:
        """Analisa oportunidade de Over/Under"""
        probs = self.probability_model.calculate_over_under(
            home_stats['avg_scored'], 
            away_stats['avg_scored'], 
            line
        )
        
        is_valid, ev = self.probability_model.validate_opportunity(
            probs['prob_over'], 
            market_odds, 
            phase_info['min_ev']
        )
        
        if not is_valid:
            return None
        
        stake = self.bankroll_manager.calculate_stake(
            probs['prob_over'], 
            market_odds, 
            ev
        )
        
        return {
            'match': f"{match['home_team']} x {match['away_team']}",
            'competition': match['competition'],
            'date': match['date'],
            'market': f'Over {line}',
            'odds': market_odds,
            'probability': probs['prob_over'],
            'ev': ev,
            'stake': stake,
            'potential_return': round(stake * market_odds, 2)
        }
    
    def _analyze_btts(self, match: Dict, odds: Dict, home_stats: Dict, 
                     away_stats: Dict, market_odds: float, phase_info: Dict) -> Dict:
        """Analisa oportunidade de BTTS"""
        prob_btts = self.probability_model.calculate_btts(
            home_stats['avg_scored'],
            home_stats['avg_conceded'],
            away_stats['avg_scored'],
            away_stats['avg_conceded']
        )
        
        is_valid, ev = self.probability_model.validate_opportunity(
            prob_btts, 
            market_odds, 
            phase_info['min_ev']
        )
        
        if not is_valid:
            return None
        
        stake = self.bankroll_manager.calculate_stake(prob_btts, market_odds, ev)
        
        return {
            'match': f"{match['home_team']} x {match['away_team']}",
            'competition': match['competition'],
            'date': match['date'],
            'market': 'BTTS (Ambas Marcam)',
            'odds': market_odds,
            'probability': prob_btts,
            'ev': ev,
            'stake': stake,
            'potential_return': round(stake * market_odds, 2)
        }
    
    def get_phase_summary(self) -> str:
        """Retorna resumo da fase atual"""
        info = self.bankroll_manager.get_phase_info()
        
        if info['phase'] == 'Consolidação':
            return f"""
✅ MODO CONSOLIDAÇÃO
Banca atual: R$ {info['bankroll']:.2f}
EV mínimo: {info['min_ev']}%
Stake máximo: {info['max_stake_pct']}%
"""
        
        return f"""
🚀 FASE {info['phase']}: ALAVANCAGEM
Banca atual: R$ {info['bankroll']:.2f}
Meta: R$ {info['target']:.2f}
Progresso: {info['progress']:.1f}%
Faltam: R$ {info['remaining']:.2f}
EV mínimo: {info['min_ev']}%
Stake máximo: {info['max_stake_pct']}%
"""