"""
Debug script for Render deployment issues
"""
import os
import sys
import logging
from pathlib import Path
import traceback

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def debug_environment():
    """Debug the environment and paths"""
    logger.info("=== Environment Debug ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Script directory: {Path(__file__).parent}")
    logger.info(f"PORT environment variable: {os.environ.get('PORT', 'Not set')}")
    
    logger.info("=== Python Path ===")
    for i, path in enumerate(sys.path):
        logger.info(f"  {i}: {path}")
    
    logger.info("=== Environment Variables ===")
    for key, value in os.environ.items():
        if any(keyword in key.upper() for keyword in ['PATH', 'PYTHON', 'VIRTUAL']):
            logger.info(f"  {key}: {value}")

def test_imports_step_by_step():
    """Test imports step by step to identify exactly where it fails"""
    logger.info("=== Testing Imports Step by Step ===")
    
    current_dir = Path(__file__).parent
    
    # Test 1: Basic FastAPI
    try:
        logger.info("1. Testing FastAPI import...")
        from fastapi import FastAPI
        logger.info("✓ FastAPI import successful")
    except Exception as e:
        logger.error(f"✗ FastAPI import failed: {e}")
        return False
    
    # Test 2: Add Nyaya_AI to path
    try:
        nyaya_path = str(current_dir / "Nyaya_AI")
        if nyaya_path not in sys.path:
            sys.path.insert(0, nyaya_path)
            logger.info(f"Added Nyaya_AI to path: {nyaya_path}")
        
        # Test importing from Nyaya_AI
        logger.info("2. Testing Nyaya_AI enforcement_engine import...")
        from enforcement_engine.engine import SovereignEnforcementEngine
        logger.info("✓ Nyaya_AI enforcement_engine import successful")
    except Exception as e:
        logger.error(f"✗ Nyaya_AI enforcement_engine import failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
    
    # Test 3: Add AI_ASSISTANT to path
    try:
        assistant_path = str(current_dir / "AI_ASSISTANT_PhaseB_Integration")
        if assistant_path not in sys.path:
            sys.path.insert(0, assistant_path)
            logger.info(f"Added AI_ASSISTANT to path: {assistant_path}")
        
        logger.info("3. Testing AI_ASSISTANT import...")
        from app.core.assistant_orchestrator import handle_assistant_request
        logger.info("✓ AI_ASSISTANT import successful")
    except Exception as e:
        logger.warning(f"⚠ AI_ASSISTANT import failed (optional): {e}")
        logger.warning(f"Traceback: {traceback.format_exc()}")
    
    # Test 4: Main application import
    try:
        logger.info("4. Testing true_integration import...")
        from true_integration import app
        logger.info("✓ true_integration import successful")
        return True
    except Exception as e:
        logger.error(f"✗ true_integration import failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def create_debug_app():
    """Create a debug FastAPI app with detailed information"""
    from fastapi import FastAPI
    import platform
    
    app = FastAPI(title="Nyaya Debug App")
    
    @app.get("/")
    async def root():
        return {
            "status": "debug",
            "message": "Debug application running",
            "python_version": sys.version,
            "platform": platform.platform(),
            "cwd": os.getcwd(),
            "script_dir": str(Path(__file__).parent),
            "python_path": sys.path[:10],  # First 10 paths
            "environment": {
                "PORT": os.environ.get("PORT", "Not set"),
                "PYTHON_VERSION": os.environ.get("PYTHON_VERSION", "Not set")
            }
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "message": "Debug app running"}
    
    @app.get("/test-imports")
    async def test_imports():
        try:
            # Test the actual imports that might fail
            results = {}
            
            # Test Chandresh components
            try:
                from enforcement_engine.engine import SovereignEnforcementEngine
                results["chandresh"] = "success"
            except Exception as e:
                results["chandresh"] = f"failed: {str(e)}"
            
            # Test Nilesh components
            try:
                from app.core.assistant_orchestrator import handle_assistant_request
                results["nilesh"] = "success"
            except Exception as e:
                results["nilesh"] = f"failed: {str(e)}"
            
            # Test main app
            try:
                from true_integration import app as main_app
                results["main_app"] = "success"
            except Exception as e:
                results["main_app"] = f"failed: {str(e)}"
            
            return {"import_tests": results}
        except Exception as e:
            return {"error": str(e), "traceback": traceback.format_exc()}
    
    return app

def main():
    debug_environment()
    
    if test_imports_step_by_step():
        logger.info("All imports successful, trying to import main app...")
        try:
            from true_integration import app
            logger.info("Successfully imported main application")
        except Exception as e:
            logger.error(f"Failed to import main app: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            app = create_debug_app()
    else:
        logger.error("Import tests failed, creating debug app")
        app = create_debug_app()
    
    # Start server
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting debug server on port {port}")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")

if __name__ == "__main__":
    main()