"""
Endpoint Testing Script
Tests all API endpoints and fixes issues
"""
import asyncio
import httpx
import json
from datetime import datetime

async def test_all_endpoints():
    """Test all endpoints and identify issues"""
    
    base_url = "http://localhost:8001"
    
    print("TESTING ALL ENDPOINTS")
    print("=" * 40)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Root endpoint
        print("\n1. Testing Root Endpoint...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Integration Status: {data.get('integration_status', {})}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Failed: {e}")
        
        # Test 2: Health endpoint
        print("\n2. Testing Health Endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   System Status: {data.get('status')}")
                print(f"   Components: {data.get('integration_status', {})}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Failed: {e}")
        
        # Test 3: Legal Query endpoint
        print("\n3. Testing Legal Query Endpoint...")
        try:
            query_data = {
                "query": "What is the procedure for filing a divorce case in India?",
                "jurisdiction_hint": "IN",
                "domain_hint": "FAMILY"
            }
            response = await client.post(f"{base_url}/api/legal/query", json=query_data)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Trace ID: {data.get('trace_id', 'Missing')}")
                print(f"   Domain: {data.get('domain', 'Missing')}")
                print(f"   Jurisdiction: {data.get('jurisdiction', 'Missing')}")
                print(f"   Confidence: {data.get('confidence', 'Missing')}")
                print(f"   Enforcement: {'Present' if 'enforcement_metadata' in data else 'Missing'}")
                
                # Save trace_id for feedback test
                global test_trace_id
                test_trace_id = data.get('trace_id')
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Failed: {e}")
        
        # Test 4: Feedback endpoint
        print("\n4. Testing Feedback Endpoint...")
        try:
            if 'test_trace_id' in globals():
                feedback_data = {
                    "trace_id": test_trace_id,
                    "rating": 4,
                    "feedback_type": "accuracy",
                    "comment": "Test feedback"
                }
                response = await client.post(f"{base_url}/api/feedback", json=feedback_data)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Feedback Status: {data.get('status')}")
                    print(f"   Message: {data.get('message')}")
                else:
                    print(f"   Error: {response.text}")
            else:
                print("   Skipped: No trace_id from legal query")
        except Exception as e:
            print(f"   Failed: {e}")
        
        # Test 5: Assistant endpoint
        print("\n5. Testing Assistant Endpoint...")
        try:
            assistant_data = {
                "message": "Hello, I need legal help",
                "payload": {"type": "legal_query"}
            }
            response = await client.post(f"{base_url}/api/assistant", json=assistant_data)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {data}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_all_endpoints())