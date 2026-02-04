#!/usr/bin/env python3
"""
Test script to verify the Render deployment setup
"""
import sys
import os
from pathlib import Path

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    # Test path setup
    current_dir = Path(__file__).parent
    nyaya_path = str(current_dir / "Nyaya_AI")
    if nyaya_path not in sys.path:
        sys.path.insert(0, nyaya_path)
        print(f"Added to path: {nyaya_path}")
    
    # Test Chandresh components
    try:
        from enforcement_engine.engine import SovereignEnforcementEngine
        print("✓ Chandresh's enforcement engine import successful")
    except ImportError as e:
        print(f"✗ Chandresh's enforcement engine import failed: {e}")
        return False
    
    # Test Nilesh components
    try:
        # Add Nilesh's path
        nilesh_path = str(current_dir / "AI_ASSISTANT_PhaseB_Integration")
        if nilesh_path not in sys.path:
            sys.path.insert(0, nilesh_path)
            
        from app.core.assistant_orchestrator import handle_assistant_request
        print("✓ Nilesh's assistant orchestrator import successful")
    except ImportError as e:
        print(f"⚠ Nilesh's assistant orchestrator import failed: {e}")
        print("  This is optional - system will run in fallback mode")
    
    # Test FastAPI app creation
    try:
        from true_integration import app
        print("✓ FastAPI app creation successful")
    except Exception as e:
        print(f"✗ FastAPI app creation failed: {e}")
        return False
    
    return True

def test_endpoints():
    """Test basic endpoints"""
    print("\nTesting endpoints...")
    
    try:
        from true_integration import app
        import asyncio
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        if response.status_code == 200:
            print("✓ Root endpoint working")
        else:
            print(f"✗ Root endpoint failed: {response.status_code}")
            return False
            
        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("✓ Health endpoint working")
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Endpoint testing failed: {e}")
        return False

def main():
    print("Nyaya Backend Deployment Verification")
    print("=" * 40)
    
    if test_imports():
        print("\n✓ All imports successful")
        if test_endpoints():
            print("\n✓ All endpoints working")
            print("\n✅ Deployment verification PASSED")
            return 0
        else:
            print("\n✗ Endpoint testing failed")
            return 1
    else:
        print("\n✗ Import testing failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())