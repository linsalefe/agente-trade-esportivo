from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

from src.agents.betting_agent import BettingAgent
from src.services.llm_service import LLMService
from src.models.bet_history import BetHistory

load_dotenv()

app = FastAPI(title="Value Betting API")


# =========================
# CORS
# =========================
# Dica: se você usa Vite, geralmente é 5173. Se é CRA, geralmente é 3000.
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Models
# =========================
class OpportunitiesRequest(BaseModel):
    bankroll: float


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class BetRequest(BaseModel):
    match: str
    market: str
    odds: float
    stake: float
    phase: int


# =========================
# Helpers
# =========================
def _needs_context(message: str) -> bool:
    """Heurística simples para decidir quando vale anexar contexto automático."""
    m = (message or "").lower()
    keywords = [
        "jogo", "jogos", "hoje", "amanhã",
        "oportunidade", "oportunidades",
        "aposta", "apostas",
        "odd", "odds",
        "múltipla", "multipla", "múltiplas", "multiplas",
        "value", "ev",
        "stake", "banca", "fase",
        "quais são", "me diga", "me mostra",
    ]
    return any(k in m for k in keywords)


def _build_context(bankroll: float = 100.0) -> Dict[str, Any]:
    """
    Monta um contexto rápido (phase + stats + oportunidades + múltiplas),
    pra o LLM responder com base em dados reais do sistema.
    """
    agent = BettingAgent(bankroll)

    # Phase
    phase_info = agent.bankroll_manager.get_phase_info()

    # Stats (usa bet_history)
    stats = agent.get_statistics()

    # Opportunities (usa APIs/cache)
    opportunities = agent.analyze_today_opportunities()
    multiples = agent.detect_multiples(opportunities)

    # Enxuga pra não mandar payload gigante pro LLM
    context = {
        "bankroll": float(phase_info.get("bankroll", bankroll)),
        "phase": phase_info.get("phase"),
        "opportunities": (opportunities or [])[:5],
        "multiples": (multiples or [])[:2],
        "stats": stats or {},
    }
    return context


# =========================
# Endpoints
# =========================
@app.get("/")
def read_root():
    return {"status": "online", "message": "Value Betting API"}


@app.post("/opportunities")
def get_opportunities(request: OpportunitiesRequest):
    """Retorna oportunidades do dia"""
    try:
        agent = BettingAgent(request.bankroll)
        opportunities = agent.analyze_today_opportunities()
        multiples = agent.detect_multiples(opportunities)

        return {
            "opportunities": opportunities,
            "multiples": multiples,
            "count": len(opportunities),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics")
def get_statistics():
    """Retorna estatísticas"""
    try:
        agent = BettingAgent(100)  # placeholder
        stats = agent.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
def get_history(limit: int = 10):
    """Retorna histórico de apostas"""
    try:
        bet_history = BetHistory()
        history = bet_history.get_recent_bets(limit)
        return history
    except Exception as e:
        import traceback
        print("ERRO NO HISTORY:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase")
def get_phase():
    """Retorna informações da fase atual"""
    try:
        agent = BettingAgent(100)  # placeholder
        phase_info = agent.bankroll_manager.get_phase_info()
        return phase_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
def chat(request: ChatRequest):
    """
    Chat com LLM.
    - Se o front/curl mandar context, usamos.
    - Se NÃO mandar e a pergunta exigir dados, a API monta contexto automaticamente.
    """
    try:
        llm = LLMService()

        # Se não veio contexto e a pergunta sugere que precisa, monta contexto automaticamente
        context = request.context
        if context is None and _needs_context(request.message):
            context = _build_context(bankroll=100.0)

        response = llm.chat(request.message, context)
        return {"message": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/register-bet")
def register_bet(request: BetRequest):
    """Registra nova aposta"""
    try:
        agent = BettingAgent(100)
        bet_data = {
            "match": request.match,
            "market": request.market,
            "odds": request.odds,
            "stake": request.stake,
            "phase": request.phase,
        }
        bet_id = agent.register_bet(bet_data)
        return {"bet_id": bet_id, "message": "Aposta registrada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
