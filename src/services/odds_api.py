import requests
from typing import List, Dict
from config.config import Config

class OddsAPI:
    """Serviço para buscar odds de diferentes mercados"""
    
    def __init__(self):
        self.api_key = Config.ODDS_API_KEY
        self.base_url = Config.ODDS_API_BASE_URL
    
    def get_odds_for_match(self, sport: str = 'soccer_brazil_campeonato') -> List[Dict]:
        """Busca odds para jogos"""
        url = f"{self.base_url}/sports/{sport}/odds"
        
        params = {
            'apiKey': self.api_key,
            'regions': 'br,uk',
            'markets': 'h2h,totals,btts',
            'oddsFormat': 'decimal'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return self._format_odds(response.json())
        
        except Exception as e:
            print(f"Erro ao buscar odds: {e}")
            return []
    
    def _format_odds(self, data: List[Dict]) -> List[Dict]:
        """Formata odds recebidas"""
        formatted = []
        
        for game in data:
            game_data = {
                'match_id': game['id'],
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'commence_time': game['commence_time'],
                'markets': {}
            }
            
            for bookmaker in game.get('bookmakers', []):
                for market in bookmaker.get('markets', []):
                    market_key = market['key']
                    
                    if market_key == 'totals':
                        self._extract_totals(market, game_data['markets'])
                    elif market_key == 'btts':
                        self._extract_btts(market, game_data['markets'])
            
            formatted.append(game_data)
        
        return formatted
    
    def _extract_totals(self, market: Dict, markets_dict: Dict):
        """Extrai odds de Over/Under"""
        for outcome in market.get('outcomes', []):
            if outcome['name'] == 'Over':
                point = outcome.get('point', 2.5)
                key = f'over_{point}'
                if key not in markets_dict or outcome['price'] > markets_dict[key]:
                    markets_dict[key] = outcome['price']
            elif outcome['name'] == 'Under':
                point = outcome.get('point', 2.5)
                key = f'under_{point}'
                if key not in markets_dict or outcome['price'] > markets_dict[key]:
                    markets_dict[key] = outcome['price']
    
    def _extract_btts(self, market: Dict, markets_dict: Dict):
        """Extrai odds de BTTS"""
        for outcome in market.get('outcomes', []):
            if outcome['name'] == 'Yes':
                if 'btts_yes' not in markets_dict or outcome['price'] > markets_dict['btts_yes']:
                    markets_dict['btts_yes'] = outcome['price']
            elif outcome['name'] == 'No':
                if 'btts_no' not in markets_dict or outcome['price'] > markets_dict['btts_no']:
                    markets_dict['btts_no'] = outcome['price']