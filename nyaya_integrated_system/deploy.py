"""
Production Deployment Configuration
Live deployment setup for Nyaya integrated system
"""
import os
import subprocess
import sys
from pathlib import Path

def setup_environment():
    """Setup production environment"""
    print("🔧 Setting up production environment...")
    
    # Install dependencies
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    print("✅ Environment setup complete")

def validate_system():
    """Validate system before deployment"""
    print("🔍 Validating system components...")
    
    # Check if all required files exist
    required_files = [
        "main.py",
        "core/legal_engine.py",
        "core/enforcement_engine.py",
        "core/rl_engine.py",
        "core/api_orchestrator.py",
        "schemas/api_contracts.py"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Required file missing: {file_path}")
    
    print("✅ System validation complete")

def start_production_server():
    """Start production server"""
    print("🚀 Starting Nyaya production server...")
    
    # Set production environment variables
    os.environ["ENV"] = "production"
    os.environ["HOST"] = "0.0.0.0"
    os.environ["PORT"] = "8000"
    
    # Start server
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--workers", "1",
        "--log-level", "info"
    ])

if __name__ == "__main__":
    try:
        setup_environment()
        validate_system()
        start_production_server()
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)