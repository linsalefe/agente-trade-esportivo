from src.models.bankroll_manager import BankrollManager
from src.models.probability_model import ProbabilityModel
from src.models.bet_history import BetHistory
from src.models.risk_manager import RiskManager
from src.models.advanced_stats import AdvancedStats
from src.services.football_api import FootballAPI
from src.services.odds_api import OddsAPI
from src.utils.validators import OpportunityValidator
from src.utils.reporter import Reporter
from src.utils.multiple_detector import MultipleDetector
from typing import List, Dict

class BettingAgent:
    """Agente principal que orquestra análises e sugestões"""
    
    def __init__(self, current_bankroll: float):
        self.bankroll_manager = BankrollManager(current_bankroll)
        self.probability_model = ProbabilityModel()
        self.football_api = FootballAPI()
        self.odds_api = OddsAPI()
        self.bet_history = BetHistory()
        self.risk_manager = RiskManager(current_bankroll, self.bankroll_manager.phase)
    
    def analyze_today_opportunities(self) -> List[Dict]:
        """Analisa todas oportunidades do dia"""
        from config.config import Config
        
        print("🔍 Buscando jogos de hoje...")
        
        # Tenta usar APIs reais
        api_key = self.football_api.api_key
        if api_key and api_key != 'your_api_key_here':
            print("✅ APIs configuradas. Usando dados reais...")
            
            try:
                # Busca jogos dos próximos 3 dias
                matches = self.football_api.get_matches_next_days(3)
                
                if not matches:
                    if Config.ENVIRONMENT == 'production':
                        print("❌ ERRO: Nenhum jogo encontrado e sistema está em PRODUÇÃO")
                        print("❌ NÃO é seguro operar sem dados reais. Abortando...")
                        return []
                    else:
                        print("⚠️  Nenhum jogo encontrado. Usando dados simulados (DEVELOPMENT)...")
                        from src.utils.mock_data import get_mock_matches, get_mock_odds
                        matches = get_mock_matches()
                        odds_data = get_mock_odds()
                else:
                    print(f"📊 Encontrados {len(matches)} jogos reais")
                    
                    # Busca odds reais
                    print("💰 Buscando odds reais...")
                    odds_data = []
                    
                    # Busca odds de múltiplas ligas
                    sports = ['soccer_epl', 'soccer_spain_la_liga', 'soccer_portugal_primeira_liga']
                    for sport in sports:
                        odds = self.odds_api.get_odds_for_match(sport)
                        odds_data.extend(odds)
                    
                    if not odds_data:
                        if Config.ENVIRONMENT == 'production':
                            print("❌ ERRO: Nenhuma odd encontrada e sistema está em PRODUÇÃO")
                            print("❌ NÃO é seguro operar sem odds reais. Abortando...")
                            return []
                        else:
                            print("⚠️  Nenhuma odd encontrada. Usando dados simulados (DEVELOPMENT)...")
                            from src.utils.mock_data import get_mock_odds
                            odds_data = get_mock_odds()
                    else:
                        print(f"💰 {len(odds_data)} jogos com odds disponíveis")
                        
            except Exception as e:
                print(f"❌ ERRO ao buscar dados das APIs: {e}")
                if Config.ENVIRONMENT == 'production':
                    print("❌ Sistema em PRODUÇÃO. Abortando por segurança...")
                    return []
                else:
                    print("⚠️  Usando dados simulados (DEVELOPMENT)...")
                    from src.utils.mock_data import get_mock_matches, get_mock_odds
                    matches = get_mock_matches()
                    odds_data = get_mock_odds()
        else:
            if Config.ENVIRONMENT == 'production':
                print("❌ ERRO: APIs não configuradas e sistema está em PRODUÇÃO")
                print("❌ Configure as API keys no .env antes de operar. Abortando...")
                return []
            else:
                print("⚠️  API não configurada. Usando dados simulados para teste (DEVELOPMENT)...")
                from src.utils.mock_data import get_mock_matches, get_mock_odds
                matches = get_mock_matches()
                odds_data = get_mock_odds()
        
        opportunities = []
        phase_info = self.bankroll_manager.get_phase_info()
        
        for match in matches:
            match_odds = self._find_match_odds(match, odds_data)
            
            if not match_odds:
                continue
            
            # Analisa cada mercado
            opps = self._analyze_match_markets(match, match_odds, phase_info)
            opportunities.extend(opps)
        
        # Valida oportunidades
        opportunities = self._validate_opportunities(opportunities, phase_info)
        
        # Ordena por EV
        opportunities.sort(key=lambda x: x['ev'], reverse=True)
        
        return opportunities
    
    def detect_multiples(self, opportunities: List[Dict]) -> List[Dict]:
        """Detecta múltiplas estratégicas"""
        # Só sugere múltiplas em fase 1 e 2 (alavancagem agressiva)
        phase = self.bankroll_manager.phase
        
        if phase not in [1, 2]:
            return []
        
        # Detecta múltiplas
        multiples = MultipleDetector.detect_multiples(
            opportunities,
            min_combined_prob=0.30,  # 30% probabilidade combinada mínima
            max_legs=3  # Máximo 3 pernas
        )
        
        # Calcula stakes para cada múltipla
        formatted_multiples = []
        for multiple in multiples[:3]:  # Top 3 múltiplas
            # Stake mais agressivo para múltiplas (5-8% da banca)
            stake_pct = 0.08 if phase == 1 else 0.05
            stake = self.bankroll_manager.bankroll * stake_pct
            
            formatted = MultipleDetector.format_multiple(multiple, stake)
            formatted_multiples.append(formatted)
        
        return formatted_multiples
    
    def _validate_opportunities(self, opportunities: List[Dict], phase_info: Dict) -> List[Dict]:
        """Valida oportunidades antes de sugerir"""
        validated = []
        
        for opp in opportunities:
            is_valid, errors = OpportunityValidator.validate_opportunity(
                opp, 
                phase_info, 
                self.bankroll_manager.bankroll
            )
            
            if is_valid:
                # Verifica limites de risco
                can_bet, msg = self.risk_manager.check_daily_limit(opp['stake'])
                if can_bet:
                    validated.append(opp)
                else:
                    print(f"⚠️  Rejeitado: {opp['match']} - {msg}")
            else:
                print(f"⚠️  Rejeitado: {opp['match']} - {errors[0]}")
        
        return validated
    
    def _find_match_odds(self, match: Dict, odds_data: List[Dict]) -> Dict:
        """Encontra odds para o jogo específico"""
        for odds in odds_data:
            home_match = odds['home_team'].lower() in match['home_team'].lower()
            away_match = odds['away_team'].lower() in match['away_team'].lower()
            
            if home_match or away_match:
                return odds
        return {}
    
    def _analyze_match_markets(self, match: Dict, odds: Dict, phase_info: Dict) -> List[Dict]:
        """Analisa mercados disponíveis do jogo"""
        opportunities = []
        markets = odds.get('markets', {})
        
        # Stats com forma recente e mando (simuladas - em produção viriam da API)
        home_team_data = {
            'base_avg_scored': 1.8,
            'base_avg_conceded': 1.2,
            'recent_form': ['W', 'W', 'W', 'D', 'W'],  # Simula boa forma
            'is_home': True
        }
        
        away_team_data = {
            'base_avg_scored': 1.5,
            'base_avg_conceded': 1.3,
            'recent_form': ['W', 'D', 'L', 'D', 'W'],  # Simula forma regular
            'is_home': False
        }
        
        # Calcula stats melhoradas
        home_stats = AdvancedStats.get_enhanced_stats(home_team_data)
        away_stats = AdvancedStats.get_enhanced_stats(away_team_data)
        
        # Analisa Over 2.5
        if 'over_2.5' in markets:
            opp = self._analyze_over_under(match, odds, home_stats, away_stats, 
                                          2.5, markets['over_2.5'], phase_info)
            if opp:
                opportunities.append(opp)
        
        # Analisa Over 2.0
        if 'over_2.0' in markets:
            opp = self._analyze_over_under(match, odds, home_stats, away_stats, 
                                          2.0, markets['over_2.0'], phase_info)
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
        
        # Aplica ajuste de risco se necessário
        stake_adjustment = self.risk_manager.get_stake_adjustment()
        stake = stake * stake_adjustment
        
        return {
            'match': f"{match['home_team']} x {match['away_team']}",
            'competition': match['competition'],
            'date': match['date'],
            'market': f'Over {line}',
            'odds': market_odds,
            'probability': probs['prob_over'],
            'ev': ev,
            'stake': round(stake, 2),
            'potential_return': round(stake * market_odds, 2),
            'phase': phase_info['phase']
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
        
        # Aplica ajuste de risco
        stake_adjustment = self.risk_manager.get_stake_adjustment()
        stake = stake * stake_adjustment
        
        return {
            'match': f"{match['home_team']} x {match['away_team']}",
            'competition': match['competition'],
            'date': match['date'],
            'market': 'BTTS (Ambas Marcam)',
            'odds': market_odds,
            'probability': prob_btts,
            'ev': ev,
            'stake': round(stake, 2),
            'potential_return': round(stake * market_odds, 2),
            'phase': phase_info['phase']
        }
    
    def register_bet(self, bet_data: Dict) -> str:
        """Registra aposta no histórico"""
        bet_id = self.bet_history.add_bet(bet_data)
        self.risk_manager.add_stake(bet_data['stake'])
        return bet_id
    
    def update_bet_result(self, bet_id: str, result: str):
        """Atualiza resultado de aposta"""
        success = self.bet_history.update_bet_result(bet_id, result)
        if success:
            self.risk_manager.update_sequence(result)
        return success
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas completas"""
        return self.bet_history.get_statistics(self.bankroll_manager.phase)
    
    def check_phase_completion(self) -> tuple:
        """Verifica se completou fase"""
        return self.bankroll_manager.check_phase_completion()
    
    def get_full_report(self, opportunities: List[Dict]) -> str:
        """Gera relatório completo"""
        phase_info = self.bankroll_manager.get_phase_info()
        risk_summary = self.risk_manager.get_risk_summary()
        
        report = Reporter.generate_daily_report(opportunities, phase_info, risk_summary)
        
        if opportunities:
            report += Reporter.format_opportunity_list(opportunities)
            
            # Detecta e mostra múltiplas
            multiples = self.detect_multiples(opportunities)
            if multiples:
                report += "\n🎯 MÚLTIPLAS ESTRATÉGICAS DETECTADAS:\n"
                for i, multiple in enumerate(multiples, 1):
                    report += Reporter.format_multiple_suggestion(multiple)
        
        # Verifica se completou fase
        completed, withdraw = self.check_phase_completion()
        if completed:
            report += Reporter.generate_phase_completion_alert(
                phase_info['phase'],
                withdraw,
                self.bankroll_manager.bankroll - withdraw
            )
        
        # Adiciona estatísticas
        stats = self.get_statistics()
        if stats['total_bets'] > 0:
            report += Reporter.generate_statistics_report(stats)
        
        return report
    
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