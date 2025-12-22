from src.agents.betting_agent import BettingAgent
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    print("=" * 60)
    print("🤖 AGENTE DE VALUE BETTING - INICIANDO")
    print("=" * 60)
    
    # Inicia com banca de R$ 100
    agent = BettingAgent(current_bankroll=100)
    
    # Mostra fase atual
    print(agent.get_phase_summary())
    
    # Busca oportunidades
    print("\n🔍 Analisando oportunidades do dia...\n")
    opportunities = agent.analyze_today_opportunities()
    
    if not opportunities:
        print("❌ Nenhuma oportunidade encontrada hoje.")
        return
    
    # Mostra sugestões
    print(f"\n📊 {len(opportunities)} OPORTUNIDADES ENCONTRADAS:\n")
    
    for i, opp in enumerate(opportunities[:5], 1):  # Mostra top 5
        print(f"{i}. {opp['match']}")
        print(f"   Mercado: {opp['market']} | Odd: {opp['odds']}")
        print(f"   Probabilidade: {opp['probability']*100:.1f}% | EV: +{opp['ev']}%")
        print(f"   💰 Stake sugerido: R$ {opp['stake']:.2f}")
        print(f"   🎯 Retorno potencial: R$ {opp['potential_return']:.2f}\n")
    
    print("=" * 60)

if __name__ == "__main__":
    main()