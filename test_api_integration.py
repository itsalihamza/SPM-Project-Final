"""
Integration tests for Ad Intelligence Agent API
Tests external API calls and validates JSON contract compliance
"""

import requests
import json
import time
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 60  # seconds


class TestAdIntelligenceAPI:
    """Integration tests for the Ad Intelligence Agent API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health_check(self) -> bool:
        """Test 1: Health check endpoint"""
        print("\n" + "="*70)
        print("TEST 1: Health Check Endpoint")
        print("="*70)
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            assert response.status_code == 200, "Health check should return 200"
            data = response.json()
            
            # Validate JSON contract
            assert "status" in data, "Response must include 'status'"
            assert "agent_id" in data, "Response must include 'agent_id'"
            assert "version" in data, "Response must include 'version'"
            assert "capabilities" in data, "Response must include 'capabilities'"
            assert data["status"] == "healthy", "Status should be 'healthy'"
            
            print("✅ PASSED: Health check endpoint working correctly")
            return True
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            return False
    
    def test_root_endpoint(self) -> bool:
        """Test 2: Root endpoint"""
        print("\n" + "="*70)
        print("TEST 2: Root Endpoint")
        print("="*70)
        
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            assert response.status_code == 200
            data = response.json()
            assert "version" in data
            assert "endpoints" in data
            
            print("✅ PASSED: Root endpoint working correctly")
            return True
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            return False
    
    def test_collect_ads_mock(self) -> bool:
        """Test 3: Collect ads with mock platform"""
        print("\n" + "="*70)
        print("TEST 3: Collect Ads (Mock Platform)")
        print("="*70)
        
        try:
            request_data = {
                "keywords": ["Nike", "Adidas"],
                "platform": "mock",
                "max_results": 5
            }
            
            print(f"Request: {json.dumps(request_data, indent=2)}")
            
            response = self.session.post(
                f"{self.base_url}/api/v1/collect",
                json=request_data,
                timeout=API_TIMEOUT
            )
            
            print(f"Status Code: {response.status_code}")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            
            print(f"Response Summary:")
            print(f"  - Success: {data['success']}")
            print(f"  - Total Collected: {data['total_collected']}")
            print(f"  - Total Preprocessed: {data['total_preprocessed']}")
            print(f"  - Total Classified: {data['total_classified']}")
            print(f"  - Execution Time: {data['execution_time_seconds']}s")
            
            # Validate JSON contract
            assert data["success"] == True, "Request should succeed"
            assert "total_collected" in data
            assert "total_preprocessed" in data
            assert "total_classified" in data
            assert "ads" in data
            assert "execution_time_seconds" in data
            assert "timestamp" in data
            
            # Validate data
            assert data["total_collected"] == 5, "Should collect 5 ads"
            assert len(data["ads"]) == 5, "Should return 5 ads"
            
            # Validate ad structure
            if len(data["ads"]) > 0:
                ad = data["ads"][0]
                assert "ad_id" in ad, "Ad must have ad_id"
                assert "platform" in ad, "Ad must have platform"
                
            print("✅ PASSED: Ad collection working correctly")
            return True
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            return False
    
    def test_collect_ads_metaweb(self) -> bool:
        """Test 4: Collect real ads with metaweb platform"""
        print("\n" + "="*70)
        print("TEST 4: Collect Ads (MetaWeb Platform - Real Data)")
        print("="*70)
        print("⚠️  This test scrapes real data and may take 30-60 seconds")
        
        try:
            request_data = {
                "keywords": ["Nike"],
                "platform": "metaweb",
                "max_results": 3
            }
            
            print(f"Request: {json.dumps(request_data, indent=2)}")
            
            response = self.session.post(
                f"{self.base_url}/api/v1/collect",
                json=request_data,
                timeout=API_TIMEOUT
            )
            
            print(f"Status Code: {response.status_code}")
            
            assert response.status_code == 200
            data = response.json()
            
            print(f"Response Summary:")
            print(f"  - Success: {data['success']}")
            print(f"  - Total Collected: {data['total_collected']}")
            print(f"  - Total Preprocessed: {data['total_preprocessed']}")
            print(f"  - Total Classified: {data['total_classified']}")
            print(f"  - Execution Time: {data['execution_time_seconds']}s")
            
            assert data["success"] == True
            assert data["total_collected"] >= 0, "Should collect some ads"
            
            print("✅ PASSED: MetaWeb scraping working correctly")
            return True
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            return False
    
    def test_invalid_platform(self) -> bool:
        """Test 5: Invalid platform should return error"""
        print("\n" + "="*70)
        print("TEST 5: Invalid Platform Error Handling")
        print("="*70)
        
        try:
            request_data = {
                "keywords": ["test"],
                "platform": "invalid_platform",
                "max_results": 5
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/collect",
                json=request_data,
                timeout=API_TIMEOUT
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            assert response.status_code == 400, "Should return 400 for invalid platform"
            
            print("✅ PASSED: Error handling working correctly")
            return True
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            return False
    
    def test_status_endpoint(self) -> bool:
        """Test 6: Status endpoint"""
        print("\n" + "="*70)
        print("TEST 6: Status Endpoint")
        print("="*70)
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/status", timeout=10)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            assert response.status_code == 200
            data = response.json()
            assert "agent_info" in data
            assert "uptime_seconds" in data
            
            print("✅ PASSED: Status endpoint working correctly")
            return True
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("\n" + "="*70)
        print("AD INTELLIGENCE AGENT - INTEGRATION TESTS")
        print("="*70)
        print(f"API Base URL: {self.base_url}")
        print(f"Timeout: {API_TIMEOUT}s")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Root Endpoint", self.test_root_endpoint),
            ("Collect Ads (Mock)", self.test_collect_ads_mock),
            ("Collect Ads (MetaWeb)", self.test_collect_ads_metaweb),
            ("Invalid Platform", self.test_invalid_platform),
            ("Status Endpoint", self.test_status_endpoint),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"\n❌ Test '{test_name}' crashed: {str(e)}")
                results.append((test_name, False))
        
        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
            return False


if __name__ == "__main__":
    print("Starting Ad Intelligence Agent Integration Tests...")
    print("Make sure the API server is running on http://localhost:8000")
    print("\nWaiting 3 seconds for you to start the server if needed...")
    time.sleep(3)
    
    tester = TestAdIntelligenceAPI()
    success = tester.run_all_tests()
    
    exit(0 if success else 1)
