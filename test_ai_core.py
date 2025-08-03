#!/usr/bin/env python3
"""
Core AI module test script - tests functionality without API keys
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
    from backend.ai import ai_module, EmpireStrategy, StrategyType, FinancialMetrics
except ImportError as e:
    logger.error(f"Failed to import AI module: {e}")
    exit(1)

class CoreAITestSuite:
    """Core test suite for AI module without API dependencies"""
    
    def __init__(self):
        self.test_results = []
        
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
    
    def _validate_enhanced_financial_metrics(self, metrics: FinancialMetrics) -> bool:
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
    
    async def test_strategy_type_detection(self) -> Dict[str, Any]:
        """Test strategy type detection logic"""
        logger.info("🧪 Testing strategy type detection...")
        
        test_cases = [
            ("Düşük bütçe ile başla", StrategyType.LEAN_STARTUP),
            ("Revenue hedefi $50K", StrategyType.SCALE_UP),
            ("Yüksek risk toleransı", StrategyType.INNOVATION),
            ("Start with low budget", StrategyType.LEAN_STARTUP),
            ("Technology focused", StrategyType.INNOVATION),
            ("Cost optimization", StrategyType.COST_OPTIMIZATION),
            ("Market expansion", StrategyType.DIVERSIFICATION),
            ("Acquisition strategy", StrategyType.ACQUISITION)
        ]
        
        results = []
        for input_text, expected_type in test_cases:
            try:
                # Test strategy type detection
                detected_type = ai_module._determine_enhanced_strategy_type(input_text, input_text)
                
                type_match = detected_type == expected_type
                results.append({
                    "input": input_text,
                    "expected": expected_type.value,
                    "detected": detected_type.value,
                    "match": type_match
                })
                
                logger.info(f"✅ {input_text}: {detected_type.value} (Expected: {expected_type.value})")
                
            except Exception as e:
                logger.error(f"❌ Strategy type detection failed for '{input_text}': {e}")
                results.append({
                    "input": input_text,
                    "error": str(e),
                    "match": False
                })
        
        total_tests = len(test_cases)
        passed_tests = sum(1 for r in results if r.get("match", False))
        
        return {
            "test_name": "strategy_type_detection",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "results": results,
            "success": passed_tests / total_tests >= 0.8,  # 80% threshold
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def test_fallback_strategy_generation(self) -> Dict[str, Any]:
        """Test fallback strategy generation when API is not available"""
        logger.info("🧪 Testing fallback strategy generation...")
        
        test_inputs = [
            "Düşük bütçe ile başla",
            "Revenue hedefi $50K",
            "Yüksek risk toleransı",
            "Start with low budget",
            "Technology focused"
        ]
        
        results = []
        for input_text in test_inputs:
            try:
                # Generate fallback strategy
                strategy = ai_module._create_fallback_strategy(input_text)
                
                # Validate strategy
                strategy_valid = (
                    strategy.title is not None and
                    strategy.description is not None and
                    len(strategy.key_actions) > 0 and
                    strategy.estimated_investment > 0 and
                    strategy.projected_roi > 0
                )
                
                results.append({
                    "input": input_text,
                    "strategy_title": strategy.title,
                    "strategy_type": strategy.strategy_type.value,
                    "estimated_investment": strategy.estimated_investment,
                    "projected_roi": strategy.projected_roi,
                    "valid": strategy_valid
                })
                
                logger.info(f"✅ Fallback strategy for '{input_text}': {strategy.title}")
                
            except Exception as e:
                logger.error(f"❌ Fallback strategy generation failed for '{input_text}': {e}")
                results.append({
                    "input": input_text,
                    "error": str(e),
                    "valid": False
                })
        
        total_tests = len(test_inputs)
        passed_tests = sum(1 for r in results if r.get("valid", False))
        
        return {
            "test_name": "fallback_strategy_generation",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "results": results,
            "success": passed_tests / total_tests >= 0.8,  # 80% threshold
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all core tests and return comprehensive results"""
        logger.info("🚀 Starting core AI module test suite...")
        
        tests = [
            self.test_dataset_creation(),
            self.test_financial_calculations(),
            self.test_strategy_type_detection(),
            self.test_fallback_strategy_generation()
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
            "test_suite": "AI Module Core Test (No API Required)",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "overall_success_rate": overall_success,
            "overall_success_percentage": f"{overall_success:.2%}",
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"🎯 Core test suite completed: {summary['overall_success_percentage']} success rate")
        return summary
    
    def save_results(self, filename: str = "ai_core_test_results.json"):
        """Save test results to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"💾 Core test results saved to {filename}")
        except Exception as e:
            logger.error(f"❌ Failed to save test results: {e}")

async def main():
    """Main test function"""
    logger.info("🤖 CK Empire AI Module Core Test Suite")
    logger.info("=" * 50)
    
    # Create test suite
    test_suite = CoreAITestSuite()
    
    # Run all tests
    summary = await test_suite.run_all_tests()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 CORE TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success Rate: {summary['overall_success_percentage']}")
    
    # Print individual test results
    print("\n📋 INDIVIDUAL TEST RESULTS")
    print("-" * 50)
    for result in summary['results']:
        test_name = result.get('test_name', 'Unknown')
        success = result.get('success', False)
        status = "✅ PASS" if success else "❌ FAIL"
        
        if 'total_examples' in result:
            print(f"{test_name}: {status} (Examples: {result['total_examples']})")
        elif 'npv' in result:
            print(f"{test_name}: {status} (NPV: ${result['npv']:,.2f})")
        elif 'success_rate' in result:
            print(f"{test_name}: {status} (Success Rate: {result['success_rate']:.2%})")
        else:
            print(f"{test_name}: {status}")
    
    # Save results
    test_suite.save_results()
    
    # Assert overall success
    if summary['overall_success_rate'] < 0.8:  # 80% success threshold
        logger.error("❌ Core test suite failed: Success rate below 80%")
        return False
    else:
        logger.info("✅ Core test suite passed: Success rate above 80%")
        return True

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 