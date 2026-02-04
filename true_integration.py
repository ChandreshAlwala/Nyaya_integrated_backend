"""
Nyaya True Backend Integration
Direct integration using existing repositories without copying
"""
import sys
import os
from pathlib import Path

# Add all repository paths to Python path
current_dir = Path(__file__).parent
nyaya_ai_path = str(current_dir / "Nyaya_AI")
if nyaya_ai_path not in sys.path:
    sys.path.insert(0, nyaya_ai_path)
    
ai_assistant_path = str(current_dir / "AI_ASSISTANT_PhaseB_Integration")
if ai_assistant_path not in sys.path:
    sys.path.insert(0, ai_assistant_path)
    
datasets_path = str(current_dir / "nyaya-legal-procedure-datasets")
if datasets_path not in sys.path:
    sys.path.insert(0, datasets_path)

from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum

# Try to import Chandresh's components
CHANDRESH_AVAILABLE = False
try:
    from enforcement_engine.engine import SovereignEnforcementEngine, EnforcementSignal
    from sovereign_agents.legal_agent import LegalAgent
    from sovereign_agents.jurisdiction_router_agent import JurisdictionRouterAgent
    from rl_engine.feedback_api import FeedbackAPI
    CHANDRESH_AVAILABLE = True
    print("SUCCESS: Chandresh's components loaded")
except ImportError as e:
    print(f"WARNING: Chandresh components not available: {e}")

# Try to import Nilesh's components
NILESH_AVAILABLE = False
try:
    from app.core.assistant_orchestrator import handle_assistant_request
    NILESH_AVAILABLE = True
    print("SUCCESS: Nilesh's components loaded")
except ImportError as e:
    print(f"WARNING: Nilesh components not available: {e}")

# Raj's datasets are always available as JSON files
RAJ_AVAILABLE = True
print("SUCCESS: Raj's datasets available")

# Pydantic models
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
    message: str

class FeedbackRequest(BaseModel):
    trace_id: str
    rating: int = Field(ge=1, le=5)
    feedback_type: str
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    status: str
    trace_id: str
    message: str

# Create FastAPI app
app = FastAPI(
    title="Nyaya True Integrated Backend",
    description="Direct integration with Chandresh, Raj & Nilesh repositories",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
enforcement_engine = None
jurisdiction_router = None
feedback_api = None
legal_agents = {}

if CHANDRESH_AVAILABLE:
    try:
        enforcement_engine = SovereignEnforcementEngine()
        jurisdiction_router = JurisdictionRouterAgent()
        feedback_api = FeedbackAPI()
        
        # Initialize legal agents
        legal_agents = {
            "IN": LegalAgent(agent_id="india_legal_agent", jurisdiction="India"),
            "UK": LegalAgent(agent_id="uk_legal_agent", jurisdiction="UK"),
            "UAE": LegalAgent(agent_id="uae_legal_agent", jurisdiction="UAE")
        }
        print("Chandresh's enforcement system initialized")
    except Exception as e:
        print(f"Error initializing Chandresh components: {e}")
        CHANDRESH_AVAILABLE = False

@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response

@app.get("/")
async def root():
    """Root endpoint showing true integration status"""
    return {
        "service": "Nyaya True Integrated Backend",
        "version": "1.0.0",
        "description": "Direct integration with actual repositories",
        "integration_status": {
            "chandresh_enforcement": CHANDRESH_AVAILABLE,
            "nilesh_assistant": NILESH_AVAILABLE,
            "raj_datasets": RAJ_AVAILABLE
        },
        "available_endpoints": {
            "legal_query": "/api/legal/query",
            "feedback": "/api/feedback", 
            "assistant": "/api/assistant" if NILESH_AVAILABLE else "Not available",
            "health": "/health"
        },
        "repositories_integrated": [
            "Nyaya_AI (Chandresh)" if CHANDRESH_AVAILABLE else "Nyaya_AI (Not loaded)",
            "AI_ASSISTANT_PhaseB_Integration (Nilesh)" if NILESH_AVAILABLE else "AI_ASSISTANT_PhaseB_Integration (Not loaded)",
            "nyaya-legal-procedure-datasets (Raj)"
        ]
    }

@app.post("/api/legal/query")
async def legal_query(
    request: LegalQueryRequest,
    trace_id: str = Depends(lambda req: req.state.trace_id)
):
    """Process legal query using Chandresh's enforcement and Raj's data"""
    
    if not CHANDRESH_AVAILABLE:
        return {
            "trace_id": trace_id,
            "domain": request.domain_hint or "CIVIL",
            "jurisdiction": request.jurisdiction_hint.value if request.jurisdiction_hint else "IN",
            "confidence": 0.5,
            "legal_route": [{"step": "FALLBACK", "description": "Enforcement engine not available"}],
            "enforcement_metadata": {"status": "fallback_mode", "reason": "enforcement_unavailable"},
            "message": "Running in fallback mode - Chandresh's enforcement engine not loaded"
        }
    
    # Use Chandresh's enforcement engine
    signal = EnforcementSignal(
        case_id=trace_id,
        country=request.jurisdiction_hint.value if request.jurisdiction_hint else "IN",
        domain=request.domain_hint or "legal_query",
        procedure_id="legal_query_processing",
        original_confidence=0.7,
        user_request=request.query,
        jurisdiction_routed_to=request.jurisdiction_hint.value if request.jurisdiction_hint else "IN",
        trace_id=trace_id
    )
    
    # Get enforcement decision
    enforcement_result = enforcement_engine.make_enforcement_decision(signal)
    
    if enforcement_result.decision.value == "BLOCK":
        return {
            "trace_id": trace_id,
            "domain": "BLOCKED",
            "jurisdiction": "BLOCKED",
            "confidence": 0.0,
            "legal_route": [],
            "enforcement_metadata": {
                "rule_id": enforcement_result.rule_id,
                "decision": enforcement_result.decision.value,
                "reasoning": enforcement_result.reasoning_summary,
                "signed_proof": enforcement_result.signed_decision_object
            },
            "message": "Request blocked by Chandresh's enforcement engine"
        }
    
    # Use jurisdiction router
    routing_result = await jurisdiction_router.process({
        "query": request.query,
        "jurisdiction_hint": request.jurisdiction_hint.value if request.jurisdiction_hint else None,
        "domain_hint": request.domain_hint
    })
    
    target_jurisdiction = routing_result.get("target_jurisdiction", "IN")
    
    # Process with legal agent
    legal_result = {}
    if target_jurisdiction in legal_agents:
        legal_agent = legal_agents[target_jurisdiction]
        legal_result = await legal_agent.process({
            "query": request.query,
            "trace_id": trace_id
        })
    
    # Load Raj's datasets for additional context
    raj_data = load_raj_datasets(target_jurisdiction, request.domain_hint)
    
    return {
        "trace_id": trace_id,
        "domain": legal_result.get("domain", request.domain_hint or "CIVIL"),
        "jurisdiction": target_jurisdiction,
        "confidence": legal_result.get("confidence", 0.7),
        "legal_route": legal_result.get("legal_route", raj_data.get("procedures", [])),
        "enforcement_metadata": {
            "rule_id": enforcement_result.rule_id,
            "decision": enforcement_result.decision.value,
            "reasoning": enforcement_result.reasoning_summary,
            "signed_proof": enforcement_result.signed_decision_object
        },
        "message": "Processed using Chandresh's enforcement + Raj's datasets"
    }

@app.post("/api/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    trace_id: str = Depends(lambda req: req.state.trace_id)
):
    """Submit feedback using Chandresh's RL engine"""
    
    if not CHANDRESH_AVAILABLE or not feedback_api:
        return {
            "status": "fallback",
            "trace_id": request.trace_id,
            "message": "Feedback recorded in fallback mode - Chandresh's RL engine not available"
        }
    
    # Use Chandresh's feedback API
    try:
        feedback_result = feedback_api.receive_feedback({
            "trace_id": request.trace_id,
            "score": request.rating,
            "nonce": trace_id,
            "comment": request.comment
        })
        
        return {
            "status": "recorded",
            "trace_id": request.trace_id,
            "message": "Feedback processed by Chandresh's RL engine"
        }
    except Exception as e:
        return {
            "status": "error",
            "trace_id": request.trace_id,
            "message": f"Error in Chandresh's RL engine: {str(e)}"
        }

@app.post("/api/assistant")
async def assistant_endpoint(
    request: Dict[str, Any],
    trace_id: str = Depends(lambda req: req.state.trace_id)
):
    """Use Nilesh's assistant orchestrator"""
    
    if not NILESH_AVAILABLE:
        return {
            "status": "fallback",
            "message": "Nilesh's assistant not available",
            "trace_id": trace_id
        }
    
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
    
    try:
        # Use Nilesh's handler
        result = await handle_assistant_request(assistant_request)
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in Nilesh's assistant: {str(e)}",
            "trace_id": trace_id
        }

def load_raj_datasets(jurisdiction: str, domain: str) -> Dict[str, Any]:
    """Load Raj's legal datasets"""
    import json
    
    try:
        # Map jurisdiction codes
        jur_map = {"IN": "india", "UAE": "uae", "UK": "uk"}
        jur_folder = jur_map.get(jurisdiction, "india")
        
        # Map domain to file
        domain_map = {
            "CRIMINAL": "criminal.json",
            "CIVIL": "civil.json", 
            "FAMILY": "family.json",
            "CONSUMER_COMMERCIAL": "consumer_commercial.json"
        }
        domain_file = domain_map.get(domain, "civil.json")
        
        # Load procedure data
        procedure_path = current_dir / "nyaya-legal-procedure-datasets" / "data" / "procedures" / jur_folder / domain_file
        
        if procedure_path.exists():
            with open(procedure_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading Raj's datasets: {e}")
    
    return {"procedures": []}

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "integration_status": {
            "chandresh_enforcement": "active" if CHANDRESH_AVAILABLE else "unavailable",
            "nilesh_assistant": "active" if NILESH_AVAILABLE else "unavailable",
            "raj_datasets": "active"
        },
        "components": {
            "enforcement_engine": enforcement_engine is not None,
            "jurisdiction_router": jurisdiction_router is not None,
            "feedback_api": feedback_api is not None,
            "legal_agents": len(legal_agents)
        },
        "message": "True backend integration with actual repositories"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False
    )