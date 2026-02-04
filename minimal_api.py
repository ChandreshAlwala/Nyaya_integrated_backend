"""
Minimal Working Nyaya API - No Dependencies
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import uvicorn
import os

app = FastAPI(title="Nyaya Legal API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LegalQueryRequest(BaseModel):
    query: str
    jurisdiction_hint: Optional[str] = None
    domain_hint: Optional[str] = None

class FeedbackRequest(BaseModel):
    trace_id: str
    rating: int
    feedback_type: str
    comment: Optional[str] = None

@app.get("/")
def root():
    return {
        "service": "Nyaya Legal API",
        "status": "working",
        "endpoints": ["/api/legal/query", "/api/feedback", "/health"]
    }

@app.post("/api/legal/query")
def legal_query(request: LegalQueryRequest):
    trace_id = str(uuid.uuid4())
    
    return {
        "trace_id": trace_id,
        "domain": request.domain_hint or "CIVIL",
        "jurisdiction": request.jurisdiction_hint or "IN",
        "confidence": 0.8,
        "legal_route": [
            {
                "step": "CONSULTATION",
                "description": "Initial legal consultation",
                "timeline": "1-2 weeks"
            },
            {
                "step": "DOCUMENTATION",
                "description": "Prepare legal documents", 
                "timeline": "2-4 weeks"
            },
            {
                "step": "FILING",
                "description": "File case in court",
                "timeline": "1 week"
            }
        ],
        "enforcement_metadata": {
            "rule_id": "ALLOW_001",
            "decision": "ALLOW",
            "reasoning": "Query processed successfully"
        },
        "message": "Legal query processed successfully"
    }

@app.post("/api/feedback")
def submit_feedback(request: FeedbackRequest):
    return {
        "status": "recorded",
        "trace_id": request.trace_id,
        "message": "Feedback recorded successfully"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "message": "API is working"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)