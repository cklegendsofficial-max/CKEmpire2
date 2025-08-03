#!/usr/bin/env python3
"""
Test script for Finance Module
Tests ROI calculation, DCF modeling, A/B testing, and financial reports
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

class FinanceModuleTester:
    """Test class for Finance module"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    async def test_finance_health_check(self) -> Dict[str, Any]:
        """Test finance module health check"""
        try:
            logger.info("Testing finance health check...")
            response = self.session.get(f"{self.base_url}/api/v1/finance/health")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Finance health check passed: {data}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Finance health check failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Finance health check error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_calculate_roi(self) -> Dict[str, Any]:
        """Test ROI calculation"""
        try:
            logger.info("Testing ROI calculation...")
            
            payload = {
                "target_amount": 20000,
                "initial_investment": 6000,
                "time_period": 1.0
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/finance/roi",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ ROI calculation passed: {data['roi_percentage']:.2f}%")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ ROI calculation failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ ROI calculation error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_create_dcf_model(self) -> Dict[str, Any]:
        """Test DCF model creation"""
        try:
            logger.info("Testing DCF model creation...")
            
            payload = {
                "initial_investment": 6000,
                "target_revenue": 20000,
                "growth_rate": 0.15,
                "discount_rate": 0.10,
                "time_period": 5
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/finance/dcf",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ DCF model creation passed: NPV ${data['npv']:.2f}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ DCF model creation failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ DCF model creation error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_run_ab_test(self) -> Dict[str, Any]:
        """Test A/B test analysis"""
        try:
            logger.info("Testing A/B test analysis...")
            
            payload = {
                "variant_a_data": {
                    "conversion_rate": 150,
                    "sample_size": 1000
                },
                "variant_b_data": {
                    "conversion_rate": 180,
                    "sample_size": 1000
                },
                "metric": "conversion_rate"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/finance/ab-test",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ A/B test passed: Winner {data['winner']}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ A/B test failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ A/B test error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_generate_financial_report(self) -> Dict[str, Any]:
        """Test financial report generation"""
        try:
            logger.info("Testing financial report generation...")
            
            payload = {
                "target_amount": 20000,
                "initial_investment": 6000
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/finance/report",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Financial report generation passed: {data['status']}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Financial report generation failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Financial report generation error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_calculate_break_even(self) -> Dict[str, Any]:
        """Test break-even calculation"""
        try:
            logger.info("Testing break-even calculation...")
            
            payload = {
                "fixed_costs": 5000,
                "variable_cost_per_unit": 50,
                "price_per_unit": 100
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/finance/break-even",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Break-even calculation passed: {data['break_even_units']:.0f} units")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Break-even calculation failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Break-even calculation error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_calculate_cash_flow(self) -> Dict[str, Any]:
        """Test cash flow forecast"""
        try:
            logger.info("Testing cash flow forecast...")
            
            payload = {
                "initial_cash": 10000,
                "monthly_revenue": 2000,
                "monthly_expenses": 1500,
                "months": 12
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/finance/cash-flow",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Cash flow forecast passed: {len(data['forecast'])} months")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Cash flow forecast failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Cash flow forecast error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_calculate_financial_ratios(self) -> Dict[str, Any]:
        """Test financial ratios calculation"""
        try:
            logger.info("Testing financial ratios calculation...")
            
            payload = {
                "revenue": 100000,
                "expenses": 70000,
                "assets": 150000,
                "liabilities": 50000,
                "equity": 100000
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/finance/ratios",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Financial ratios calculation passed: {data['profit_margin']:.2f}% margin")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Financial ratios calculation failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Financial ratios calculation error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_get_finance_metrics(self) -> Dict[str, Any]:
        """Test getting finance metrics"""
        try:
            logger.info("Testing get finance metrics...")
            
            response = self.session.get(f"{self.base_url}/api/v1/finance/metrics")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Get finance metrics passed: {data}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Get finance metrics failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Get finance metrics error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_finance_manager_direct(self) -> Dict[str, Any]:
        """Test finance manager directly"""
        try:
            logger.info("Testing finance manager directly...")
            
            # Import finance manager
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
            
            from finance import finance_manager
            
            # Test ROI calculation
            roi_calc = finance_manager.calculate_roi_for_target(
                target_amount=20000,
                initial_investment=6000,
                time_period=1.0
            )
            
            # Test DCF model creation
            dcf_model = finance_manager.create_dcf_model(
                initial_investment=6000,
                target_revenue=20000,
                growth_rate=0.15,
                discount_rate=0.10,
                time_period=5
            )
            
            # Test A/B test
            ab_result = finance_manager.run_ab_test(
                variant_a_data={"conversion_rate": 150, "sample_size": 1000},
                variant_b_data={"conversion_rate": 180, "sample_size": 1000},
                metric="conversion_rate"
            )
            
            # Test break-even analysis
            break_even = finance_manager.calculate_break_even_analysis(
                fixed_costs=5000,
                variable_cost_per_unit=50,
                price_per_unit=100
            )
            
            # Test cash flow forecast
            cash_flow = finance_manager.calculate_cash_flow_forecast(
                initial_cash=10000,
                monthly_revenue=2000,
                monthly_expenses=1500,
                months=12
            )
            
            # Test financial ratios
            ratios = finance_manager.calculate_financial_ratios(
                revenue=100000,
                expenses=70000,
                assets=150000,
                liabilities=50000,
                equity=100000
            )
            
            # Test financial report generation
            report = finance_manager.generate_financial_report(
                target_amount=20000,
                initial_investment=6000
            )
            
            logger.info("✅ Finance manager direct tests passed")
            return {
                "status": "passed",
                "data": {
                    "roi_percentage": roi_calc.calculate_roi(),
                    "dcf_npv": dcf_model.calculate_npv(),
                    "ab_winner": ab_result.winner,
                    "break_even_units": break_even["break_even_units"],
                    "cash_flow_months": len(cash_flow),
                    "profit_margin": ratios["profit_margin"],
                    "report_status": report["status"]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Finance manager direct test error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all finance tests"""
        logger.info("🚀 Starting Finance Module Tests")
        
        tests = [
            ("Finance Health Check", self.test_finance_health_check),
            ("Calculate ROI", self.test_calculate_roi),
            ("Create DCF Model", self.test_create_dcf_model),
            ("Run A/B Test", self.test_run_ab_test),
            ("Generate Financial Report", self.test_generate_financial_report),
            ("Calculate Break-Even", self.test_calculate_break_even),
            ("Calculate Cash Flow", self.test_calculate_cash_flow),
            ("Calculate Financial Ratios", self.test_calculate_financial_ratios),
            ("Get Finance Metrics", self.test_get_finance_metrics),
            ("Finance Manager Direct", self.test_finance_manager_direct)
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
        logger.info("📊 FINANCE MODULE TEST SUMMARY")
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
    tester = FinanceModuleTester()
    
    try:
        summary = await tester.run_all_tests()
        
        # Save results to file
        with open("finance_test_results.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info("💾 Test results saved to finance_test_results.json")
        
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