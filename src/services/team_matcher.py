from difflib import SequenceMatcher
from typing import Optional, Dict, List


class TeamMatcher:
    """Serviço para fazer matching inteligente entre nomes de times de diferentes APIs"""
    
    # Mapeamento manual de abreviações conhecidas
    KNOWN_MAPPINGS = {
        # Premier League
        "man utd": "manchester united",
        "man united": "manchester united",
        "man city": "manchester city",
        "spurs": "tottenham",
        "tottenham hotspur": "tottenham",
        
        # La Liga
        "athletic bilbao": "athletic club",
        "athletic club": "athletic bilbao",
        
        # Serie A
        "ac milan": "milan",
        "inter milan": "inter",
        
        # Bundesliga
        "bayern munich": "bayern munchen",
        "bayern munchen": "bayern munich",
        
        # Portugal
        "sporting lisbon": "sporting cp",
        "sporting cp": "sporting lisbon",
        "sporting clube de portugal": "sporting cp",
        
        # Brasil
        "sao paulo": "são paulo",
        "atletico mineiro": "atlético mineiro",
        "atletico paranaense": "athletico paranaense",
    }
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """Normaliza nome do time para matching"""
        name = name.lower().strip()
        
        # Remove palavras comuns
        remove_words = ['fc', 'cf', 'sc', 'afc', 'bfc', 'united', 'city']
        for word in remove_words:
            name = name.replace(f' {word}', '').replace(f'{word} ', '')
        
        # Remove caracteres especiais
        name = name.replace('.', '').replace('-', ' ')
        
        # Remove espaços extras
        name = ' '.join(name.split())
        
        return name
    
    @staticmethod
    def similarity_score(name1: str, name2: str) -> float:
        """Calcula score de similaridade entre dois nomes (0-1)"""
        # Normaliza ambos
        norm1 = TeamMatcher.normalize_name(name1)
        norm2 = TeamMatcher.normalize_name(name2)
        
        # Checa mapeamento manual primeiro
        if norm1 in TeamMatcher.KNOWN_MAPPINGS:
            norm1 = TeamMatcher.KNOWN_MAPPINGS[norm1]
        if norm2 in TeamMatcher.KNOWN_MAPPINGS:
            norm2 = TeamMatcher.KNOWN_MAPPINGS[norm2]
        
        # Se forem iguais após normalização, match perfeito
        if norm1 == norm2:
            return 1.0
        
        # Usa SequenceMatcher para calcular similaridade
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    @staticmethod
    def find_best_match(team_name: str, candidates: List[Dict], threshold: float = 0.7) -> Optional[Dict]:
        """
        Encontra o melhor match para um time em uma lista de candidatos
        
        Args:
            team_name: Nome do time para buscar
            candidates: Lista de dicts com 'name' e outros dados do time
            threshold: Score mínimo para considerar um match (0-1)
        
        Returns:
            Dict com dados do time matched, ou None se não houver match bom
        """
        best_score = 0.0
        best_match = None
        
        for candidate in candidates:
            candidate_name = candidate.get('name', '')
            score = TeamMatcher.similarity_score(team_name, candidate_name)
            
            if score > best_score:
                best_score = score
                best_match = candidate
        
        # Só retorna se passou do threshold
        if best_score >= threshold:
            return best_match
        
        return None
    
    @staticmethod
    def match_teams(odds_home: str, odds_away: str, 
                   api_football_matches: List[Dict], 
                   threshold: float = 0.7) -> Optional[Dict]:
        """
        Tenta fazer match de um jogo da The Odds API com um jogo da API-Football
        
        Args:
            odds_home: Nome do time mandante (The Odds API)
            odds_away: Nome do time visitante (The Odds API)
            api_football_matches: Lista de jogos da API-Football
            threshold: Score mínimo para considerar um match
        
        Returns:
            Dict com dados do jogo da API-Football, ou None se não houver match
        """
        for match in api_football_matches:
            home_name = match.get('home_team', '')
            away_name = match.get('away_team', '')
            
            # Calcula score para ambos os times
            home_score = TeamMatcher.similarity_score(odds_home, home_name)
            away_score = TeamMatcher.similarity_score(odds_away, away_name)
            
            # Considera match se AMBOS os times têm score bom
            if home_score >= threshold and away_score >= threshold:
                # Score combinado (média)
                combined_score = (home_score + away_score) / 2
                
                return {
                    **match,
                    'match_score': combined_score,
                    'home_match_score': home_score,
                    'away_match_score': away_score
                }
        
        return None