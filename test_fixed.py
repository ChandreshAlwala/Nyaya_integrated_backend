"""
Test Fixed Legal Query Endpoint
"""
import asyncio
import httpx
import json

async def test_fixed_endpoint():
    """Test the fixed legal query endpoint"""
    
    base_url = "http://localhost:8002"
    
    print("Testing Fixed Legal Query Endpoint")
    print("=" * 40)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test legal query
        print("\nTesting Legal Query...")
        try:
            query_data = {
                "query": "What is the procedure for filing a divorce case in India?",
                "jurisdiction_hint": "IN",
                "domain_hint": "FAMILY"
            }
            response = await client.post(f"{base_url}/api/legal/query", json=query_data)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Trace ID: {data.get('trace_id')}")
                print(f"Domain: {data.get('domain')}")
                print(f"Jurisdiction: {data.get('jurisdiction')}")
                print(f"Confidence: {data.get('confidence')}")
                print(f"Message: {data.get('message')}")
                print("SUCCESS: Legal query endpoint working!")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_fixed_endpoint())