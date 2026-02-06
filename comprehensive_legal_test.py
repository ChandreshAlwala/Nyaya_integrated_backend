#!/usr/bin/env python3
"""
Comprehensive test to demonstrate the enhanced legal data retrieval system
"""

import requests
import json

def test_comprehensive_legal_data():
    """Test various queries to show comprehensive legal information"""
    
    test_cases = [
        {
            "query": "unauthorized access to phone",
            "description": "Technology/Cyber Crime Query - Should return IT Act provisions"
        },
        {
            "query": "murder first degree",
            "description": "Criminal Law Query - Should return BNS/IPC provisions"  
        },
        {
            "query": "contract dispute breach of agreement",
            "description": "Civil Law Query - Should return civil procedure provisions"
        }
    ]
    
    base_url = "http://localhost:8080"
    
    print("COMPREHENSIVE LEGAL DATA RETRIEVAL TEST")
    print("="*80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Query: '{test_case['query']}'")
        print("-" * 80)
        
        try:
            response = requests.post(
                f"{base_url}/api/legal/query",
                json={
                    "query": test_case['query'],
                    "jurisdiction_hint": "IN"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Display key information
                print(f"   Status: {result.get('status')}")
                print(f"   Jurisdiction: {result.get('jurisdiction')}")
                print(f"   Domain: {result.get('domain')}")
                print(f"   Confidence: {result.get('confidence'):.2f}")
                
                # Display legal summary if available
                legal_summary = result.get('legal_summary', {})
                if legal_summary:
                    print(f"   Total Sections: {legal_summary.get('total_sections', 0)}")
                    print(f"   Key Provisions: {legal_summary.get('key_provisions_count', 0)}")
                    print(f"   Confidence Level: {legal_summary.get('confidence_level', 'N/A')}")
                
                # Display legal guidance sections
                legal_guidance = result.get('legal_guidance', [])
                print(f"\n   Legal Provisions Found: {len(legal_guidance)}")
                
                for j, section in enumerate(legal_guidance[:2], 1):  # Show first 2 sections
                    print(f"\n   Section {j}: {section.get('title', 'N/A')}")
                    print(f"     Type: {section.get('type', 'N/A')}")
                    
                    # Show key components
                    if 'definition' in section:
                        print(f"     Definition: {section['definition'][:100]}...")
                    if 'elements' in section and section['elements']:
                        print(f"     Elements: {len(section['elements'])} key elements")
                    if 'penalties' in section:
                        penalties = section['penalties']
                        if isinstance(penalties, dict):
                            print(f"     Penalties: {', '.join([f'{k}: {v}' for k, v in penalties.items()][:3])}")
                        else:
                            print(f"     Penalties: {penalties}")
                    if 'process' in section and section['process']:
                        print(f"     Process Steps: {len(section['process'])} steps")
                    
                    # Show confidence
                    print(f"     Confidence: {section.get('confidence', 'N/A'):.2f}")
                
                # Show citations
                citations = result.get('citations', [])
                if citations:
                    print(f"\n   Key Citations ({len(citations)} total):")
                    for citation in citations[:3]:  # Show first 3 citations
                        print(f"     • {citation}")
                
                print(f"\n   Disclaimer: {result.get('disclaimer', 'N/A')}")
                
            else:
                print(f"   ERROR: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ERROR: {str(e)}")
    
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST COMPLETED")
    print("="*80)

if __name__ == "__main__":
    test_comprehensive_legal_data()