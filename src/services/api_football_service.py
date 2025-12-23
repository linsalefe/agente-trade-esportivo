import requests
from datetime import datetime, timedelta
from typing import List, Dict
from config.config import Config
from src.cache.redis_client import RedisCache
from src.utils.api_retry import retry_on_rate_limit

class APIFootballService:
    """Serviço para API-Football (api-sports.io) - mais jogos"""
    
    def __init__(self):
        self.api_key = Config.API_FOOTBALL_KEY
        self.base_url = Config.API_FOOTBALL_BASE_URL
        self.headers = {
            'x-apisports-key': self.api_key
        }
        self.cache = RedisCache()
    
    @retry_on_rate_limit(max_retries=3)
    def get_fixtures_by_date(self, date: str) -> List[Dict]:
        """
        Busca jogos por data (formato: YYYY-MM-DD)
        Cache: 6 horas
        """
        cache_key = f"api_football:fixtures:{date}"
        
        # Tenta cache
        cached = self.cache.get(cache_key)
        if cached:
            print(f"📦 Usando cache (API-Football {date})")
            return cached
        
        if not self.api_key:
            return []
        
        url = f"{self.base_url}/fixtures"
        params = {'date': date}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            fixtures = data.get('response', [])
            
            formatted = self._format_fixtures(fixtures)
            
            # Salva no cache (6 horas)
            self.cache.set(cache_key, formatted, expire_seconds=21600)
            
            return formatted
            
        except Exception as e:
            print(f"⚠️ Erro ao buscar API-Football: {e}")
            return []
    
    def get_fixtures_next_days(self, days: int = 3) -> List[Dict]:
        """Busca jogos dos próximos N dias"""
        all_fixtures = []
        
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            fixtures = self.get_fixtures_by_date(date)
            all_fixtures.extend(fixtures)
        
        return all_fixtures
    
    def _format_fixtures(self, fixtures: List[Dict]) -> List[Dict]:
        """Formata jogos para padrão unificado"""
        formatted = []
        
        for fixture in fixtures:
            try:
                # Filtra apenas jogos agendados ou em andamento
                status = fixture['fixture']['status']['short']
                if status not in ['NS', 'TBD', '1H', '2H', 'HT', 'LIVE']:
                    continue
                
                formatted.append({
                    'match_id': f"apif_{fixture['fixture']['id']}",
                    'home_team': fixture['teams']['home']['name'],
                    'away_team': fixture['teams']['away']['name'],
                    'competition': fixture['league']['name'],
                    'date': fixture['fixture']['date'],
                    'status': 'SCHEDULED',
                    'source': 'api-football'
                })
            except Exception as e:
                continue
        
        return formatted
    
    @retry_on_rate_limit(max_retries=3)
    def get_team_statistics(self, team_id: int, league_id: int, season: int) -> Dict:
        """
        Busca estatísticas de um time
        Cache: 24 horas
        """
        cache_key = f"api_football:team_stats:{team_id}:{league_id}:{season}"
        
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        if not self.api_key:
            return {}
        
        url = f"{self.base_url}/teams/statistics"
        params = {
            'team': team_id,
            'league': league_id,
            'season': season
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            stats = self._extract_team_stats(data.get('response', {}))
            
            # Salva no cache (24 horas)
            self.cache.set(cache_key, stats, expire_seconds=86400)
            
            return stats
            
        except Exception as e:
            print(f"⚠️ Erro ao buscar stats do time: {e}")
            return {}
    
    def _extract_team_stats(self, data: Dict) -> Dict:
        """Extrai médias de gols"""
        try:
            goals_for = data.get('goals', {}).get('for', {})
            goals_against = data.get('goals', {}).get('against', {})
            
            return {
                'avg_scored': goals_for.get('average', {}).get('total', 1.5),
                'avg_conceded': goals_against.get('average', {}).get('total', 1.5),
                'source': 'api-football'
            }
        except:
            return {
                'avg_scored': 1.5,
                'avg_conceded': 1.5,
                'source': 'api-football'
            }