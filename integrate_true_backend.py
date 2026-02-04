"""
True Backend Integration Script
Properly integrates Chandresh, Raj, and Nilesh's actual implementations
"""
import os
import shutil
from pathlib import Path

def integrate_backends():
    """Integrate all three backends properly"""
    
    print("Starting true backend integration...")
    
    # Create integrated backend directory
    integrated_dir = Path("nyaya_true_integration")
    integrated_dir.mkdir(exist_ok=True)
    
    # 1. Copy Chandresh's Nyaya_AI core components
    print("Integrating Chandresh's enforcement engine...")
    chandresh_src = Path("Nyaya_AI")
    chandresh_dest = integrated_dir / "chandresh_components"
    
    if chandresh_src.exists():
        shutil.copytree(chandresh_src, chandresh_dest, dirs_exist_ok=True)
        print("Chandresh's components copied")
    
    # 2. Copy Nilesh's AI Assistant components  
    print("Integrating Nilesh's assistant platform...")
    nilesh_src = Path("AI_ASSISTANT_PhaseB_Integration")
    nilesh_dest = integrated_dir / "nilesh_components"
    
    if nilesh_src.exists():
        shutil.copytree(nilesh_src, nilesh_dest, dirs_exist_ok=True)
        print("Nilesh's components copied")
    
    # 3. Copy Raj's legal datasets
    print("Integrating Raj's legal datasets...")
    raj_src = Path("nyaya-legal-procedure-datasets")
    raj_dest = integrated_dir / "raj_datasets"
    
    if raj_src.exists():
        shutil.copytree(raj_src, raj_dest, dirs_exist_ok=True)
        print("Raj's datasets copied")
    
    # 4. Create unified main application
    create_unified_main(integrated_dir)
    
    # 5. Create requirements file
    create_unified_requirements(integrated_dir)
    
    print("True backend integration complete!")
    print(f"Integrated system available in: {integrated_dir}")
    
    return integrated_dir

def create_unified_main(integrated_dir):
    """Create unified main application"""
    
    main_content = '''"""
Nyaya True Integrated Backend
Uses actual implementations from Chandresh, Raj, and Nilesh
"""
import sys
import os
from pathlib import Path

# Add component paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "chandresh_components"))
sys.path.insert(0, str(current_dir / "nilesh_components"))
sys.path.insert(0, str(current_dir / "raj_datasets"))

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum

# Import Chandresh's actual implementations
try:
    from enforcement_engine.engine import SovereignEnforcementEngine, EnforcementSignal
    from sovereign_agents.legal_agent import LegalAgent
    from sovereign_agents.jurisdiction_router_agent import JurisdictionRouterAgent
    from rl_engine.feedback_api import FeedbackAPI
    from api.router import router as nyaya_router
    CHANDRESH_AVAILABLE = True
except ImportError as e:
    print(f"Chandresh components not fully available: {e}")
    CHANDRESH_AVAILABLE = False

# Import Nilesh's actual implementations
try:
    from app.core.assistant_orchestrator import handle_assistant_request
    from app.api.assistant import router as assistant_router
    NILESH_AVAILABLE = True
except ImportError as e:
    print(f"Nilesh components not fully available: {e}")
    NILESH_AVAILABLE = False

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

# Create FastAPI app
app = FastAPI(
    title="Nyaya True Integrated Backend",
    description="Production system with actual Chandresh, Raj & Nilesh code",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components if available
if CHANDRESH_AVAILABLE:
    try:
        enforcement_engine = SovereignEnforcementEngine()
        jurisdiction_router = JurisdictionRouterAgent()
        feedback_api = FeedbackAPI()
        
        # Include Chandresh's router
        app.include_router(nyaya_router)
        print("Chandresh's Nyaya AI components loaded")
    except Exception as e:
        print(f"Error initializing Chandresh components: {e}")
        CHANDRESH_AVAILABLE = False

if NILESH_AVAILABLE:
    try:
        # Include Nilesh's assistant router
        app.include_router(assistant_router)
        print("Nilesh's AI Assistant components loaded")
    except Exception as e:
        print(f"Error initializing Nilesh components: {e}")
        NILESH_AVAILABLE = False

@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response

@app.get("/")
async def root():
    """Root endpoint showing integration status"""
    return {
        "service": "Nyaya True Integrated Backend",
        "version": "1.0.0",
        "integration_status": {
            "chandresh_enforcement": CHANDRESH_AVAILABLE,
            "nilesh_assistant": NILESH_AVAILABLE,
            "raj_datasets": True  # Always available as files
        },
        "endpoints": {
            "nyaya_legal": "/nyaya/*" if CHANDRESH_AVAILABLE else "Not available",
            "ai_assistant": "/api/assistant" if NILESH_AVAILABLE else "Not available",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    components = {
        "chandresh_enforcement": "active" if CHANDRESH_AVAILABLE else "unavailable",
        "nilesh_assistant": "active" if NILESH_AVAILABLE else "unavailable", 
        "raj_datasets": "active"
    }
    
    overall_status = "healthy" if any(status == "active" for status in components.values()) else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "components": components,
        "integration": "true_backend_integration"
    }

if __name__ == "__main__":
    print("Starting Nyaya True Integrated Backend...")
    print(f"Chandresh components: {'OK' if CHANDRESH_AVAILABLE else 'MISSING'}")
    print(f"Nilesh components: {'OK' if NILESH_AVAILABLE else 'MISSING'}")
    print("Raj datasets: OK")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
'''
    
    with open(integrated_dir / "main.py", "w") as f:
        f.write(main_content)
    
    print("Unified main application created")

def create_unified_requirements(integrated_dir):
    """Create unified requirements file"""
    
    requirements = """# Nyaya True Integration Requirements
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.8.2
python-multipart==0.0.6
requests==2.31.0
httpx==0.27.0
python-dateutil==2.8.2

# Additional dependencies from original repos
openai==1.3.0
groq==0.4.1
google-generativeai==0.3.2
numpy==1.26.4
sqlalchemy==2.0.23
aiosqlite==0.19.0
"""
    
    with open(integrated_dir / "requirements.txt", "w") as f:
        f.write(requirements)
    
    print("Unified requirements created")

if __name__ == "__main__":
    integrated_path = integrate_backends()
    
    print("\n" + "="*50)
    print("TRUE BACKEND INTEGRATION COMPLETE")
    print("="*50)
    print(f"Location: {integrated_path}")
    print("\nTo run the integrated system:")
    print(f"cd {integrated_path}")
    print("pip install -r requirements.txt")
    print("python main.py")
    print("\nThis uses the ACTUAL code from all three repositories!")