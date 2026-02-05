from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI()

class LegalQuery(BaseModel):
    query: str
    jurisdiction_hint: Optional[str] = None
    domain_hint: Optional[str] = None

@app.post("/api/legal/query")
def query_legal(request: LegalQuery):
    return {
        "trace_id": str(uuid.uuid4()),
        "domain": "CIVIL",
        "jurisdiction": "IN", 
        "confidence": 0.8,
        "legal_route": [{"step": "CONSULTATION", "description": "Legal consultation"}],
        "message": "Success"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)