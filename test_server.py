import requests
import json

def test_endpoints():
    # Test the endpoints
    base_url = 'http://localhost:8080'

    print('Testing integrated Nyaya backend endpoints...')
    print('=' * 50)

    # Test 1: Root endpoint
    print('1. Testing GET /')
    try:
        response = requests.get(f'{base_url}/', timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 200}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Service: {data.get("service", "N/A")}')
            print(f'   Version: {data.get("version", "N/A")}')
            print(f'   Has trace_id: {"trace_id" in data}')
    except Exception as e:
        print(f'   Error: {e}')

    print()

    # Test 2: Health endpoint
    print('2. Testing GET /health')
    try:
        response = requests.get(f'{base_url}/health', timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 200}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Status: {data.get("status", "N/A")}')
            print(f'   Has trace_id: {"trace_id" in data}')
    except Exception as e:
        print(f'   Error: {e}')

    print()

    # Test 3: Legal query endpoint
    print('3. Testing POST /api/legal/query')
    try:
        payload = {
            'query': 'What are my property rights?',
            'jurisdiction_hint': 'IN',
            'domain_hint': 'CIVIL'
        }
        response = requests.post(f'{base_url}/api/legal/query', json=payload, timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code in [200, 400]}')  # 400 is also valid for validation errors
        if response.status_code in [200, 400, 403, 500]:
            data = response.json()
            print(f'   Has trace_id: {"trace_id" in data}')
            if response.status_code == 200:
                print(f'   Has required fields: {"confidence" in data and "legal_route" in data}')
    except Exception as e:
        print(f'   Error: {e}')

    print()

    # Test 4: Nyaya query endpoint
    print('4. Testing POST /nyaya/query')
    try:
        payload = {
            'query': 'What legal remedies are available?',
            'jurisdiction_hint': 'IN',
            'domain_hint': 'CIVIL'
        }
        response = requests.post(f'{base_url}/nyaya/query', json=payload, timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code in [200, 400]}')
        if response.status_code in [200, 400, 403, 500]:
            data = response.json()
            print(f'   Has trace_id: {"trace_id" in data}')
            if response.status_code == 200:
                print(f'   Has required fields: {"confidence" in data and "legal_route" in data}')
    except Exception as e:
        print(f'   Error: {e}')

    print()

    # Test 5: Multi-jurisdiction endpoint
    print('5. Testing POST /nyaya/multi_jurisdiction')
    try:
        payload = {
            'query': 'Compare property laws',
            'jurisdictions': ['IN', 'US']
        }
        response = requests.post(f'{base_url}/nyaya/multi_jurisdiction', json=payload, timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code in [200, 400]}')
        if response.status_code in [200, 400, 403, 500]:
            data = response.json()
            print(f'   Has trace_id: {"trace_id" in data}')
            if response.status_code == 200:
                print(f'   Has comparative_analysis: {"comparative_analysis" in data}')
    except Exception as e:
        print(f'   Error: {e}')

    print()

    # Test 6: Trace endpoint
    print('6. Testing GET /nyaya/trace/test123')
    try:
        response = requests.get(f'{base_url}/nyaya/trace/test123', timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 200}')
        if response.status_code in [200, 404]:
            data = response.json()
            print(f'   Has trace_id: {"trace_id" in data}')
            if response.status_code == 200:
                print(f'   Has provenance_chain: {"provenance_chain" in data}')
    except Exception as e:
        print(f'   Error: {e}')

    print()

    # Test 7: Non-existent endpoint (should return 200, not 500)
    print('7. Testing GET /nonexistent (should not return 500)')
    try:
        response = requests.get(f'{base_url}/nonexistent', timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code != 500}')  # Main thing is no 500
        if response.status_code != 500:
            data = response.json()
            print(f'   Has trace_id: {"trace_id" in data}')
    except Exception as e:
        print(f'   Error: {e}')

    print()
    print('Endpoint testing complete!')
    print('=' * 50)

if __name__ == "__main__":
    test_endpoints()