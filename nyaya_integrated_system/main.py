"""
Nyaya Integrated Production System
End-to-End Legal AI Platform with Sovereign Enforcement
"""
import os
import sys
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Literal
import uvicorn
import uuid

# Local imports
from core.legal_engine import LegalDecisionEngine
from core.enforcement_engine import SovereignEnforcementEngine
from core.api_orchestrator import APIOrchestrator
from core.rl_engine import RLFeedbackEngine
from schemas.api_contracts import *

# Initialize core components
legal_engine = LegalDecisionEngine()
enforcement_engine = SovereignEnforcementEngine()
api_orchestrator = APIOrchestrator(legal_engine, enforcement_engine)
rl_engine = RLFeedbackEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize system components on startup"""
    await legal_engine.initialize()
    await enforcement_engine.initialize()
    await rl_engine.initialize()
    yield
    await legal_engine.shutdown()
    await enforcement_engine.shutdown()
    await rl_engine.shutdown()

# FastAPI app
app = FastAPI(
    title="Nyaya Legal AI - Production System",
    description="Integrated Legal Decision Engine with Sovereign Enforcement",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    # Add trace ID
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response

# Main API endpoints
@app.post("/api/legal/query", response_model=LegalQueryResponse)
async def legal_query(
    request: LegalQueryRequest,
    trace_id: str = Depends(lambda req: req.state.trace_id),
    background_tasks: BackgroundTasks = None
):
    """Execute legal query with sovereign enforcement"""
    return await api_orchestrator.process_legal_query(request, trace_id, background_tasks)

@app.post("/api/legal/multi-jurisdiction", response_model=MultiJurisdictionResponse)
async def multi_jurisdiction_query(
    request: MultiJurisdictionRequest,
    trace_id: str = Depends(lambda req: req.state.trace_id),
    background_tasks: BackgroundTasks = None
):
    """Execute multi-jurisdiction legal analysis"""
    return await api_orchestrator.process_multi_jurisdiction(request, trace_id, background_tasks)

@app.post("/api/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    trace_id: str = Depends(lambda req: req.state.trace_id),
    background_tasks: BackgroundTasks = None
):
    """Submit RL feedback with enforcement validation"""
    return await api_orchestrator.process_feedback(request, trace_id, background_tasks)

@app.get("/api/trace/{trace_id}", response_model=TraceResponse)
async def get_trace(trace_id: str):
    """Get complete audit trail"""
    return await api_orchestrator.get_trace(trace_id)

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "legal_engine": await legal_engine.health_check(),
            "enforcement_engine": await enforcement_engine.health_check(),
            "rl_engine": await rl_engine.health_check()
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )