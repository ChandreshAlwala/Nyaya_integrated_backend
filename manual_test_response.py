#!/usr/bin/env python3
"""
Manual test to see the actual response content for the fixed query
"""

import requests
import json

def test_response_content():
    """Test and display the actual response content"""
    
    response = requests.post(
        "http://localhost:8080/api/legal/query",
        json={
            "query": "unauthorized access to phone",
            "jurisdiction_hint": "IN"
        },
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print("RESPONSE FOR 'unauthorized access to phone':")
        print("="*60)
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_response_content()