"""
Nyaya Integrated Backend - True Integration
Uses actual code from Chandresh, Raj, and Nilesh repositories
"""
import sys
import os
from pathlib import Path

# Add all repository paths
current_dir = Path(__file__).parent
base_dir = current_dir.parent

# Add paths for all repositories
sys.path.insert(0, str(base_dir / "Nyaya_AI"))
sys.path.insert(0, str(base_dir / "AI_ASSISTANT_PhaseB_Integration"))
sys.path.insert(0, str(base_dir / "nyaya-legal-procedure-datasets"))

from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
from datetime import datetime

# Import Chandresh's enforcement engine
from enforcement_engine.engine import SovereignEnforcementEngine, EnforcementSignal
from sovereign_agents.legal_agent import LegalAgent
from sovereign_agents.jurisdiction_router_agent import JurisdictionRouterAgent
from rl_engine.feedback_api import FeedbackAPI

# Import Nilesh's orchestrator
from app.core.assistant_orchestrator import handle_assistant_request

# Pydantic models
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class JurisdictionEnum(str, Enum):
    INDIA = "IN"
    UAE = "UAE" 
    UK = "UK"

class LegalQueryRequest(BaseModel):
    query: str
    jurisdiction_hint: Optional[JurisdictionEnum] = None
    domain_hint: Optional[str] = None

class LegalQueryResponse(BaseModel):
    trace_id: str
    domain: str
    jurisdiction: str
    confidence: float
    legal_route: List[Dict[str, Any]]
    enforcement_metadata: Dict[str, Any]

class FeedbackRequest(BaseModel):
    trace_id: str
    rating: int = Field(ge=1, le=5)
    feedback_type: str
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    status: str
    trace_id: str
    message: str

# Initialize components using actual implementations
app = FastAPI(
    title="Nyaya Integrated Legal AI",
    description="Production system using Chandresh, Raj & Nilesh implementations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Chandresh's components
enforcement_engine = SovereignEnforcementEngine()
jurisdiction_router_agent = JurisdictionRouterAgent()
feedback_api = FeedbackAPI()

# Initialize legal agents for each jurisdiction
legal_agents = {
    "IN": LegalAgent(agent_id="india_legal_agent", jurisdiction="India"),
    "UK": LegalAgent(agent_id="uk_legal_agent", jurisdiction="UK"), 
    "UAE": LegalAgent(agent_id="uae_legal_agent", jurisdiction="UAE")
}

@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response

@app.post("/api/legal/query", response_model=LegalQueryResponse)
async def legal_query(
    request: LegalQueryRequest,
    trace_id: str = Depends(lambda req: req.state.trace_id)
):
    """Process legal query using integrated backend"""
    
    # Step 1: Create enforcement signal using Chandresh's implementation
    signal = EnforcementSignal(
        case_id=trace_id,
        country=request.jurisdiction_hint.value if request.jurisdiction_hint else "IN",
        domain="legal_query",
        procedure_id="legal_query_processing",
        original_confidence=0.5,
        user_request=request.query,
        jurisdiction_routed_to=request.jurisdiction_hint.value if request.jurisdiction_hint else "IN",
        trace_id=trace_id
    )
    
    # Step 2: Check enforcement permission
    enforcement_result = enforcement_engine.make_enforcement_decision(signal)
    
    if enforcement_result.decision.value == "BLOCK":
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Request blocked by enforcement engine",
                "rule_id": enforcement_result.rule_id,
                "reasoning": enforcement_result.reasoning_summary
            }
        )
    
    # Step 3: Route to jurisdiction using Chandresh's router
    routing_result = await jurisdiction_router_agent.process({
        "query": request.query,
        "jurisdiction_hint": request.jurisdiction_hint.value if request.jurisdiction_hint else None,
        "domain_hint": request.domain_hint
    })
    
    target_jurisdiction = routing_result["target_jurisdiction"]
    
    # Step 4: Process with legal agent
    if target_jurisdiction in legal_agents:
        legal_agent = legal_agents[target_jurisdiction]
        legal_result = await legal_agent.process({
            "query": request.query,
            "trace_id": trace_id
        })
    else:
        legal_result = {
            "domain": request.domain_hint or "CIVIL",
            "confidence": 0.7,
            "legal_route": [{"step": "CONSULTATION", "description": "Legal consultation required"}]
        }
    
    # Step 5: Build response with enforcement metadata
    return LegalQueryResponse(
        trace_id=trace_id,
        domain=legal_result.get("domain", "CIVIL"),
        jurisdiction=target_jurisdiction,
        confidence=legal_result.get("confidence", 0.7),
        legal_route=legal_result.get("legal_route", []),
        enforcement_metadata={
            "rule_id": enforcement_result.rule_id,
            "decision": enforcement_result.decision.value,
            "signed_proof": enforcement_result.signed_decision_object,
            "reasoning": enforcement_result.reasoning_summary
        }
    )

@app.post("/api/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    trace_id: str = Depends(lambda req: req.state.trace_id)
):
    """Submit feedback using Chandresh's RL engine"""
    
    # Use Chandresh's feedback API
    feedback_result = feedback_api.receive_feedback({
        "trace_id": request.trace_id,
        "score": request.rating,
        "nonce": trace_id,
        "comment": request.comment
    })
    
    return FeedbackResponse(
        status="recorded",
        trace_id=request.trace_id,
        message="Feedback processed successfully"
    )

@app.post("/api/assistant", response_model=Dict[str, Any])
async def assistant_endpoint(
    request: Dict[str, Any],
    trace_id: str = Depends(lambda req: req.state.trace_id)
):
    """Use Nilesh's assistant orchestrator"""
    
    # Convert to Nilesh's expected format
    assistant_request = {
        "version": "3.0.0",
        "input": {
            "message": request.get("message", ""),
            "summarized_payload": request.get("payload", {})
        },
        "context": {
            "platform": "web",
            "device": "desktop",
            "session_id": trace_id
        }
    }
    
    # Use Nilesh's handler
    result = await handle_assistant_request(assistant_request)
    return result

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "enforcement_engine": "active",
            "legal_agents": len(legal_agents),
            "feedback_api": "active"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "integrated_main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )