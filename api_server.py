from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
from src.agents.betting_agent import BettingAgent
from src.services.llm_service import LLMService
from src.models.bet_history import BetHistory
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Value Betting API")

# CORS para permitir requisições do React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos
class OpportunitiesRequest(BaseModel):
    bankroll: float

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict] = None

class BetRequest(BaseModel):
    match: str
    market: str
    odds: float
    stake: float
    phase: int

# Endpoints
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
            "count": len(opportunities)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics")
def get_statistics():
    """Retorna estatísticas"""
    try:
        agent = BettingAgent(100)  # Valor placeholder
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/phase")
def get_phase():
    """Retorna informações da fase atual"""
    try:
        agent = BettingAgent(100)  # Será atualizado com banca real
        phase_info = agent.bankroll_manager.get_phase_info()
        return phase_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def chat(request: ChatRequest):
    """Envia mensagem para o LLM"""
    try:
        llm = LLMService()
        response = llm.chat(request.message, request.context)
        return {"message": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/register-bet")
def register_bet(request: BetRequest):
    """Registra nova aposta"""
    try:
        agent = BettingAgent(100)
        bet_data = {
            'match': request.match,
            'market': request.market,
            'odds': request.odds,
            'stake': request.stake,
            'phase': request.phase
        }
        bet_id = agent.register_bet(bet_data)
        return {"bet_id": bet_id, "message": "Aposta registrada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)