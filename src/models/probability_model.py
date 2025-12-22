import numpy as np
from typing import Dict, Tuple
from scipy.stats import poisson

class ProbabilityModel:
    """Calcula probabilidades para diferentes mercados usando Poisson"""
    
    def __init__(self):
        self.home_advantage = 1.15
    
    def calculate_over_under(self, home_avg: float, away_avg: float, line: float) -> Dict:
        """Calcula probabilidade de Over/Under X.5 gols"""
        home_expected = home_avg * self.home_advantage
        away_expected = away_avg
        
        total_expected = home_expected + away_expected
        
        # Probabilidade de over usando Poisson
        prob_under = sum([poisson.pmf(i, total_expected) for i in range(int(line) + 1)])
        prob_over = 1 - prob_under
        
        return {
            'prob_over': round(prob_over, 4),
            'prob_under': round(prob_under, 4),
            'expected_goals': round(total_expected, 2)
        }
    
    def calculate_btts(self, home_scored_avg: float, home_conceded_avg: float,
                       away_scored_avg: float, away_conceded_avg: float) -> float:
        """Calcula probabilidade de BTTS (ambas marcam)"""
        home_score_prob = 1 - poisson.pmf(0, home_scored_avg * self.home_advantage)
        away_score_prob = 1 - poisson.pmf(0, away_scored_avg)
        
        btts_prob = home_score_prob * away_score_prob
        
        return round(btts_prob, 4)
    
    def calculate_ev(self, model_probability: float, market_odds: float) -> float:
        """Calcula Expected Value (EV)"""
        implied_prob = 1 / market_odds
        ev = (model_probability * market_odds) - 1
        ev_percentage = ev * 100
        
        return round(ev_percentage, 2)
    
    def validate_opportunity(self, model_prob: float, odds: float, min_ev: float) -> Tuple[bool, float]:
        """Valida se oportunidade tem EV positivo suficiente"""
        ev = self.calculate_ev(model_prob, odds)
        
        if ev >= min_ev and model_prob > (1 / odds):
            return True, ev
        
        return False, ev