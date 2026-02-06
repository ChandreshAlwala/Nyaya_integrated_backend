#!/usr/bin/env python3
"""
Integration test to verify that the legal data retrieval fixes work with the actual backend server
"""

import requests
import json
import time

def test_backend_legal_query_fix():
    """Test the backend server with the fixed legal data retrieval system"""
    
    # Test the main problematic query that was returning irrelevant results
    test_queries = [
        {
            "query": "unauthorized access to phone",
            "description": "Main problematic query that was returning family law instead of cyber law"
        },
        {
            "query": "cyber crime phone hacking", 
            "description": "Technology-related query that should return cyber crime provisions"
        },
        {
            "query": "divorce proceedings property division",
            "description": "Family law query that should return family law provisions (to verify it still works)"
        }
    ]
    
    base_url = "http://localhost:8080"
    
    print("INTEGRATION TEST: Legal Data Retrieval Fixes")
    print("="*60)
    
    # Test each query
    for test_case in test_queries:
        print(f"\nTesting: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        
        try:
            # Test legal query endpoint
            response = requests.post(
                f"{base_url}/api/legal/query",
                json={
                    "query": test_case['query'],
                    "jurisdiction_hint": "IN"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Status: {result.get('status', 'N/A')}")
                print(f"  Jurisdiction: {result.get('jurisdiction', 'N/A')}")
                print(f"  Domain: {result.get('domain', 'N/A')}")
                print(f"  Confidence: {result.get('confidence', 'N/A')}")
                
                # Check if legal guidance is provided
                legal_guidance = result.get('legal_guidance', [])
                print(f"  Legal guidance sections: {len(legal_guidance)}")
                
                # Check content for relevance
                relevant_sections = 0
                for section in legal_guidance:
                    title = section.get('title', '').lower()
                    content = str(section.get('content', '')).lower()
                    
                    # Check if it's tech-related for tech queries, or family-related for family queries
                    if 'phone' in test_case['query'].lower() or 'cyber' in test_case['query'].lower():
                        # Tech query - should not contain family law terms
                        if 'divorce' not in title and 'marriage' not in title and 'family' not in title:
                            relevant_sections += 1
                    else:
                        # Family query - should contain family law terms
                        if 'divorce' in title or 'marriage' in title or 'family' in title:
                            relevant_sections += 1
                
                print(f"  Relevant sections: {relevant_sections}")
                
                if relevant_sections > 0:
                    print("  ✓ SUCCESS: Relevant legal provisions returned")
                else:
                    print("  ⚠ WARNING: No relevant legal provisions found")
                    
            else:
                print(f"  ERROR: HTTP {response.status_code}")
                print(f"  Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print("  ERROR: Could not connect to backend server")
            print("  Please ensure the integrated_nyaya_server.py is running on port 8080")
            return False
        except Exception as e:
            print(f"  ERROR: {str(e)}")
    
    print("\n" + "="*60)
    print("INTEGRATION TEST COMPLETED")
    print("="*60)
    return True

if __name__ == "__main__":
    test_backend_legal_query_fix()