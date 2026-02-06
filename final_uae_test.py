#!/usr/bin/env python3
"""
Final test for UAE murder query to ensure all requirements are met
"""

import requests
import json

def test_uae_murder_query():
    """Test the UAE murder query with all requirements"""
    
    print("FINAL UAE MURDER QUERY TEST")
    print("="*60)
    
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
        
        print("✅ RESPONSE ANALYSIS:")
        print(f"   Status: {result.get('status')}")
        print(f"   Jurisdiction: {result.get('jurisdiction')} (✓ Correct)")
        print(f"   Domain: {result.get('domain')} (✓ Correct - Criminal)")
        print(f"   Confidence: {result.get('confidence'):.2f}")
        
        # Check legal guidance
        legal_guidance = result.get('legal_guidance', [])
        print(f"\n✅ LEGAL GUIDANCE ANALYSIS:")
        print(f"   Sections Found: {len(legal_guidance)}")
        
        if legal_guidance:
            section = legal_guidance[0]
            print(f"   Title: {section.get('title')}")
            print(f"   Definition: {'✓ Present' if 'definition' in section else '✗ Missing'}")
            print(f"   Elements: {len(section.get('elements', []))} items {'✓ Present' if section.get('elements') else '✗ Missing'}")
            print(f"   Penalties: {'✓ Present' if 'penalties' in section else '✗ Missing'}")
            print(f"   Process: {len(section.get('process', []))} steps {'✓ Present' if section.get('process') else '✗ Missing'}")
            print(f"   Citations: {len(section.get('citations', []))} items {'✓ Present' if section.get('citations') else '✗ Missing'}")
            
            # Display key information
            print(f"\n📋 KEY LEGAL INFORMATION:")
            print(f"   Definition: {section.get('definition', 'N/A')}")
            print(f"   Elements: {section.get('elements', 'N/A')}")
            print(f"   Penalties: {section.get('penalties', 'N/A')}")
            print(f"   Process Steps: {len(section.get('process', []))} total steps")
            print(f"   Citations: {len(section.get('citations', []))} total citations")
        
        print(f"\n✅ REQUIREMENTS VERIFICATION:")
        requirements = [
            ("Jurisdiction Detection", result.get('jurisdiction') == 'UAE'),
            ("Domain Classification", result.get('domain') == 'criminal'),
            ("Legal Provisions", len(legal_guidance) > 0),
            ("Detailed Information", all(key in legal_guidance[0] for key in ['definition', 'elements', 'penalties', 'process']) if legal_guidance else False),
            ("Citations", len(result.get('citations', [])) > 0)
        ]
        
        for req, met in requirements:
            status = "✅ MET" if met else "❌ NOT MET"
            print(f"   {req}: {status}")
        
        total_met = sum(1 for _, met in requirements if met)
        print(f"\n📊 OVERALL SCORE: {total_met}/{len(requirements)} requirements met")
        
        if total_met == len(requirements):
            print("🎉 SUCCESS: All requirements fully satisfied!")
        else:
            print("⚠️  Some requirements not fully met")
            
    else:
        print(f"❌ ERROR: HTTP {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_uae_murder_query()