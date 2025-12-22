import requests
from typing import List, Dict
from config.config import Config
from src.cache.redis_client import RedisCache
from src.utils.api_retry import retry_on_rate_limit
from datetime import datetime

class OddsAPI:
    """Serviço para buscar odds com cache Redis"""
    
    def __init__(self):
        self.api_key = Config.ODDS_API_KEY
        self.base_url = Config.ODDS_API_BASE_URL
        self.cache = RedisCache()
    
    @retry_on_rate_limit(max_retries=3)
    def get_odds_for_match(self, sport: str = 'soccer_epl') -> List[Dict]:
        """Busca odds para jogos (cache: 15 minutos)"""
        cache_key = f"odds:{sport}:{datetime.now().strftime('%Y-%m-%d-%H')}"
        
        # Tenta cache
        cached = self.cache.get(cache_key)
        if cached:
            print(f"📦 Usando cache (odds {sport})")
            return cached
        
        url = f"{self.base_url}/sports/{sport}/odds"
        
        params = {
            'apiKey': self.api_key,
            'regions': 'us,uk,eu',
            'markets': 'h2h,totals,spreads',  # Adicionado spreads
            'oddsFormat': 'decimal'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        formatted = self._format_odds(response.json())
        
        # Salva no cache (15 minutos)
        self.cache.set(cache_key, formatted, expire_seconds=900)
        
        return formatted
    
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
                    elif market_key == 'h2h':
                        self._extract_h2h(market, game_data['markets'])
                    elif market_key == 'spreads':
                        self._extract_spreads(market, game_data['markets'])
            
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
    
    def _extract_h2h(self, market: Dict, markets_dict: Dict):
        """Extrai odds de 1X2"""
        for outcome in market.get('outcomes', []):
            name = outcome['name']
            if name == 'Draw':
                key = 'draw'
            else:
                continue
            
            if key not in markets_dict or outcome['price'] > markets_dict[key]:
                markets_dict[key] = outcome['price']
    
    def _extract_spreads(self, market: Dict, markets_dict: Dict):
        """Extrai odds de Spreads/Handicaps"""
        for outcome in market.get('outcomes', []):
            point = outcome.get('point')
            if point is None:
                continue
            
            # Normaliza a key (ex: spread_-1.5 ou spread_1.5)
            key = f'spread_{point}'
            
            # Pega a melhor odd disponível
            if key not in markets_dict or outcome['price'] > markets_dict[key]:
                markets_dict[key] = outcome['price']