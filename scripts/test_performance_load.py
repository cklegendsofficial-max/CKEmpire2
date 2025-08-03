#!/usr/bin/env python3
"""
Performance Load Testing Script for CK Empire
Simulates high load scenarios and tests Redis cluster performance
"""

import asyncio
import aiohttp
import time
import json
import random
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any
import argparse
import sys
import os

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from performance import cache, metrics, get_performance_summary, analyze_performance

class PerformanceLoadTester:
    """Comprehensive performance load tester"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.results = {
            "start_time": None,
            "end_time": None,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "cache_performance": {},
            "load_scenarios": {},
            "errors": []
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"Content-Type": "application/json"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make a single HTTP request and record metrics"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    response_time = time.time() - start_time
                    success = response.status == 200
                    
                    return {
                        "method": method,
                        "endpoint": endpoint,
                        "status_code": response.status,
                        "response_time": response_time,
                        "success": success,
                        "error": None
                    }
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    response_time = time.time() - start_time
                    success = response.status in [200, 201]
                    
                    return {
                        "method": method,
                        "endpoint": endpoint,
                        "status_code": response.status,
                        "response_time": response_time,
                        "success": success,
                        "error": None
                    }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "method": method,
                "endpoint": endpoint,
                "status_code": 0,
                "response_time": response_time,
                "success": False,
                "error": str(e)
            }
    
    async def run_load_scenario(self, scenario_name: str, requests: List[Dict], 
                               concurrent_users: int = 10, duration: int = 60) -> Dict[str, Any]:
        """Run a specific load scenario"""
        print(f"🚀 Starting load scenario: {scenario_name}")
        print(f"   Concurrent users: {concurrent_users}")
        print(f"   Duration: {duration} seconds")
        
        scenario_results = {
            "name": scenario_name,
            "start_time": datetime.now(),
            "concurrent_users": concurrent_users,
            "duration": duration,
            "requests": [],
            "summary": {}
        }
        
        # Create tasks for concurrent users
        tasks = []
        for user_id in range(concurrent_users):
            task = self._user_worker(user_id, requests, duration)
            tasks.append(task)
        
        # Run all tasks concurrently
        user_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect all results
        for user_result in user_results:
            if isinstance(user_result, list):
                scenario_results["requests"].extend(user_result)
        
        # Calculate summary statistics
        response_times = [r["response_time"] for r in scenario_results["requests"]]
        successful_requests = [r for r in scenario_results["requests"] if r["success"]]
        failed_requests = [r for r in scenario_results["requests"] if not r["success"]]
        
        scenario_results["summary"] = {
            "total_requests": len(scenario_results["requests"]),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": len(successful_requests) / len(scenario_results["requests"]) * 100 if scenario_results["requests"] else 0,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "median_response_time": statistics.median(response_times) if response_times else 0,
            "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0,
            "p99_response_time": statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "requests_per_second": len(scenario_results["requests"]) / duration
        }
        
        print(f"✅ Completed load scenario: {scenario_name}")
        print(f"   Total requests: {scenario_results['summary']['total_requests']}")
        print(f"   Success rate: {scenario_results['summary']['success_rate']:.1f}%")
        print(f"   Avg response time: {scenario_results['summary']['avg_response_time']:.3f}s")
        print(f"   Requests/sec: {scenario_results['summary']['requests_per_second']:.1f}")
        
        return scenario_results
    
    async def _user_worker(self, user_id: int, requests: List[Dict], duration: int) -> List[Dict]:
        """Worker function for a single user"""
        user_results = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Randomly select a request from the list
            request_config = random.choice(requests)
            
            # Add some randomization to request data
            if request_config.get("data"):
                request_data = request_config["data"].copy()
                if "name" in request_data:
                    request_data["name"] = f"{request_data['name']}_{user_id}_{int(time.time())}"
                if "amount" in request_data:
                    request_data["amount"] = random.randint(100, 10000)
            else:
                request_data = None
            
            # Make the request
            result = await self.make_request(
                request_config["method"],
                request_config["endpoint"],
                request_data
            )
            
            user_results.append(result)
            
            # Add some delay between requests
            await asyncio.sleep(random.uniform(0.1, 0.5))
        
        return user_results
    
    async def test_cache_performance(self) -> Dict[str, Any]:
        """Test cache performance with repeated requests"""
        print("🧪 Testing cache performance...")
        
        cache_test_requests = [
            {"method": "GET", "endpoint": "/performance/cached-summary"},
            {"method": "GET", "endpoint": "/performance/health"},
            {"method": "GET", "endpoint": "/projects"},
            {"method": "GET", "endpoint": "/revenue"}
        ]
        
        # First run: populate cache
        print("   Populating cache...")
        for request in cache_test_requests:
            await self.make_request(request["method"], request["endpoint"])
        
        # Second run: test cache hits
        print("   Testing cache hits...")
        cache_hit_results = []
        for _ in range(20):
            request = random.choice(cache_test_requests)
            result = await self.make_request(request["method"], request["endpoint"])
            cache_hit_results.append(result)
        
        # Third run: test cache invalidation
        print("   Testing cache invalidation...")
        await self.make_request("DELETE", "/performance/clear-cache")
        
        cache_miss_results = []
        for _ in range(10):
            request = random.choice(cache_test_requests)
            result = await self.make_request(request["method"], request["endpoint"])
            cache_miss_results.append(result)
        
        # Calculate cache performance metrics
        cache_hit_times = [r["response_time"] for r in cache_hit_results]
        cache_miss_times = [r["response_time"] for r in cache_miss_results]
        
        cache_performance = {
            "cache_hit_avg_time": statistics.mean(cache_hit_times) if cache_hit_times else 0,
            "cache_miss_avg_time": statistics.mean(cache_miss_times) if cache_miss_times else 0,
            "cache_speedup": statistics.mean(cache_miss_times) / statistics.mean(cache_hit_times) if cache_hit_times and cache_miss_times and statistics.mean(cache_hit_times) > 0 else 0,
            "total_cache_tests": len(cache_hit_results) + len(cache_miss_results)
        }
        
        print(f"   Cache hit avg time: {cache_performance['cache_hit_avg_time']:.3f}s")
        print(f"   Cache miss avg time: {cache_performance['cache_miss_avg_time']:.3f}s")
        print(f"   Cache speedup: {cache_performance['cache_speedup']:.1f}x")
        
        return cache_performance
    
    async def run_comprehensive_load_test(self) -> Dict[str, Any]:
        """Run comprehensive load testing with multiple scenarios"""
        print("🚀 Starting comprehensive performance load test")
        self.results["start_time"] = datetime.now()
        
        # Define load scenarios
        scenarios = {
            "light_load": {
                "requests": [
                    {"method": "GET", "endpoint": "/health"},
                    {"method": "GET", "endpoint": "/metrics"},
                    {"method": "GET", "endpoint": "/projects"},
                    {"method": "GET", "endpoint": "/revenue"}
                ],
                "concurrent_users": 5,
                "duration": 30
            },
            "medium_load": {
                "requests": [
                    {"method": "GET", "endpoint": "/health"},
                    {"method": "GET", "endpoint": "/metrics"},
                    {"method": "GET", "endpoint": "/projects"},
                    {"method": "GET", "endpoint": "/revenue"},
                    {"method": "GET", "endpoint": "/performance/metrics"},
                    {"method": "POST", "endpoint": "/projects", "data": {"name": "Test Project", "description": "Load test", "status": "active"}},
                    {"method": "POST", "endpoint": "/revenue", "data": {"amount": 1000, "source": "test", "date": "2024-01-01"}}
                ],
                "concurrent_users": 15,
                "duration": 60
            },
            "high_load": {
                "requests": [
                    {"method": "GET", "endpoint": "/health"},
                    {"method": "GET", "endpoint": "/metrics"},
                    {"method": "GET", "endpoint": "/projects"},
                    {"method": "GET", "endpoint": "/revenue"},
                    {"method": "GET", "endpoint": "/performance/metrics"},
                    {"method": "GET", "endpoint": "/performance/cached-summary"},
                    {"method": "POST", "endpoint": "/projects", "data": {"name": "Test Project", "description": "Load test", "status": "active"}},
                    {"method": "POST", "endpoint": "/revenue", "data": {"amount": 1000, "source": "test", "date": "2024-01-01"}},
                    {"method": "POST", "endpoint": "/ethics/check", "data": {"content": "Test content", "content_type": "text", "user_id": "test"}},
                    {"method": "POST", "endpoint": "/ai/ideas", "data": {"topic": "technology", "style": "viral", "count": 3}}
                ],
                "concurrent_users": 30,
                "duration": 90
            },
            "extreme_load": {
                "requests": [
                    {"method": "GET", "endpoint": "/health"},
                    {"method": "GET", "endpoint": "/metrics"},
                    {"method": "GET", "endpoint": "/projects"},
                    {"method": "GET", "endpoint": "/revenue"},
                    {"method": "GET", "endpoint": "/performance/metrics"},
                    {"method": "GET", "endpoint": "/performance/cached-summary"},
                    {"method": "GET", "endpoint": "/performance/health"},
                    {"method": "POST", "endpoint": "/projects", "data": {"name": "Test Project", "description": "Load test", "status": "active"}},
                    {"method": "POST", "endpoint": "/revenue", "data": {"amount": 1000, "source": "test", "date": "2024-01-01"}},
                    {"method": "POST", "endpoint": "/ethics/check", "data": {"content": "Test content", "content_type": "text", "user_id": "test"}},
                    {"method": "POST", "endpoint": "/ai/ideas", "data": {"topic": "technology", "style": "viral", "count": 3}},
                    {"method": "DELETE", "endpoint": "/performance/clear-cache"}
                ],
                "concurrent_users": 50,
                "duration": 120
            }
        }
        
        # Run each scenario
        for scenario_name, scenario_config in scenarios.items():
            scenario_result = await self.run_load_scenario(
                scenario_name,
                scenario_config["requests"],
                scenario_config["concurrent_users"],
                scenario_config["duration"]
            )
            self.results["load_scenarios"][scenario_name] = scenario_result
        
        # Test cache performance
        self.results["cache_performance"] = await self.test_cache_performance()
        
        # Get performance summary
        performance_summary = get_performance_summary()
        self.results["performance_summary"] = performance_summary
        
        # Analyze performance
        performance_analysis = analyze_performance()
        self.results["performance_analysis"] = performance_analysis
        
        self.results["end_time"] = datetime.now()
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate a comprehensive performance report"""
        duration = (self.results["end_time"] - self.results["start_time"]).total_seconds()
        
        report = f"""
🚀 CK Empire Performance Load Test Report
{'='*50}

📊 Test Summary:
   Start Time: {self.results['start_time']}
   End Time: {self.results['end_time']}
   Total Duration: {duration:.1f} seconds

📈 Load Scenarios:
"""
        
        for scenario_name, scenario_result in self.results["load_scenarios"].items():
            summary = scenario_result["summary"]
            report += f"""
   {scenario_name.upper()}:
     - Total Requests: {summary['total_requests']}
     - Success Rate: {summary['success_rate']:.1f}%
     - Avg Response Time: {summary['avg_response_time']:.3f}s
     - P95 Response Time: {summary['p95_response_time']:.3f}s
     - Requests/sec: {summary['requests_per_second']:.1f}
"""
        
        if self.results["cache_performance"]:
            cache_perf = self.results["cache_performance"]
            report += f"""
🧪 Cache Performance:
   - Cache Hit Avg Time: {cache_perf['cache_hit_avg_time']:.3f}s
   - Cache Miss Avg Time: {cache_perf['cache_miss_avg_time']:.3f}s
   - Cache Speedup: {cache_perf['cache_speedup']:.1f}x
   - Total Cache Tests: {cache_perf['total_cache_tests']}
"""
        
        if "performance_summary" in self.results:
            perf_summary = self.results["performance_summary"]
            report += f"""
📊 Performance Summary:
   - Uptime: {perf_summary['uptime']:.1f}s
   - Total Queries: {perf_summary['total_queries']}
   - Avg Query Time: {perf_summary['average_query_time']:.3f}s
   - Redis Cache Hit Rate: {perf_summary['redis_cache_hit_rate']:.1f}%
   - LRU Cache Hit Rate: {perf_summary['lru_cache_hit_rate']:.1f}%
   - Performance Alerts: {perf_summary['performance_alerts']}
"""
        
        if "performance_analysis" in self.results:
            analysis = self.results["performance_analysis"]
            report += f"""
🔍 Performance Analysis:
   - Slow Queries: {len(analysis['slow_queries'])}
   - Recommendations: {len(analysis['recommendations'])}
   - Alerts: {len(analysis['alerts'])}
"""
        
        report += f"""
{'='*50}
✅ Performance load test completed successfully!
"""
        
        return report

async def main():
    """Main function to run the performance load test"""
    parser = argparse.ArgumentParser(description="CK Empire Performance Load Tester")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for the API")
    parser.add_argument("--output", help="Output file for the test results")
    parser.add_argument("--scenario", choices=["light", "medium", "high", "extreme", "all"], 
                       default="all", help="Specific load scenario to run")
    
    args = parser.parse_args()
    
    print("🚀 CK Empire Performance Load Tester")
    print(f"Target URL: {args.url}")
    print(f"Scenario: {args.scenario}")
    
    async with PerformanceLoadTester(args.url) as tester:
        try:
            results = await tester.run_comprehensive_load_test()
            
            # Generate and print report
            report = tester.generate_report()
            print(report)
            
            # Save results to file if specified
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                print(f"📄 Results saved to: {args.output}")
            
            # Determine if test passed
            total_requests = sum(s["summary"]["total_requests"] for s in results["load_scenarios"].values())
            avg_success_rate = sum(s["summary"]["success_rate"] for s in results["load_scenarios"].values()) / len(results["load_scenarios"])
            
            if avg_success_rate >= 95 and total_requests > 0:
                print("✅ Performance test PASSED")
                return 0
            else:
                print("❌ Performance test FAILED")
                return 1
                
        except Exception as e:
            print(f"❌ Performance test failed with error: {e}")
            return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 