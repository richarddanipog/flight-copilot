from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List
from src.llm.agent import LLMAgent
from src.utils.logger import get_logger
from src.config import get_settings

router = APIRouter()
log = get_logger()
settings = get_settings()


class AgentRequest(BaseModel):
    query: str


class AgentResponse(BaseModel):
    options: List[Dict[str, Any]]
    output: str  # natural-language reasoning/summary


agent = LLMAgent()


@router.post("/agent", response_model=AgentResponse)
def agent_query(body: AgentRequest) -> AgentResponse:
    try:
        options, output = agent.execute(agent=body.query)
        return AgentResponse(options=options, output=output)
    except ValueError as ve:
        # e.g., date guard past date
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        log.error("Agent failed: %s", e)
        raise HTTPException(status_code=500, detail="Agent failed")
