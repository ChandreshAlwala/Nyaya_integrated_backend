import requests
import json

def test_webhooks():
    base_url = 'http://localhost:8080'

    print('Testing webhook functionality...')
    print('=' * 30)

    # Test webhook endpoints
    print('1. Testing GET /webhook (challenge verification)')
    try:
        response = requests.get(f'{base_url}/webhook?hub.challenge=12345', timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 200}')
        print(f'   Response text: {response.text}')
    except Exception as e:
        print(f'   Error: {e}')

    print()

    print('2. Testing POST /webhook (normal webhook)')
    try:
        payload = {'event': 'test_event', 'data': {'message': 'test'}}
        response = requests.post(f'{base_url}/webhook', json=payload, timeout=5)
        print(f'   Status: {response.status_code}')
        print(f'   Success: {response.status_code == 200}')
        data = response.json()
        print(f'   Has trace_id: {"trace_id" in data}')
        print(f'   Status: {data.get("status")}')
    except Exception as e:
        print(f'   Error: {e}')

    print()

    print('Webhook functionality tests complete!')
    print('=' * 30)

if __name__ == "__main__":
    test_webhooks()