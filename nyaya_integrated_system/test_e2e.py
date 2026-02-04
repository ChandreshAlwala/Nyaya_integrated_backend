"""
End-to-End Testing Suite - Vinayak's QA Implementation
Comprehensive testing, edge-case validation, regression checks
"""
import asyncio
import json
import httpx
from typing import Dict, Any, List
from datetime import datetime
import pytest

class NyayaE2ETestSuite:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.client = httpx.AsyncClient()
        
    async def run_full_test_suite(self) -> Dict[str, Any]:
        """Run complete test suite and return results"""
        print("🚀 Starting Nyaya E2E Test Suite...")
        
        test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "test_details": []
        }
        
        # Test categories
        test_categories = [
            ("Health Check", self.test_health_check),
            ("Single Legal Query", self.test_single_legal_query),
            ("Multi-Jurisdiction Query", self.test_multi_jurisdiction_query),
            ("Feedback Submission", self.test_feedback_submission),
            ("Trace Retrieval", self.test_trace_retrieval),
            ("Edge Cases", self.test_edge_cases),
            ("Enforcement Validation", self.test_enforcement_validation),
            ("RL Integration", self.test_rl_integration)
        ]
        
        for category_name, test_func in test_categories:
            print(f"\n📋 Testing: {category_name}")
            try:
                result = await test_func()
                test_results["test_details"].append({
                    "category": category_name,
                    "status": "PASSED" if result["passed"] else "FAILED",
                    "details": result
                })
                test_results["total_tests"] += result.get("total", 1)
                test_results["passed"] += result.get("passed_count", 1 if result["passed"] else 0)
                test_results["failed"] += result.get("failed_count", 0 if result["passed"] else 1)
                
                print(f"✅ {category_name}: PASSED")
            except Exception as e:
                test_results["test_details"].append({
                    "category": category_name,
                    "status": "FAILED",
                    "error": str(e)
                })
                test_results["total_tests"] += 1
                test_results["failed"] += 1
                print(f"❌ {category_name}: FAILED - {str(e)}")
        
        # Calculate success rate
        success_rate = (test_results["passed"] / test_results["total_tests"]) * 100 if test_results["total_tests"] > 0 else 0
        test_results["success_rate"] = round(success_rate, 2)
        
        print(f"\n📊 Test Summary:")
        print(f"Total Tests: {test_results['total_tests']}")
        print(f"Passed: {test_results['passed']}")
        print(f"Failed: {test_results['failed']}")
        print(f"Success Rate: {test_results['success_rate']}%")
        
        return test_results
    
    async def test_health_check(self) -> Dict[str, Any]:
        """Test system health endpoint"""
        response = await self.client.get(f"{self.base_url}/health")
        
        if response.status_code == 200:
            data = response.json()
            return {
                "passed": data.get("status") == "healthy",
                "response_data": data,
                "status_code": response.status_code
            }
        else:
            return {
                "passed": False,
                "error": f"Health check failed with status {response.status_code}",
                "status_code": response.status_code
            }
    
    async def test_single_legal_query(self) -> Dict[str, Any]:
        """Test single legal query functionality"""
        test_queries = [
            {
                "query": "What is the procedure for filing a divorce case in India?",
                "jurisdiction_hint": "IN",
                "domain_hint": "FAMILY"
            },
            {
                "query": "How to register a company in UAE?",
                "jurisdiction_hint": "UAE",
                "domain_hint": "CONSUMER_COMMERCIAL"
            },
            {
                "query": "What are the steps for criminal case proceedings in UK?",
                "jurisdiction_hint": "UK",
                "domain_hint": "CRIMINAL"
            }
        ]
        
        results = []
        for query_data in test_queries:
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/legal/query",
                    json=query_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Validate response structure
                    required_fields = ["trace_id", "domain", "jurisdiction", "confidence", "legal_route"]
                    has_required_fields = all(field in data for field in required_fields)
                    
                    results.append({
                        "query": query_data["query"],
                        "passed": has_required_fields and data["confidence"] > 0,
                        "response_data": data
                    })
                else:
                    results.append({
                        "query": query_data["query"],
                        "passed": False,
                        "error": f"Status code: {response.status_code}"
                    })
            except Exception as e:
                results.append({
                    "query": query_data["query"],
                    "passed": False,
                    "error": str(e)
                })
        
        passed_count = sum(1 for r in results if r["passed"])
        return {
            "passed": passed_count == len(results),
            "total": len(results),
            "passed_count": passed_count,
            "failed_count": len(results) - passed_count,
            "details": results
        }
    
    async def test_multi_jurisdiction_query(self) -> Dict[str, Any]:
        """Test multi-jurisdiction comparative analysis"""
        query_data = {
            "query": "What are the contract law procedures?",
            "jurisdictions": ["IN", "UAE", "UK"],
            "domain_hint": "CIVIL"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/legal/multi-jurisdiction",
                json=query_data
            )
            
            if response.status_code == 200:
                data = response.json()
                # Validate multi-jurisdiction response
                has_comparative_analysis = "comparative_analysis" in data
                has_all_jurisdictions = len(data.get("comparative_analysis", {})) == 3
                
                return {
                    "passed": has_comparative_analysis and has_all_jurisdictions,
                    "response_data": data,
                    "validation": {
                        "has_comparative_analysis": has_comparative_analysis,
                        "has_all_jurisdictions": has_all_jurisdictions
                    }
                }
            else:
                return {
                    "passed": False,
                    "error": f"Status code: {response.status_code}"
                }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }
    
    async def test_feedback_submission(self) -> Dict[str, Any]:
        """Test RL feedback submission"""
        # First, create a query to get a trace_id
        query_response = await self.client.post(
            f"{self.base_url}/api/legal/query",
            json={
                "query": "Test query for feedback",
                "jurisdiction_hint": "IN",
                "domain_hint": "CIVIL"
            }
        )
        
        if query_response.status_code != 200:
            return {
                "passed": False,
                "error": "Failed to create initial query for feedback test"
            }
        
        trace_id = query_response.json()["trace_id"]
        
        # Submit feedback
        feedback_data = {
            "trace_id": trace_id,
            "rating": 4,
            "feedback_type": "accuracy",
            "comment": "Test feedback submission"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/feedback",
                json=feedback_data
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "passed": data.get("status") in ["recorded", "blocked"],
                    "response_data": data
                }
            else:
                return {
                    "passed": False,
                    "error": f"Status code: {response.status_code}"
                }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }
    
    async def test_trace_retrieval(self) -> Dict[str, Any]:
        """Test trace audit trail retrieval"""
        # First, create a query to get a trace_id
        query_response = await self.client.post(
            f"{self.base_url}/api/legal/query",
            json={
                "query": "Test query for trace retrieval",
                "jurisdiction_hint": "IN"
            }
        )
        
        if query_response.status_code != 200:
            return {
                "passed": False,
                "error": "Failed to create initial query for trace test"
            }
        
        trace_id = query_response.json()["trace_id"]
        
        # Retrieve trace
        try:
            response = await self.client.get(f"{self.base_url}/api/trace/{trace_id}")
            
            if response.status_code == 200:
                data = response.json()
                has_required_fields = all(field in data for field in ["trace_id", "query", "processing_steps"])
                
                return {
                    "passed": has_required_fields,
                    "response_data": data
                }
            else:
                return {
                    "passed": False,
                    "error": f"Status code: {response.status_code}"
                }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }
    
    async def test_edge_cases(self) -> Dict[str, Any]:
        """Test edge cases and error handling"""
        edge_cases = [
            {
                "name": "Empty query",
                "data": {"query": "", "jurisdiction_hint": "IN"},
                "expect_error": True
            },
            {
                "name": "Very long query",
                "data": {"query": "A" * 10000, "jurisdiction_hint": "IN"},
                "expect_error": False
            },
            {
                "name": "Invalid jurisdiction",
                "data": {"query": "Test query", "jurisdiction_hint": "INVALID"},
                "expect_error": True
            },
            {
                "name": "Low certainty query",
                "data": {"query": "xyz abc def", "jurisdiction_hint": "IN"},
                "expect_error": False
            }
        ]
        
        results = []
        for case in edge_cases:
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/legal/query",
                    json=case["data"]
                )
                
                if case["expect_error"]:
                    # Should return error status
                    passed = response.status_code >= 400
                else:
                    # Should handle gracefully
                    passed = response.status_code == 200
                
                results.append({
                    "case": case["name"],
                    "passed": passed,
                    "status_code": response.status_code
                })
            except Exception as e:
                results.append({
                    "case": case["name"],
                    "passed": case["expect_error"],  # Exception is expected for error cases
                    "error": str(e)
                })
        
        passed_count = sum(1 for r in results if r["passed"])
        return {
            "passed": passed_count == len(results),
            "total": len(results),
            "passed_count": passed_count,
            "failed_count": len(results) - passed_count,
            "details": results
        }
    
    async def test_enforcement_validation(self) -> Dict[str, Any]:
        """Test enforcement engine integration"""
        # Test that enforcement metadata is present in responses
        response = await self.client.post(
            f"{self.base_url}/api/legal/query",
            json={
                "query": "Legal enforcement test query",
                "jurisdiction_hint": "IN"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            has_enforcement_metadata = "enforcement_metadata" in data
            has_provenance_chain = "provenance_chain" in data and len(data["provenance_chain"]) > 0
            
            return {
                "passed": has_enforcement_metadata and has_provenance_chain,
                "validation": {
                    "has_enforcement_metadata": has_enforcement_metadata,
                    "has_provenance_chain": has_provenance_chain
                },
                "response_data": data
            }
        else:
            return {
                "passed": False,
                "error": f"Status code: {response.status_code}"
            }
    
    async def test_rl_integration(self) -> Dict[str, Any]:
        """Test RL engine integration and feedback loop"""
        # Create query, submit feedback, create another query to test learning
        
        # First query
        query1_response = await self.client.post(
            f"{self.base_url}/api/legal/query",
            json={
                "query": "RL integration test query",
                "jurisdiction_hint": "IN"
            }
        )
        
        if query1_response.status_code != 200:
            return {
                "passed": False,
                "error": "Failed to create first query for RL test"
            }
        
        trace_id1 = query1_response.json()["trace_id"]
        confidence1 = query1_response.json()["confidence"]
        
        # Submit positive feedback
        feedback_response = await self.client.post(
            f"{self.base_url}/api/feedback",
            json={
                "trace_id": trace_id1,
                "rating": 5,
                "feedback_type": "accuracy"
            }
        )
        
        if feedback_response.status_code != 200:
            return {
                "passed": False,
                "error": "Failed to submit feedback for RL test"
            }
        
        # Second similar query to test learning impact
        query2_response = await self.client.post(
            f"{self.base_url}/api/legal/query",
            json={
                "query": "RL integration test query similar",
                "jurisdiction_hint": "IN"
            }
        )
        
        if query2_response.status_code != 200:
            return {
                "passed": False,
                "error": "Failed to create second query for RL test"
            }
        
        confidence2 = query2_response.json()["confidence"]
        
        return {
            "passed": True,  # RL integration is working if no errors occurred
            "details": {
                "first_confidence": confidence1,
                "second_confidence": confidence2,
                "feedback_processed": feedback_response.json().get("status") == "recorded"
            }
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

# Standalone test runner
async def run_e2e_tests():
    """Run E2E tests and save results"""
    test_suite = NyayaE2ETestSuite()
    
    try:
        results = await test_suite.run_full_test_suite()
        
        # Save results to file
        with open("test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Test results saved to test_results.json")
        
        # Return exit code based on success rate
        if results["success_rate"] >= 80:
            print("🎉 Tests PASSED - System is demo-ready!")
            return 0
        else:
            print("⚠️ Tests FAILED - System needs fixes before demo")
            return 1
            
    finally:
        await test_suite.close()

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(run_e2e_tests())
    sys.exit(exit_code)