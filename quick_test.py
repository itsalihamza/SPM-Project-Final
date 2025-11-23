"""
Quick test script to verify the API is working
"""

import requests
import json

API_URL = "http://localhost:8000"

print("="*70)
print("QUICK API TEST")
print("="*70)

# Test 1: Health Check
print("\n1. Testing Health Check...")
try:
    response = requests.get(f"{API_URL}/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    print("   ✅ PASSED")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 2: Collect Ads (Mock)
print("\n2. Testing Ad Collection (Mock Platform)...")
try:
    response = requests.post(
        f"{API_URL}/api/v1/collect",
        json={
            "keywords": ["Nike"],
            "platform": "mock",
            "max_results": 3
        },
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Collected: {data['total_collected']} ads")
    print(f"   Execution Time: {data['execution_time_seconds']}s")
    print("   ✅ PASSED")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

print("\n" + "="*70)
print("API is working! ✅")
print("="*70)
print("\nNext steps:")
print("1. Run full integration tests: python test_api_integration.py")
print("2. View API docs: http://localhost:8000/docs")
print("3. Test with real data: Change platform to 'metaweb'")
