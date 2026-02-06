#!/usr/bin/env python3
"""
Debug script to check domain classification for technology-related queries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from legal_data_loader import legal_data_loader

def debug_domain_classification():
    """Debug domain classification for various queries"""
    queries = [
        "unauthorized access to phone",
        "cyber crime phone hacking",
        "computer unauthorized access",
        "phone privacy violation",
        "digital device intrusion",
        "unauthorized access"
    ]
    
    print("DOMAIN CLASSIFICATION DEBUG")
    print("="*60)
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        
        # Load domain map for inspection
        domain_map = legal_data_loader.domain_maps.get('IN', {})
        keyword_mapping = domain_map.get('keyword_mapping', {})
        
        print("  Keyword mapping for each subdomain:")
        for subdomain, keywords in keyword_mapping.items():
            query_lower = query.lower()
            matches = [kw for kw in keywords if kw.lower() in query_lower]
            if matches:
                print(f"    {subdomain}: {matches}")
        
        jurisdiction = legal_data_loader.detect_jurisdiction(query, None)
        domain, subdomain, confidence = legal_data_loader.classify_domain(query, jurisdiction)
        
        print(f"  Detected: Domain={domain}, Subdomain={subdomain}, Confidence={confidence}")

if __name__ == "__main__":
    debug_domain_classification()