"""
Minimal Nyaya backend for Render deployment testing
"""
import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_minimal_app():
    """Create a minimal FastAPI app without complex dependencies"""
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import platform
    
    app = FastAPI(title="Nyaya Minimal Backend")
    
    class HealthResponse(BaseModel):
        status: str
        message: str
        python_version: str
        platform: str
        cwd: str
    
    @app.get("/")
    async def root():
        return {
            "service": "Nyaya Minimal Backend",
            "status": "running",
            "message": "Minimal version for debugging deployment issues",
            "version": "1.0.0"
        }
    
    @app.get("/health", response_model=HealthResponse)
    async def health():
        return HealthResponse(
            status="healthy",
            message="Service is running",
            python_version=sys.version,
            platform=platform.platform(),
            cwd=os.getcwd()
        )
    
    @app.get("/debug-info")
    async def debug_info():
        return {
            "python_path": sys.path[:10],
            "environment": dict(os.environ),
            "current_dir": str(Path(__file__).parent),
            "files_in_dir": [f.name for f in Path(__file__).parent.iterdir() if f.is_file()][:10]
        }
    
    @app.get("/test-components")
    async def test_components():
        """Test if we can import the main components"""
        results = {}
        
        # Test Chandresh components
        try:
            chandresh_path = str(Path(__file__).parent / "Nyaya_AI")
            if chandresh_path not in sys.path:
                sys.path.insert(0, chandresh_path)
            
            from enforcement_engine.engine import SovereignEnforcementEngine
            results["chandresh"] = "success"
        except Exception as e:
            results["chandresh"] = f"failed: {str(e)}"
        
        # Test Nilesh components
        try:
            nilesh_path = str(Path(__file__).parent / "AI_ASSISTANT_PhaseB_Integration")
            if nilesh_path not in sys.path:
                sys.path.insert(0, nilesh_path)
            
            from app.core.assistant_orchestrator import handle_assistant_request
            results["nilesh"] = "success"
        except Exception as e:
            results["nilesh"] = f"failed: {str(e)}"
        
        # Test main integration
        try:
            from true_integration import app as main_app
            results["main_integration"] = "success"
        except Exception as e:
            results["main_integration"] = f"failed: {str(e)}"
        
        return {"component_tests": results}
    
    return app

def main():
    logger.info("Starting minimal Nyaya backend...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Script directory: {Path(__file__).parent}")
    
    # Add component paths
    current_dir = Path(__file__).parent
    nyaya_path = str(current_dir / "Nyaya_AI")
    assistant_path = str(current_dir / "AI_ASSISTANT_PhaseB_Integration")
    
    if nyaya_path not in sys.path:
        sys.path.insert(0, nyaya_path)
        logger.info(f"Added Nyaya_AI path: {nyaya_path}")
    
    if assistant_path not in sys.path:
        sys.path.insert(0, assistant_path)
        logger.info(f"Added AI_ASSISTANT path: {assistant_path}")
    
    app = create_minimal_app()
    
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()