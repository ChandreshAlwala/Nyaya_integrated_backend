#!/usr/bin/env python3
"""
Test edge cases for the legal query endpoint
"""

import requests
import json

def test_edge_cases():
    """Test edge cases for the legal query endpoint"""
    
    base_url = "http://localhost:8080"
    
    # Test cases for edge cases
    test_cases = [
        {
            "description": "Empty query",
            "query": "",
            "expected_status": 400
        },
        {
            "description": "Too short query",
            "query": "a",
            "expected_status": 400
        },
        {
            "description": "Serious criminal query",
            "query": "I have murdered",
            "expected_status": 200
        },
        {
            "description": "Civil matter without jurisdiction hint",
            "query": "property dispute",
            "expected_status": 200
        }
    ]
    
    print("Testing Edge Cases")
    print("=" * 30)
    
    # Start server
    import subprocess
    import os
    import time
    
    env = os.environ.copy()
    env["PORT"] = "8080"
    
    server_process = subprocess.Popen(
        ["python", "integrated_nyaya_server.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        for test_case in test_cases:
            print(f"\nTesting: {test_case['description']}")
            print(f"Query: '{test_case['query']}'")
            
            try:
                response = requests.post(
                    f"{base_url}/api/legal/query",
                    json={"query": test_case["query"]},
                    timeout=10
                )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"Jurisdiction: {result.get('jurisdiction', 'N/A')}")
                    print(f"Domain: {result.get('domain', 'N/A')}")
                    print(f"Legal guidance sections: {len(result.get('legal_guidance', []))}")
                    if result.get('legal_guidance'):
                        print("✅ Returns legal guidance")
                    else:
                        print("⚠️  No legal guidance returned")
                        
                elif response.status_code == 400:
                    result = response.json()
                    print(f"Error: {result.get('error', 'Unknown error')}")
                    print("✅ Proper validation error")
                    
                else:
                    print(f"❌ Unexpected status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
    
    finally:
        # Stop server
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()
        print("Server stopped.")

if __name__ == "__main__":
    test_edge_cases()