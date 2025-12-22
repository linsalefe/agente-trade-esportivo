from openai import OpenAI
import os
import json
from typing import Dict, List, Optional

class LLMService:
    """Serviço para interação com LLM (OpenAI)"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o-mini"  # Barato e eficiente
        
        self.system_prompt = """Você é um assistente especializado em apostas esportivas e value betting.

Seu papel:
- Ajudar usuários a entender oportunidades de apostas
- Explicar conceitos como EV (Expected Value), odds, probabilidades
- Analisar múltiplas e apostas simples
- Dar contexto sobre gestão de banca e controle de risco
- Sempre ser objetivo e matemático, nunca prometer lucro garantido

Conceitos importantes:
- EV (Expected Value): Lucro esperado no longo prazo. EV positivo = boa aposta matematicamente
- Value Bet: Quando as odds do mercado são maiores que a probabilidade real (edge)
- Kelly Criterion: Método matemático para calcular stake ótimo
- Gestão de Banca: Sistema de fases com stakes que diminuem conforme banca cresce
- Múltiplas: Combinação de apostas. Maior risco, maior retorno potencial

Fase 1-4: Alavancagem (stakes 15% → 4%)
Consolidação: Acima R$ 50k (stakes 1.5%)

Sempre seja direto, conciso e educativo. Nunca use emojis excessivamente."""

    def chat(self, user_message: str, context: Optional[Dict] = None) -> str:
        """Envia mensagem para o LLM com contexto opcional"""
        
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Adiciona contexto se fornecido
        if context:
            context_message = self._format_context(context)
            messages.append({"role": "system", "content": f"Contexto atual:\n{context_message}"})
        
        # Adiciona mensagem do usuário
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Erro ao processar: {str(e)}"
    
    def _format_context(self, context: Dict) -> str:
        """Formata contexto para o LLM"""
        formatted = []
        
        # Informações da banca
        if 'bankroll' in context:
            formatted.append(f"Banca atual: R$ {context['bankroll']:.2f}")
        
        if 'phase' in context:
            formatted.append(f"Fase atual: {context['phase']}")
        
        # Oportunidades
        if 'opportunities' in context and context['opportunities']:
            formatted.append(f"\nOportunidades encontradas: {len(context['opportunities'])}")
            
            # Top 3 oportunidades
            for i, opp in enumerate(context['opportunities'][:3], 1):
                formatted.append(
                    f"{i}. {opp['match']} - {opp['market']} @ {opp['odds']} "
                    f"(EV: +{opp['ev']:.1f}%, Prob: {opp['probability']*100:.1f}%)"
                )
        
        # Múltiplas
        if 'multiples' in context and context['multiples']:
            formatted.append(f"\nMúltiplas detectadas: {len(context['multiples'])}")
            
            for i, mult in enumerate(context['multiples'][:2], 1):
                # Usa as chaves corretas retornadas pelo MultipleDetector
                legs = mult.get('legs', [])
                formatted.append(
                    f"{i}. Odd combinada: {mult['combined_odds']:.2f}x "
                    f"(EV: +{mult['ev']:.1f}%, {len(legs)} pernas)"
                )
        
        # Estatísticas
        if 'stats' in context:
            stats = context['stats']
            if stats.get('total_bets', 0) > 0:
                formatted.append(f"\nEstatísticas:")
                formatted.append(f"- Total apostas: {stats['total_bets']}")
                formatted.append(f"- Win rate: {stats['win_rate']:.1f}%")
                formatted.append(f"- ROI: {stats['roi']:.2f}%")
        
        return "\n".join(formatted)