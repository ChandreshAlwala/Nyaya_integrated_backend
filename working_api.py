from fastapi import FastAPI

app = FastAPI()

@app.post("/api/legal/query")
def legal_query(request: dict):
    return {
        "trace_id": "12345",
        "domain": "CIVIL",
        "jurisdiction": "IN",
        "confidence": 0.8,
        "legal_route": [{"step": "CONSULTATION"}],
        "message": "Success"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)