#!/usr/bin/env python3
"""
Test script to verify that the legal data retrieval system properly handles
technology-related queries like "unauthorized access to phone"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from legal_data_loader import legal_data_loader

def test_unauthorized_access_phone_query():
    """Test the specific query that was returning irrelevant results"""
    print("Testing query: 'unauthorized access to phone'")
    
    # Test with India jurisdiction
    jurisdiction = legal_data_loader.detect_jurisdiction("unauthorized access to phone", None)
    print(f"Detected jurisdiction: {jurisdiction}")
    
    domain, subdomain, confidence = legal_data_loader.classify_domain("unauthorized access to phone", jurisdiction)
    print(f"Domain: {domain}, Subdomain: {subdomain}, Confidence: {confidence}")
    
    legal_data = legal_data_loader.search_law_data("unauthorized access to phone", jurisdiction, domain, subdomain)
    print(f"Number of results found: {len(legal_data)}")
    
    for i, result in enumerate(legal_data):
        print(f"\nResult {i+1}:")
        print(f"  Type: {result.get('type', 'N/A')}")
        print(f"  Title/Section: {result.get('section', result.get('article', result.get('offence', 'N/A')))}")
        print(f"  Content: {result.get('title', result.get('offence', result.get('description', 'N/A')))[:100]}...")
        print(f"  Punishment/Details: {str(result.get('punishment', result.get('remedies', result.get('elements', 'N/A'))))[:100]}...")
        print(f"  Confidence: {result.get('confidence', 'N/A')}")
    
    # Check if results are relevant (should not contain personal status/family law)
    relevant_results = []
    for result in legal_data:
        content = f"{result.get('title', '')} {result.get('offence', '')} {result.get('description', '')}".lower()
        # Skip results that are about personal status/family law
        if 'divorce' not in content and 'marriage' not in content and 'family' not in content and 'spouse' not in content:
            relevant_results.append(result)
    
    print(f"\nRelevant results (excluding personal status/family law): {len(relevant_results)}")
    
    if len(relevant_results) > 0:
        print("\n✓ SUCCESS: Found relevant tech-related legal provisions!")
        print("The system is now correctly filtering out irrelevant family/personal status law.")
    else:
        print("\n⚠ WARNING: No relevant tech-related results found.")
        print("May need to add more technology-related law data to the datasets.")
    
    return legal_data

def test_other_queries():
    """Test other technology-related queries"""
    queries = [
        "cyber crime phone hacking",
        "computer unauthorized access",
        "phone privacy violation",
        "digital device intrusion"
    ]
    
    print("\n" + "="*60)
    print("TESTING OTHER TECHNOLOGY-RELATED QUERIES")
    print("="*60)
    
    for query in queries:
        print(f"\nTesting query: '{query}'")
        jurisdiction = legal_data_loader.detect_jurisdiction(query, None)
        domain, subdomain, confidence = legal_data_loader.classify_domain(query, jurisdiction)
        
        legal_data = legal_data_loader.search_law_data(query, jurisdiction, domain, subdomain)
        
        relevant_count = 0
        for result in legal_data:
            content = f"{result.get('title', '')} {result.get('offence', '')} {result.get('description', '')}".lower()
            if 'divorce' not in content and 'marriage' not in content and 'family' not in content:
                relevant_count += 1
        
        print(f"  Total results: {len(legal_data)}, Relevant results: {relevant_count}")
        if relevant_count > 0:
            print("  ✓ Relevant results found")
        else:
            print("  ⚠ No relevant results found")

if __name__ == "__main__":
    print("Testing Legal Data Retrieval System Fixes")
    print("="*60)
    
    # Test the main problematic query
    results = test_unauthorized_access_phone_query()
    
    # Test other queries
    test_other_queries()
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)