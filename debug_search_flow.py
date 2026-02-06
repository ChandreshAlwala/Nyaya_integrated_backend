#!/usr/bin/env python3
"""
Debug the search flow to understand why IT Act sections aren't being returned
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from legal_data_loader import legal_data_loader

def debug_search_flow():
    """Debug the complete search flow"""
    query = "unauthorized access to phone"
    
    print("SEARCH FLOW DEBUG")
    print("="*60)
    print(f"Query: '{query}'")
    
    # Step 1: Jurisdiction detection
    jurisdiction = legal_data_loader.detect_jurisdiction(query, None)
    print(f"1. Jurisdiction: {jurisdiction}")
    
    # Step 2: Domain classification
    domain, subdomain, confidence = legal_data_loader.classify_domain(query, jurisdiction)
    print(f"2. Domain: {domain}, Subdomain: {subdomain}, Confidence: {confidence}")
    
    # Step 3: Check if it's a tech query
    query_lower = query.lower()
    query_words = set(query_lower.split())
    tech_terms = {'computer', 'digital', 'electronic', 'phone', 'mobile', 'device', 'access', 
                 'unauthorized', 'cyber', 'hacking', 'data', 'privacy', 'telecommunication'}
    
    is_tech_query = any(term in query_words for term in tech_terms)
    print(f"3. Is tech query: {is_tech_query}")
    
    # Step 4: Check for direct fallback matches
    fallback_tech_provisions = {
        'unauthorized access to phone': {
            'type': 'it_act_section',
            'section': 'IT Act Section 43, 66',
            'title': 'Unauthorized Access to Electronic Devices',
            'description': 'Unauthorized access to computer resources, electronic devices, or communication systems',
            'penalties': 'Up to Rs. 1 crore compensation under Section 43, imprisonment up to 3 years under Section 66',
            'process': ['File complaint with Cyber Crime Cell', 'Digital evidence collection', 'Forensic analysis', 'Police investigation', 'Special court trial']
        }
    }
    
    direct_matches = []
    for pattern, provision in fallback_tech_provisions.items():
        if pattern in query_lower or any(term in query_lower for term in pattern.split()):
            matched_provision = provision.copy()
            matched_provision['relevance_score'] = 0.9
            matched_provision['confidence'] = 0.9
            direct_matches.append(matched_provision)
    
    print(f"4. Direct fallback matches: {len(direct_matches)}")
    if direct_matches:
        print(f"   Matched pattern: {list(fallback_tech_provisions.keys())[0]}")
    
    # Step 5: Perform actual search
    legal_data = legal_data_loader.search_law_data(query, jurisdiction, domain, subdomain)
    print(f"5. Search results count: {len(legal_data)}")
    
    # Show result types
    result_types = [result.get('type', 'unknown') for result in legal_data]
    print(f"   Result types: {result_types}")
    
    # Show first result details
    if legal_data:
        first_result = legal_data[0]
        print(f"   First result type: {first_result.get('type')}")
        print(f"   First result title: {first_result.get('title', first_result.get('offence', 'N/A'))}")

if __name__ == "__main__":
    debug_search_flow()