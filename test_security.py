import requests
import json

def test_security_and_errors():
    base_url = 'http://localhost:8080'

    print('Testing error scenarios and security features...')
    print('=' * 50)

    # Test 1: Empty query (should return 400)
    print('1. Testing POST /api/legal/query with empty query')
    try:
        payload = {'query': '', 'jurisdiction_hint': 'IN'}
        response = requests.post(f'{base_url}/api/legal/query', json=payload, timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 400}')  # Should be 400, not 500
        data = response.json()
        print(f'   Has trace_id: {"trace_id" in data}')
        print(f'   Has error message: {"error" in data}')
    except Exception as e:
        print(f'   Error: {e}')

    print()

    # Test 2: Missing query field (should return 400 or 403)
    print('2. Testing POST /api/legal/query with missing query')
    try:
        payload = {'jurisdiction_hint': 'IN'}
        response = requests.post(f'{base_url}/api/legal/query', json=payload, timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code in [400, 403]}')  # Should be validation error, not 500
        data = response.json()
        print(f'   Has trace_id: {"trace_id" in data}')
    except Exception as e:
        print(f'   Error: {e}')

    print()

    # Test 3: Dangerous content (should return 403, not 500)
    print('3. Testing POST /api/legal/query with dangerous content')
    try:
        payload = {'query': 'exec(import os)', 'jurisdiction_hint': 'IN'}
        response = requests.post(f'{base_url}/api/legal/query', json=payload, timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 403}')  # Should be 403, not 500
        data = response.json()
        print(f'   Has trace_id: {"trace_id" in data}')
        print(f'   Is safety rejection: {data.get("status") == "safety_rejected"}')
    except Exception as e:
        print(f'   Error: {e}')

    print()

    # Test 4: SQL injection attempt (should return 403, not 500)
    print('4. Testing POST /api/legal/query with SQL injection')
    try:
        payload = {'query': 'DROP TABLE users; SELECT * FROM accounts', 'jurisdiction_hint': 'IN'}
        response = requests.post(f'{base_url}/api/legal/query', json=payload, timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 403}')  # Should be 403, not 500
        data = response.json()
        print(f'   Has trace_id: {"trace_id" in data}')
        print(f'   Is safety rejection: {"safety_rejected" in str(data.get("status", ""))}')
    except Exception as e:
        print(f'   Error: {e}')

    print()

    # Test 5: Valid request should still work
    print('5. Testing POST /api/legal/query with valid query')
    try:
        payload = {'query': 'What are my legal rights?', 'jurisdiction_hint': 'IN', 'domain_hint': 'CIVIL'}
        response = requests.post(f'{base_url}/api/legal/query', json=payload, timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 200}')  # Should be 200
        data = response.json()
        print(f'   Has trace_id: {"trace_id" in data}')
        print(f'   Has confidence: {"confidence" in data}')
        print(f'   Has legal_route: {"legal_route" in data}')
        print(f'   Has enforcement_metadata: {"enforcement_metadata" in data}')
    except Exception as e:
        print(f'   Error: {e}')

    print()
    print('Security and error handling tests complete!')
    print('=' * 50)

if __name__ == "__main__":
    test_security_and_errors()