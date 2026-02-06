#!/usr/bin/env python3
"""
Test the murder query fix
"""

import requests
import json

def test_murder_query():
    """Test the 'I have murdered' query"""
    
    response = requests.post(
        "http://localhost:8080/api/legal/query",
        json={
            "query": "I have murdered",
            "jurisdiction_hint": "UAE"
        },
        timeout=15
    )
    
    if response.status_code == 200:
        result = response.json()
        print("MURDER QUERY RESPONSE:")
        print("="*60)
        print(json.dumps(result, indent=2))
        
        # Check key components
        print("\nKEY COMPONENTS CHECK:")
        print(f"Status: {result.get('status')}")
        print(f"Domain: {result.get('domain')}")
        print(f"Legal Guidance Sections: {len(result.get('legal_guidance', []))}")
        print(f"Citations: {len(result.get('citations', []))}")
        
        if result.get('legal_guidance'):
            guidance = result['legal_guidance'][0]
            print(f"\nFirst Section Title: {guidance.get('title')}")
            print(f"Has Definition: {'definition' in guidance}")
            print(f"Has Elements: {len(guidance.get('elements', []))} elements")
            print(f"Has Penalties: {'penalties' in guidance}")
            print(f"Has Process: {len(guidance.get('process', []))} steps")
            print(f"Has Citations: {len(guidance.get('citations', []))} citations")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_murder_query()