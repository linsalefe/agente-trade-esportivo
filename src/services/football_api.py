import requests
from datetime import datetime, timedelta
from typing import List, Dict
from config.config import Config

class FootballAPI:
    """Serviço para buscar dados de jogos"""
    
    def __init__(self):
        self.api_key = Config.FOOTBALL_API_KEY
        self.base_url = Config.FOOTBALL_API_BASE_URL
        self.headers = {'X-Auth-Token': self.api_key}
    
    def get_today_matches(self) -> List[Dict]:
        """Busca jogos de hoje"""
        if not self.api_key or self.api_key == 'your_api_key_here':
            return []
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        url = f"{self.base_url}/matches"
        params = {'dateFrom': today, 'dateTo': today}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            matches = response.json().get('matches', [])
            return self._format_matches(matches)
        
        except Exception as e:
            print(f"Erro ao buscar jogos: {e}")
            return []
    
    def _format_matches(self, matches: List[Dict]) -> List[Dict]:
        """Formata dados dos jogos"""
        formatted = []
        
        for match in matches:
            formatted.append({
                'match_id': match['id'],
                'home_team': match['homeTeam']['name'],
                'away_team': match['awayTeam']['name'],
                'competition': match['competition']['name'],
                'date': match['utcDate'],
                'status': match['status']
            })
        
        return formatted
    
    def get_team_stats(self, team_id: int, last_n_games: int = 5) -> Dict:
        """Busca estatísticas recentes do time"""
        url = f"{self.base_url}/teams/{team_id}/matches"
        params = {'limit': last_n_games}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            matches = response.json().get('matches', [])
            return self._calculate_team_stats(matches, team_id)
        
        except Exception as e:
            print(f"Erro ao buscar stats do time: {e}")
            return {}
    
    def _calculate_team_stats(self, matches: List[Dict], team_id: int) -> Dict:
        """Calcula médias de gols"""
        scored = []
        conceded = []
        
        for match in matches:
            if match['status'] != 'FINISHED':
                continue
            
            is_home = match['homeTeam']['id'] == team_id
            
            if is_home:
                scored.append(match['score']['fullTime']['home'])
                conceded.append(match['score']['fullTime']['away'])
            else:
                scored.append(match['score']['fullTime']['away'])
                conceded.append(match['score']['fullTime']['home'])
        
        return {
            'avg_scored': round(sum(scored) / len(scored), 2) if scored else 0,
            'avg_conceded': round(sum(conceded) / len(conceded), 2) if conceded else 0,
            'games_analyzed': len(scored)
        }