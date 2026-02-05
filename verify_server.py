import requests

try:
    response = requests.get('http://localhost:8000/', timeout=5)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Service: {data["service"]}')
        print(f'Version: {data["version"]}')
        print(f'Status: {data["status"]}')
    else:
        print(f'Error: Received status {response.status_code}')
except Exception as e:
    print(f'Connection error: {e}')