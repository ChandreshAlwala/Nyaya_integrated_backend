#!/usr/bin/env python3
"""
Test the fixed legal query endpoint to ensure it properly retrieves and returns legal information.
"""

import requests
import json
import time

def test_legal_query_endpoint():
    """Test the legal query endpoint with various queries"""
    
    base_url = "http://localhost:8080"
    
    # Test cases for different jurisdictions and domains
    test_cases = [
        {
            "name": "Indian murder query",
            "query": "What are the charges for murder in India?",
            "jurisdiction_hint": "IN",
            "expected_jurisdiction": "IN",
            "expected_domain": "criminal"
        },
        {
            "name": "UAE criminal query",
            "query": "What is the punishment for theft in UAE?",
            "jurisdiction_hint": "UAE",
            "expected_jurisdiction": "UAE",
            "expected_domain": "criminal"
        },
        {
            "name": "UK civil query",
            "query": "How to file a divorce case in UK?",
            "jurisdiction_hint": "UK",
            "expected_jurisdiction": "UK",
            "expected_domain": "civil"
        },
        {
            "name": "Technology-related query",
            "query": "What are the laws for unauthorized access to phone in India?",
            "jurisdiction_hint": "IN",
            "expected_jurisdiction": "IN",
            "expected_domain": "technology"
        }
    ]
    
    print("Testing Legal Query Endpoint")
    print("=" * 50)
    
    # Start the server in background
    print("Starting server...")
    import subprocess
    import os
    
    # Set environment variable for port
    env = os.environ.copy()
    env["PORT"] = "8080"
    
    # Start server process
    server_process = subprocess.Popen(
        ["python", "integrated_nyaya_server.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(5)
    
    try:
        # Test each case
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: {test_case['name']}")
            print(f"   Query: {test_case['query']}")
            
            try:
                response = requests.post(
                    f"{base_url}/api/legal/query",
                    json={
                        "query": test_case["query"],
                        "jurisdiction_hint": test_case["jurisdiction_hint"]
                    },
                    timeout=15
                )
                
                print(f"   Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Success!")
                    print(f"   Jurisdiction: {result.get('jurisdiction', 'N/A')}")
                    print(f"   Domain: {result.get('domain', 'N/A')}")
                    print(f"   Confidence: {result.get('confidence', 'N/A')}")
                    print(f"   Legal guidance sections: {len(result.get('legal_guidance', []))}")
                    print(f"   Citations: {len(result.get('citations', []))}")
                    
                    # Check if response contains expected data
                    has_guidance = len(result.get('legal_guidance', [])) > 0
                    has_citations = len(result.get('citations', [])) > 0
                    has_jurisdiction = result.get('jurisdiction') == test_case['expected_jurisdiction']
                    
                    if has_guidance and has_citations and has_jurisdiction:
                        print(f"   🎉 Complete legal information retrieved!")
                    else:
                        print(f"   ⚠️  Partial information retrieved")
                        
                elif response.status_code == 400:
                    result = response.json()
                    print(f"   ⚠️  Validation error: {result.get('error', 'Unknown validation error')}")
                    
                elif response.status_code == 500:
                    result = response.json()
                    print(f"   ❌ Server error: {result.get('error', 'Unknown server error')}")
                    
                else:
                    print(f"   ❌ Unexpected status code: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Request failed: {e}")
            except Exception as e:
                print(f"   ❌ Unexpected error: {e}")
    
    finally:
        # Stop the server
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()
        print("Server stopped.")

if __name__ == "__main__":
    test_legal_query_endpoint()