"""
Nyaya Production Entry Point for Render with enhanced error handling
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

try:
    # Add current directory to path for imports
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    logger.info("Importing true_integration module...")
    from true_integration import app
    logger.info("Successfully imported true_integration")
    
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Sys path contents:")
    for path in sys.path:
        logger.error(f"  {path}")
    
    # Fallback - create minimal FastAPI app
    from fastapi import FastAPI
    app = FastAPI(title="Nyaya Backend - Fallback Mode")
    
    @app.get("/")
    async def root():
        return {
            "status": "error",
            "message": f"Failed to import main application: {str(e)}",
            "sys_path": sys.path[:5]  # Show first 5 paths
        }
    
    @app.get("/health")
    async def health():
        return {"status": "unhealthy", "error": str(e)}

except Exception as e:
    logger.error(f"Unexpected error during startup: {e}")
    
    # Fallback - create minimal FastAPI app
    from fastapi import FastAPI
    app = FastAPI(title="Nyaya Backend - Error Mode")
    
    @app.get("/")
    async def root():
        return {
            "status": "error", 
            "message": f"Startup error: {str(e)}",
            "type": type(e).__name__
        }
    
    @app.get("/health")
    async def health():
        return {"status": "error", "message": str(e)}

# Get port from environment
port = int(os.environ.get("PORT", 8000))
logger.info(f"Starting server on port {port}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn server...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )