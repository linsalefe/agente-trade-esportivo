import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class BetHistory:
    """Gerencia histórico de apostas e resultados"""
    
    def __init__(self, history_file: str = 'data/historical/bet_history.json'):
        self.history_file = history_file
        self.bets = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Carrega histórico do arquivo"""
        if not os.path.exists(self.history_file):
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_history(self):
        """Salva histórico no arquivo"""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.bets, f, indent=2, ensure_ascii=False)
    
    def add_bet(self, bet_data: Dict) -> str:
        """Adiciona nova aposta ao histórico"""
        bet_id = f"BET_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        bet = {
            'bet_id': bet_id,
            'timestamp': datetime.now().isoformat(),
            'match': bet_data['match'],
            'competition': bet_data['competition'],
            'market': bet_data['market'],
            'odds': bet_data['odds'],
            'stake': bet_data['stake'],
            'probability': bet_data['probability'],
            'ev': bet_data['ev'],
            'phase': bet_data.get('phase', 1),
            'status': 'pending',  # pending, won, lost, void
            'result': None,
            'profit': None,
            'closed_at': None
        }
        
        self.bets.append(bet)
        self._save_history()
        
        return bet_id
    
    def update_bet_result(self, bet_id: str, result: str):
        """Atualiza resultado da aposta (won/lost/void)"""
        for bet in self.bets:
            if bet['bet_id'] == bet_id:
                bet['status'] = result
                bet['closed_at'] = datetime.now().isoformat()
                
                if result == 'won':
                    bet['profit'] = round(bet['stake'] * (bet['odds'] - 1), 2)
                elif result == 'lost':
                    bet['profit'] = -bet['stake']
                else:  # void
                    bet['profit'] = 0
                
                self._save_history()
                return True
        
        return False
    
    def get_pending_bets(self) -> List[Dict]:
        """Retorna apostas pendentes"""
        return [bet for bet in self.bets if bet['status'] == 'pending']
    
    def get_statistics(self, phase: Optional[int] = None) -> Dict:
        """Calcula estatísticas do histórico"""
        if phase:
            bets = [b for b in self.bets if b.get('phase') == phase and b['status'] != 'pending']
        else:
            bets = [b for b in self.bets if b['status'] != 'pending']
        
        if not bets:
            return {
                'total_bets': 0,
                'won': 0,
                'lost': 0,
                'void': 0,
                'win_rate': 0,
                'total_staked': 0,
                'total_profit': 0,
                'roi': 0,
                'avg_odds': 0,
                'avg_stake': 0
            }
        
        won = [b for b in bets if b['status'] == 'won']
        lost = [b for b in bets if b['status'] == 'lost']
        void = [b for b in bets if b['status'] == 'void']
        
        total_staked = sum(b['stake'] for b in bets)
        total_profit = sum(b['profit'] for b in bets)
        
        return {
            'total_bets': len(bets),
            'won': len(won),
            'lost': len(lost),
            'void': len(void),
            'win_rate': round((len(won) / len(bets)) * 100, 2) if bets else 0,
            'total_staked': round(total_staked, 2),
            'total_profit': round(total_profit, 2),
            'roi': round((total_profit / total_staked) * 100, 2) if total_staked > 0 else 0,
            'avg_odds': round(sum(b['odds'] for b in bets) / len(bets), 2),
            'avg_stake': round(total_staked / len(bets), 2)
        }
    
    def get_recent_bets(self, n: int = 10) -> List[Dict]:
        """Retorna as N apostas mais recentes"""
        return sorted(self.bets, key=lambda x: x['timestamp'], reverse=True)[:n]