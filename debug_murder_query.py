#!/usr/bin/env python3
"""
Debug the 'I have murdered' query to understand why it's not finding relevant data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from legal_data_loader import legal_data_loader

def debug_murder_query():
    """Debug the murder query classification and search"""
    query = "I have murdered"
    
    print("MURDER QUERY DEBUG")
    print("="*60)
    print(f"Query: '{query}'")
    
    # Step 1: Jurisdiction detection
    jurisdiction = legal_data_loader.detect_jurisdiction(query, "UAE")
    print(f"1. Jurisdiction: {jurisdiction}")
    
    # Step 2: Domain classification
    domain, subdomain, confidence = legal_data_loader.classify_domain(query, jurisdiction)
    print(f"2. Domain: {domain}, Subdomain: {subdomain}, Confidence: {confidence}")
    
    # Step 3: Check UAE domain map
    if jurisdiction in legal_data_loader.domain_maps:
        domain_map = legal_data_loader.domain_maps[jurisdiction]
        keyword_mapping = domain_map.get('keyword_mapping', {})
        
        print(f"3. UAE Keyword Mapping:")
        query_lower = query.lower()
        for subdomain_key, keywords in keyword_mapping.items():
            matches = [kw for kw in keywords if kw.lower() in query_lower]
            if matches:
                print(f"   {subdomain_key}: {matches}")
    
    # Step 4: Check UAE law dataset
    if jurisdiction in legal_data_loader.law_datasets:
        dataset = legal_data_loader.law_datasets[jurisdiction]
        print(f"4. UAE Dataset Keys: {list(dataset.keys())}")
        
        # Check if criminal law data exists
        if 'criminal_law' in dataset:
            print("   Criminal law data found")
            # Show sample criminal law sections
            criminal_data = dataset['criminal_law']
            print(f"   Criminal law keys: {list(criminal_data.keys())}")
        else:
            print("   No criminal law data found")
    
    # Step 5: Perform actual search
    legal_data = legal_data_loader.search_law_data(query, jurisdiction, domain, subdomain)
    print(f"5. Search results count: {len(legal_data)}")
    
    # Show result details
    for i, result in enumerate(legal_data):
        print(f"   Result {i+1}: {result.get('type', 'N/A')} - {result.get('title', result.get('offence', 'N/A'))}")

if __name__ == "__main__":
    debug_murder_query()