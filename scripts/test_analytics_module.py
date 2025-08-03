#!/usr/bin/env python3
"""
Test script for Analytics Module
Tests user metrics tracking, A/B testing, GA integration, and data-driven decisions
"""

import asyncio
import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsModuleTester:
    """Test class for Analytics module"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    async def test_analytics_health_check(self) -> Dict[str, Any]:
        """Test analytics module health check"""
        try:
            logger.info("Testing analytics health check...")
            response = self.session.get(f"{self.base_url}/api/v1/analytics/health")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Analytics health check passed: {data}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Analytics health check failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Analytics health check error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_track_user_metrics(self) -> Dict[str, Any]:
        """Test user metrics tracking"""
        try:
            logger.info("Testing user metrics tracking...")
            
            payload = {
                "user_id": f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "session_duration": 1800.0,  # 30 minutes
                "page_views": 15,
                "conversion_rate": 0.05,  # 5%
                "revenue": 250.0
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analytics/track",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ User metrics tracking passed: {data['user_id']}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ User metrics tracking failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ User metrics tracking error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_get_user_metrics(self) -> Dict[str, Any]:
        """Test getting user metrics"""
        try:
            logger.info("Testing get user metrics...")
            
            # First track a metric
            user_id = f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            track_payload = {
                "user_id": user_id,
                "session_duration": 1200.0,
                "page_views": 10,
                "conversion_rate": 0.03,
                "revenue": 150.0
            }
            
            self.session.post(f"{self.base_url}/api/v1/analytics/track", json=track_payload)
            
            # Then get the metrics
            response = self.session.get(f"{self.base_url}/api/v1/analytics/metrics/{user_id}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Get user metrics passed: {data['user_id']}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Get user metrics failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Get user metrics error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_get_all_user_metrics(self) -> Dict[str, Any]:
        """Test getting all user metrics"""
        try:
            logger.info("Testing get all user metrics...")
            
            response = self.session.get(f"{self.base_url}/api/v1/analytics/metrics")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Get all user metrics passed: {len(data)} metrics")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Get all user metrics failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Get all user metrics error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_run_ab_test(self) -> Dict[str, Any]:
        """Test A/B test analysis"""
        try:
            logger.info("Testing A/B test analysis...")
            
            payload = {
                "test_id": f"ab_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "variant_a_data": {
                    "conversion_rate": 120,
                    "sample_size": 1000
                },
                "variant_b_data": {
                    "conversion_rate": 150,
                    "sample_size": 1000
                },
                "metric": "conversion_rate"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analytics/ab-test",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ A/B test analysis passed: Winner {data['winner']}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ A/B test analysis failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ A/B test analysis error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_get_all_ab_tests(self) -> Dict[str, Any]:
        """Test getting all A/B test results"""
        try:
            logger.info("Testing get all A/B test results...")
            
            response = self.session.get(f"{self.base_url}/api/v1/analytics/ab-tests")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Get all A/B test results passed: {len(data)} tests")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Get all A/B test results failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Get all A/B test results error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_generate_analytics_report(self) -> Dict[str, Any]:
        """Test analytics report generation"""
        try:
            logger.info("Testing analytics report generation...")
            
            response = self.session.post(f"{self.base_url}/api/v1/analytics/report")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Analytics report generation passed: {data['total_users']} users")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Analytics report generation failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Analytics report generation error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_get_all_analytics_reports(self) -> Dict[str, Any]:
        """Test getting all analytics reports"""
        try:
            logger.info("Testing get all analytics reports...")
            
            response = self.session.get(f"{self.base_url}/api/v1/analytics/reports")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Get all analytics reports passed: {len(data)} reports")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Get all analytics reports failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Get all analytics reports error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_ga_integration(self) -> Dict[str, Any]:
        """Test Google Analytics integration"""
        try:
            logger.info("Testing GA integration...")
            
            payload = {
                "property_id": "test_property_123",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "metrics": ["page_views", "unique_visitors", "conversion_rate"]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analytics/ga-integration",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ GA integration passed: {data['property_id']}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ GA integration failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ GA integration error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_make_data_driven_decision(self) -> Dict[str, Any]:
        """Test data-driven decision making"""
        try:
            logger.info("Testing data-driven decision making...")
            
            payload = {
                "category": "pricing",
                "data": {
                    "conversion_rate": 0.05,
                    "revenue": 5000,
                    "user_count": 1000
                },
                "confidence_threshold": 0.95
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analytics/decision",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Data-driven decision passed: {data['decision']}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Data-driven decision failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Data-driven decision error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_get_analytics_dashboard(self) -> Dict[str, Any]:
        """Test getting analytics dashboard data"""
        try:
            logger.info("Testing get analytics dashboard...")
            
            response = self.session.get(f"{self.base_url}/api/v1/analytics/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Get analytics dashboard passed: {data['status']}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Get analytics dashboard failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Get analytics dashboard error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_get_analytics_metrics(self) -> Dict[str, Any]:
        """Test getting analytics metrics summary"""
        try:
            logger.info("Testing get analytics metrics summary...")
            
            response = self.session.get(f"{self.base_url}/api/v1/analytics/metrics-summary")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Get analytics metrics summary passed: {data['total_users']} users")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Get analytics metrics summary failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Get analytics metrics summary error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_analytics_manager_direct(self) -> Dict[str, Any]:
        """Test analytics manager directly"""
        try:
            logger.info("Testing analytics manager directly...")
            
            # Import analytics manager
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
            
            from analytics import analytics_manager
            
            # Test user metrics tracking
            metric = analytics_manager.track_user_metric(
                user_id=f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                session_duration=1800.0,
                page_views=15,
                conversion_rate=0.05,
                revenue=250.0
            )
            
            # Test A/B test
            ab_result = analytics_manager.run_ab_test(
                test_id=f"ab_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                variant_a_data={"conversion_rate": 120, "sample_size": 1000},
                variant_b_data={"conversion_rate": 150, "sample_size": 1000},
                metric="conversion_rate"
            )
            
            # Test analytics report generation
            report = analytics_manager.generate_analytics_report()
            
            # Test data-driven decision
            decision = analytics_manager.make_data_driven_decision(
                category="pricing",
                data={"conversion_rate": 0.05, "revenue": 5000, "user_count": 1000},
                confidence_threshold=0.95
            )
            
            # Test dashboard data
            dashboard_data = analytics_manager.get_analytics_dashboard_data()
            
            logger.info("✅ Analytics manager direct tests passed")
            return {
                "status": "passed",
                "data": {
                    "user_metric_tracked": metric.user_id,
                    "ab_test_winner": ab_result.winner,
                    "report_total_users": report.total_users,
                    "decision_category": decision["category"],
                    "dashboard_status": dashboard_data["status"]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Analytics manager direct test error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all analytics tests"""
        logger.info("🚀 Starting Analytics Module Tests")
        
        tests = [
            ("Analytics Health Check", self.test_analytics_health_check),
            ("Track User Metrics", self.test_track_user_metrics),
            ("Get User Metrics", self.test_get_user_metrics),
            ("Get All User Metrics", self.test_get_all_user_metrics),
            ("Run A/B Test", self.test_run_ab_test),
            ("Get All A/B Tests", self.test_get_all_ab_tests),
            ("Generate Analytics Report", self.test_generate_analytics_report),
            ("Get All Analytics Reports", self.test_get_all_analytics_reports),
            ("GA Integration", self.test_ga_integration),
            ("Make Data-Driven Decision", self.test_make_data_driven_decision),
            ("Get Analytics Dashboard", self.test_get_analytics_dashboard),
            ("Get Analytics Metrics", self.test_get_analytics_metrics),
            ("Analytics Manager Direct", self.test_analytics_manager_direct)
        ]
        
        results = {}
        passed = 0
        failed = 0
        errors = 0
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*50}")
            logger.info(f"Running: {test_name}")
            logger.info(f"{'='*50}")
            
            result = await test_func()
            results[test_name] = result
            
            if result["status"] == "passed":
                passed += 1
            elif result["status"] == "failed":
                failed += 1
            else:
                errors += 1
        
        # Generate summary
        summary = {
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": (passed / len(tests)) * 100 if len(tests) > 0 else 0,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"\n{'='*60}")
        logger.info("📊 ANALYTICS MODULE TEST SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total Tests: {summary['total_tests']}")
        logger.info(f"✅ Passed: {summary['passed']}")
        logger.info(f"❌ Failed: {summary['failed']}")
        logger.info(f"⚠️  Errors: {summary['errors']}")
        logger.info(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"{'='*60}")
        
        return summary

async def main():
    """Main test function"""
    tester = AnalyticsModuleTester()
    
    try:
        summary = await tester.run_all_tests()
        
        # Save results to file
        with open("analytics_test_results.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info("💾 Test results saved to analytics_test_results.json")
        
        # Exit with appropriate code
        if summary["failed"] == 0 and summary["errors"] == 0:
            logger.info("🎉 All tests passed!")
            exit(0)
        else:
            logger.error("❌ Some tests failed!")
            exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"💥 Test execution failed: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 