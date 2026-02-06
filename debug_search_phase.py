#!/usr/bin/env python3
"""
Debug script to check the search phase for technology-related queries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from legal_data_loader import legal_data_loader

def debug_search_phase():
    """Debug search phase for the main query"""
    query = "unauthorized access to phone"
    
    print("SEARCH PHASE DEBUG")
    print("="*60)
    print(f"Query: '{query}'")
    
    jurisdiction = legal_data_loader.detect_jurisdiction(query, None)
    print(f"Jurisdiction: {jurisdiction}")
    
    domain, subdomain, confidence = legal_data_loader.classify_domain(query, jurisdiction)
    print(f"Domain: {domain}, Subdomain: {subdomain}, Confidence: {confidence}")
    
    # Manually call the search function for Indian law
    dataset = legal_data_loader.law_datasets.get(jurisdiction, {})
    print(f"Dataset keys: {list(dataset.keys())}")
    
    # Show IT Act data if it exists
    if 'special_laws' in dataset and 'it_act' in dataset['special_laws']:
        it_act_data = dataset['special_laws']['it_act']
        print(f"IT Act data: {it_act_data}")
    
    # Perform search
    legal_data = legal_data_loader.search_law_data(query, jurisdiction, domain, subdomain)
    print(f"Search results: {len(legal_data)} items")
    
    for i, result in enumerate(legal_data):
        print(f"  Result {i+1}: {result}")

if __name__ == "__main__":
    debug_search_phase()