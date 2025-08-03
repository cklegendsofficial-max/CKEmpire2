#!/usr/bin/env python3
"""
Test script for AI module with GPT fine-tuning and accuracy testing
Tests the enhanced AI module with mock dataset and accuracy assertions
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import AI module
try:
    from backend.ai import ai_module
    from backend.models import EmpireStrategyRequest, FinancialMetricsResponse
except ImportError as e:
    logger.error(f"Failed to import AI module: {e}")
    exit(1)

class AITestSuite:
    """Comprehensive test suite for AI module"""
    
    def __init__(self):
        self.test_results = []
        self.accuracy_threshold = 0.7  # 70% accuracy threshold
        
    async def test_custom_strategy_generation(self) -> Dict[str, Any]:
        """Test custom strategy generation with various inputs"""
        logger.info("🧪 Testing custom strategy generation...")
        
        test_cases = [
            {
                "input": "Düşük bütçe ile başla",
                "expected_type": "lean_startup",
                "description": "Turkish lean startup request"
            },
            {
                "input": "Revenue hedefi $50K",
                "expected_type": "scale_up", 
                "description": "Turkish revenue target request"
            },
            {
                "input": "Yüksek risk toleransı",
                "expected_type": "innovation",
                "description": "Turkish high risk tolerance request"
            },
            {
                "input": "Start with low budget",
                "expected_type": "lean_startup",
                "description": "English lean startup request"
            },
            {
                "input": "Technology focused growth",
                "expected_type": "innovation",
                "description": "English technology focus request"
            },
            {
                "input": "Cost optimization needed",
                "expected_type": "cost_optimization",
                "description": "English cost optimization request"
            }
        ]
        
        results = []
        for i, test_case in enumerate(test_cases):
            try:
                # Generate strategy
                strategy, financial_metrics = await ai_module.generate_custom_strategy(
                    test_case["input"], 
                    include_financial_metrics=True
                )
                
                # Check if strategy type matches expected
                type_match = strategy.strategy_type.value == test_case["expected_type"]
                
                # Validate financial metrics
                metrics_valid = self._validate_financial_metrics(financial_metrics)
                
                result = {
                    "test_case": i + 1,
                    "input": test_case["input"],
                    "expected_type": test_case["expected_type"],
                    "actual_type": strategy.strategy_type.value,
                    "type_match": type_match,
                    "metrics_valid": metrics_valid,
                    "strategy_title": strategy.title,
                    "estimated_investment": strategy.estimated_investment,
                    "projected_roi": strategy.projected_roi,
                    "success": type_match and metrics_valid
                }
                
                results.append(result)
                logger.info(f"✅ Test case {i+1}: {test_case['description']} - {'PASS' if result['success'] else 'FAIL'}")
                
            except Exception as e:
                logger.error(f"❌ Test case {i+1} failed: {e}")
                results.append({
                    "test_case": i + 1,
                    "input": test_case["input"],
                    "error": str(e),
                    "success": False
                })
        
        return {
            "test_name": "custom_strategy_generation",
            "total_tests": len(test_cases),
            "passed_tests": sum(1 for r in results if r.get("success", False)),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _validate_financial_metrics(self, metrics: FinancialMetricsResponse) -> bool:
        """Validate financial metrics are reasonable"""
        if not metrics:
            return False
        
        try:
            # Check NPV is reasonable
            if metrics.npv < -1000000 or metrics.npv > 10000000:
                return False
            
            # Check ROI is reasonable (0-100%)
            if metrics.roi_percentage < 0 or metrics.roi_percentage > 100:
                return False
            
            # Check payback period is reasonable (1-60 months)
            if metrics.payback_period < 1 or metrics.payback_period > 60:
                return False
            
            # Check investment amount is reasonable
            if metrics.total_investment < 1000 or metrics.total_investment > 10000000:
                return False
            
            return True
            
        except Exception:
            return False
    
    async def test_fine_tuning_accuracy(self) -> Dict[str, Any]:
        """Test fine-tuning accuracy with mock dataset"""
        logger.info("🧪 Testing fine-tuning accuracy...")
        
        # Test inputs for accuracy evaluation
        test_inputs = [
            "Düşük bütçe ile başla",
            "Revenue hedefi $50K", 
            "Yüksek risk toleransı",
            "Hızlı büyüme istiyorum",
            "Maliyet optimizasyonu",
            "Yeni pazarlara açıl",
            "Teknoloji odaklı",
            "Konsolide et",
            "Sürdürülebilir büyüme",
            "Kriz yönetimi",
            "Start with low budget",
            "Technology focused",
            "Cost optimization",
            "Market expansion",
            "Innovation strategy"
        ]
        
        try:
            # Test accuracy
            accuracy_results = await ai_module.test_fine_tuning_accuracy(test_inputs)
            
            # Assert accuracy meets threshold
            accuracy_meets_threshold = accuracy_results["accuracy"] >= self.accuracy_threshold
            
            result = {
                "test_name": "fine_tuning_accuracy",
                "accuracy": accuracy_results["accuracy"],
                "accuracy_percentage": f"{accuracy_results['accuracy']:.2%}",
                "correct_predictions": accuracy_results["correct_predictions"],
                "total_predictions": accuracy_results["total_predictions"],
                "threshold": self.accuracy_threshold,
                "threshold_percentage": f"{self.accuracy_threshold:.2%}",
                "meets_threshold": accuracy_meets_threshold,
                "test_inputs": test_inputs,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Accuracy test completed: {result['accuracy_percentage']} (Threshold: {result['threshold_percentage']})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Accuracy test failed: {e}")
            return {
                "test_name": "fine_tuning_accuracy",
                "error": str(e),
                "success": False,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_dataset_creation(self) -> Dict[str, Any]:
        """Test enhanced dataset creation"""
        logger.info("🧪 Testing enhanced dataset creation...")
        
        try:
            # Create enhanced dataset
            dataset = await ai_module.create_enhanced_fine_tuning_dataset()
            
            # Validate dataset
            dataset_valid = (
                len(dataset.training_data) > 0 and
                len(dataset.validation_data) > 0 and
                dataset.dataset_size > 0 and
                dataset.training_status == "ready"
            )
            
            result = {
                "test_name": "dataset_creation",
                "training_examples": len(dataset.training_data),
                "validation_examples": len(dataset.validation_data),
                "total_examples": dataset.dataset_size,
                "training_status": dataset.training_status,
                "model_name": dataset.model_name,
                "dataset_valid": dataset_valid,
                "success": dataset_valid,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Dataset creation test completed: {result['total_examples']} total examples")
            return result
            
        except Exception as e:
            logger.error(f"❌ Dataset creation test failed: {e}")
            return {
                "test_name": "dataset_creation",
                "error": str(e),
                "success": False,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_financial_calculations(self) -> Dict[str, Any]:
        """Test enhanced financial calculations with DCF"""
        logger.info("🧪 Testing enhanced financial calculations...")
        
        # Create a test strategy
        from backend.ai import EmpireStrategy, StrategyType
        
        test_strategy = EmpireStrategy(
            strategy_type=StrategyType.LEAN_STARTUP,
            title="Test Strategy",
            description="Test strategy for financial calculations",
            key_actions=["Action 1", "Action 2", "Action 3"],
            timeline_months=12,
            estimated_investment=100000,
            projected_roi=0.20,
            risk_level="Medium",
            success_metrics=["Metric 1", "Metric 2"]
        )
        
        try:
            # Calculate financial metrics
            financial_metrics = ai_module._calculate_enhanced_financial_metrics(test_strategy)
            
            # Validate calculations
            calculations_valid = self._validate_enhanced_financial_metrics(financial_metrics)
            
            result = {
                "test_name": "financial_calculations",
                "npv": financial_metrics.npv,
                "irr": financial_metrics.irr,
                "roi_percentage": financial_metrics.roi_percentage,
                "payback_period": financial_metrics.payback_period,
                "present_value": financial_metrics.present_value,
                "terminal_value": financial_metrics.terminal_value,
                "wacc": financial_metrics.wacc,
                "discounted_cash_flows_count": len(financial_metrics.discounted_cash_flows),
                "calculations_valid": calculations_valid,
                "success": calculations_valid,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Financial calculations test completed: NPV=${financial_metrics.npv:,.2f}, ROI={financial_metrics.roi_percentage:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"❌ Financial calculations test failed: {e}")
            return {
                "test_name": "financial_calculations",
                "error": str(e),
                "success": False,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _validate_enhanced_financial_metrics(self, metrics: FinancialMetricsResponse) -> bool:
        """Validate enhanced financial metrics"""
        try:
            # Check all required fields are present
            required_fields = [
                'npv', 'irr', 'roi_percentage', 'payback_period',
                'present_value', 'terminal_value', 'wacc',
                'discounted_cash_flows'
            ]
            
            for field in required_fields:
                if not hasattr(metrics, field):
                    return False
            
            # Check values are reasonable
            if metrics.npv < -1000000 or metrics.npv > 10000000:
                return False
            
            if metrics.roi_percentage < 0 or metrics.roi_percentage > 100:
                return False
            
            if metrics.payback_period < 1 or metrics.payback_period > 60:
                return False
            
            if metrics.wacc < 0.05 or metrics.wacc > 0.25:
                return False
            
            if len(metrics.discounted_cash_flows) == 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        logger.info("🚀 Starting comprehensive AI module test suite...")
        
        tests = [
            self.test_custom_strategy_generation(),
            self.test_fine_tuning_accuracy(),
            self.test_dataset_creation(),
            self.test_financial_calculations()
        ]
        
        results = []
        for test in tests:
            result = await test
            results.append(result)
            self.test_results.append(result)
        
        # Calculate overall success
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get("success", False))
        overall_success = passed_tests / total_tests if total_tests > 0 else 0
        
        summary = {
            "test_suite": "AI Module Comprehensive Test",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "overall_success_rate": overall_success,
            "overall_success_percentage": f"{overall_success:.2%}",
            "accuracy_threshold": self.accuracy_threshold,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"🎯 Test suite completed: {summary['overall_success_percentage']} success rate")
        return summary
    
    def save_results(self, filename: str = "ai_test_results.json"):
        """Save test results to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"💾 Test results saved to {filename}")
        except Exception as e:
            logger.error(f"❌ Failed to save test results: {e}")

async def main():
    """Main test function"""
    logger.info("🤖 CK Empire AI Module Test Suite")
    logger.info("=" * 50)
    
    # Create test suite
    test_suite = AITestSuite()
    
    # Run all tests
    summary = await test_suite.run_all_tests()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success Rate: {summary['overall_success_percentage']}")
    print(f"Accuracy Threshold: {summary['accuracy_threshold']:.2%}")
    
    # Print individual test results
    print("\n📋 INDIVIDUAL TEST RESULTS")
    print("-" * 50)
    for result in summary['results']:
        test_name = result.get('test_name', 'Unknown')
        success = result.get('success', False)
        status = "✅ PASS" if success else "❌ FAIL"
        
        if 'accuracy' in result:
            print(f"{test_name}: {status} (Accuracy: {result['accuracy']:.2%})")
        elif 'total_examples' in result:
            print(f"{test_name}: {status} (Examples: {result['total_examples']})")
        elif 'npv' in result:
            print(f"{test_name}: {status} (NPV: ${result['npv']:,.2f})")
        else:
            print(f"{test_name}: {status}")
    
    # Save results
    test_suite.save_results()
    
    # Assert overall success
    if summary['overall_success_rate'] < 0.8:  # 80% success threshold
        logger.error("❌ Test suite failed: Success rate below 80%")
        return False
    else:
        logger.info("✅ Test suite passed: Success rate above 80%")
        return True

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 