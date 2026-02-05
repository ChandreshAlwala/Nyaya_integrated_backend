import requests
import json

def test_new_endpoints():
    base_url = 'http://localhost:8080'
    
    print('Testing NEWLY IMPLEMENTED endpoints...')
    print('=' * 50)
    
    # Test 1: Documentation endpoint
    print('1. Testing GET /docs')
    try:
        response = requests.get(f'{base_url}/docs', timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 200}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Title: {data.get("title", "N/A")}')
            print(f'   Version: {data.get("version", "N/A")}')
            print(f'   Has endpoints: {"endpoints" in data}')
            print(f'   Has schemas: {"schemas" in data}')
    except Exception as e:
        print(f'   Error: {e}')
    
    print()
    
    # Test 2: Feedback endpoint - valid request
    print('2. Testing POST /nyaya/feedback (valid)')
    try:
        payload = {
            'trace_id': 'test_feedback_123',
            'rating': 5,
            'feedback_type': 'clarity',
            'comment': 'Very helpful legal guidance provided'
        }
        response = requests.post(f'{base_url}/nyaya/feedback', json=payload, timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 200}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Status: {data.get("status", "N/A")}')
            print(f'   Has feedback_details: {"feedback_details" in data}')
            print(f'   Has enforcement_metadata: {"enforcement_metadata" in data}')
    except Exception as e:
        print(f'   Error: {e}')
    
    print()
    
    # Test 3: Feedback endpoint - invalid rating
    print('3. Testing POST /nyaya/feedback (invalid rating)')
    try:
        payload = {
            'trace_id': 'test_feedback_123',
            'rating': 10,  # Invalid rating
            'feedback_type': 'clarity'
        }
        response = requests.post(f'{base_url}/nyaya/feedback', json=payload, timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 400}')  # Should be validation error
        if response.status_code == 400:
            data = response.json()
            print(f'   Error: {data.get("error", "N/A")}')
    except Exception as e:
        print(f'   Error: {e}')
    
    print()
    
    # Test 4: Explain reasoning endpoint - brief level
    print('4. Testing POST /nyaya/explain_reasoning (brief)')
    try:
        payload = {
            'trace_id': 'test_explain_123',
            'explanation_level': 'brief'
        }
        response = requests.post(f'{base_url}/nyaya/explain_reasoning', json=payload, timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 200}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Level: {data.get("explanation_level", "N/A")}')
            print(f'   Has explanation: {"explanation" in data}')
            print(f'   Has reasoning_tree: {"reasoning_tree" in data}')
    except Exception as e:
        print(f'   Error: {e}')
    
    print()
    
    # Test 5: Explain reasoning endpoint - detailed level
    print('5. Testing POST /nyaya/explain_reasoning (detailed)')
    try:
        payload = {
            'trace_id': 'test_explain_456',
            'explanation_level': 'detailed'
        }
        response = requests.post(f'{base_url}/nyaya/explain_reasoning', json=payload, timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 200}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Level: {data.get("explanation_level", "N/A")}')
            print(f'   Has detailed explanation: {"explanation" in data and "processing_details" in data.get("explanation", {})}')
    except Exception as e:
        print(f'   Error: {e}')
    
    print()
    
    # Test 6: Explain reasoning endpoint - constitutional level
    print('6. Testing POST /nyaya/explain_reasoning (constitutional)')
    try:
        payload = {
            'trace_id': 'test_explain_789',
            'explanation_level': 'constitutional'
        }
        response = requests.post(f'{base_url}/nyaya/explain_reasoning', json=payload, timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 200}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Level: {data.get("explanation_level", "N/A")}')
            print(f'   Has constitutional_articles: {len(data.get("constitutional_articles", [])) > 0}')
            print(f'   Has constitutional_basis: {"constitutional_basis" in data.get("explanation", {})}')
    except Exception as e:
        print(f'   Error: {e}')
    
    print()
    
    # Test 7: Debug nonce state endpoint
    print('7. Testing GET /debug/nonce-state')
    try:
        response = requests.get(f'{base_url}/debug/nonce-state', timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 200}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Pending nonces: {data.get("pending_nonces_count", "N/A")}')
            print(f'   Used nonces: {data.get("used_nonces_count", "N/A")}')
            print(f'   TTL: {data.get("ttl_seconds", "N/A")} seconds')
    except Exception as e:
        print(f'   Error: {e}')
    
    print()
    
    # Test 8: Debug generate nonce endpoint
    print('8. Testing GET /debug/generate-nonce')
    try:
        response = requests.get(f'{base_url}/debug/generate-nonce', timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 200}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Nonce: {data.get("nonce", "N/A")}')
            print(f'   Expires in: {data.get("expires_in_seconds", "N/A")} seconds')
    except Exception as e:
        print(f'   Error: {e}')
    
    print()
    print('New endpoint testing complete!')
    print('=' * 50)

if __name__ == "__main__":
    test_new_endpoints()