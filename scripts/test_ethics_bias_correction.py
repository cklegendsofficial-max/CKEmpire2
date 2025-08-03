#!/usr/bin/env python3
"""
Ethics Module Test Script
Tests AIF360 bias detection and correction functionality
"""

import asyncio
import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ethics import ethics_manager, BiasType, CorrectionMethod

class EthicsModuleTester:
    """Test ethics module functionality"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.test_results = []
    
    def print_header(self, title):
        """Print test header"""
        print("\n" + "="*60)
        print(f"🧪 {title}")
        print("="*60)
    
    def print_success(self, message):
        """Print success message"""
        print(f"✅ {message}")
        self.test_results.append({"test": message, "status": "PASS"})
    
    def print_error(self, message):
        """Print error message"""
        print(f"❌ {message}")
        self.test_results.append({"test": message, "status": "FAIL"})
    
    def print_info(self, message):
        """Print info message"""
        print(f"ℹ️  {message}")
    
    def create_biased_dataset(self):
        """Create a biased dataset for testing"""
        np.random.seed(42)
        n_samples = 1000
        
        # Create biased dataset where gender affects outcome
        gender = np.random.choice([0, 1], n_samples, p=[0.6, 0.4])  # More females
        age = np.random.normal(35, 10, n_samples)
        income = np.random.normal(50000, 20000, n_samples)
        education = np.random.choice([0, 1, 2], n_samples, p=[0.3, 0.5, 0.2])
        
        # Biased outcome: males more likely to get positive outcome
        outcome = np.where(
            (gender == 1) & (income > 45000) | (gender == 0) & (income > 60000),
            1, 0
        )
        
        data = []
        for i in range(n_samples):
            data.append({
                'gender': int(gender[i]),
                'age': int(age[i]),
                'income': int(income[i]),
                'education': int(education[i]),
                'outcome': int(outcome[i])
            })
        
        return data
    
    async def test_bias_detection(self):
        """Test bias detection endpoint"""
        self.print_header("Testing Bias Detection")
        
        try:
            # Create biased dataset
            data = self.create_biased_dataset()
            
            # Test API endpoint
            request_data = {
                "data": data,
                "protected_attributes": ["gender", "age"],
                "target_column": "outcome",
                "privileged_groups": [
                    {"privileged_value": 1, "unprivileged_value": 0},  # gender
                    {"privileged_value": 1, "unprivileged_value": 0}   # age (simplified)
                ]
            }
            
            response = requests.post(f"{self.base_url}/ethics/detect-bias", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                self.print_success("Bias detection API test passed")
                self.print_info(f"Bias detected: {result['bias_detected']}")
                self.print_info(f"Total metrics: {result['total_metrics']}")
                self.print_info(f"Metrics found: {len(result['bias_metrics'])}")
                
                # Check bias metrics
                for metric in result['bias_metrics']:
                    self.print_info(f"Bias type: {metric['bias_type']}, Score: {metric['overall_bias_score']:.3f}")
                
                return result
            else:
                self.print_error(f"Bias detection failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.print_error(f"Error testing bias detection: {e}")
            return None
    
    async def test_bias_correction(self):
        """Test bias correction endpoint"""
        self.print_header("Testing Bias Correction")
        
        try:
            # Create biased dataset
            data = self.create_biased_dataset()
            
            # Test API endpoint
            request_data = {
                "data": data,
                "protected_attributes": ["gender"],
                "target_column": "outcome",
                "privileged_groups": [
                    {"privileged_value": 1, "unprivileged_value": 0}
                ],
                "correction_method": "reweighing"
            }
            
            response = requests.post(f"{self.base_url}/ethics/correct-bias", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                self.print_success("Bias correction API test passed")
                self.print_info(f"Correction successful: {result['correction_successful']}")
                self.print_info(f"Method used: {result['method']}")
                self.print_info(f"Original bias: {result['original_bias']:.3f}")
                self.print_info(f"Corrected bias: {result['corrected_bias']:.3f}")
                self.print_info(f"Bias reduction: {result['bias_reduction']:.3f}")
                self.print_info(f"Corrected data size: {len(result['corrected_data'])}")
                
                return result
            else:
                self.print_error(f"Bias correction failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.print_error(f"Error testing bias correction: {e}")
            return None
    
    async def test_ethical_report(self):
        """Test ethical report generation"""
        self.print_header("Testing Ethical Report Generation")
        
        try:
            # Create biased dataset
            data = self.create_biased_dataset()
            
            # Test API endpoint
            request_data = {
                "data": data,
                "protected_attributes": ["gender", "age"],
                "target_column": "outcome",
                "privileged_groups": [
                    {"privileged_value": 1, "unprivileged_value": 0},
                    {"privileged_value": 1, "unprivileged_value": 0}
                ]
            }
            
            response = requests.post(f"{self.base_url}/ethics/report", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                self.print_success("Ethical report generation test passed")
                self.print_info(f"Ethical score: {result['overall_ethical_score']:.3f}")
                self.print_info(f"Bias detected: {result['bias_detected']}")
                self.print_info(f"Correction applied: {result['correction_applied']}")
                self.print_info(f"Compliance status: {result['compliance_status']}")
                self.print_info(f"Risk level: {result['risk_level']}")
                self.print_info(f"Should stop evolution: {result['should_stop_evolution']}")
                self.print_info(f"Recommendations: {len(result['recommendations'])}")
                
                return result
            else:
                self.print_error(f"Ethical report generation failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.print_error(f"Error testing ethical report: {e}")
            return None
    
    async def test_ethics_dashboard(self):
        """Test ethics dashboard endpoint"""
        self.print_header("Testing Ethics Dashboard")
        
        try:
            response = requests.get(f"{self.base_url}/ethics/dashboard")
            
            if response.status_code == 200:
                result = response.json()
                self.print_success("Ethics dashboard test passed")
                self.print_info(f"Overall ethical score: {result['overall_ethical_score']:.3f}")
                self.print_info(f"Bias detection rate: {result['bias_detection_rate']:.3f}")
                self.print_info(f"Correction success rate: {result['correction_success_rate']:.3f}")
                self.print_info(f"Compliance rate: {result['compliance_rate']:.3f}")
                self.print_info(f"Total corrections: {result['total_corrections']}")
                self.print_info(f"Total reports: {result['total_reports']}")
                
                return result
            else:
                self.print_error(f"Ethics dashboard failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.print_error(f"Error testing ethics dashboard: {e}")
            return None
    
    async def test_bias_types(self):
        """Test bias types endpoint"""
        self.print_header("Testing Bias Types Endpoint")
        
        try:
            response = requests.get(f"{self.base_url}/ethics/bias-types")
            
            if response.status_code == 200:
                result = response.json()
                self.print_success("Bias types endpoint test passed")
                self.print_info(f"Available bias types: {len(result['bias_types'])}")
                
                for bias_type in result['bias_types']:
                    self.print_info(f"  - {bias_type['label']} ({bias_type['value']})")
                
                return result
            else:
                self.print_error(f"Bias types endpoint failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.print_error(f"Error testing bias types: {e}")
            return None
    
    async def test_correction_methods(self):
        """Test correction methods endpoint"""
        self.print_header("Testing Correction Methods Endpoint")
        
        try:
            response = requests.get(f"{self.base_url}/ethics/correction-methods")
            
            if response.status_code == 200:
                result = response.json()
                self.print_success("Correction methods endpoint test passed")
                self.print_info(f"Available correction methods: {len(result['correction_methods'])}")
                
                for method in result['correction_methods']:
                    self.print_info(f"  - {method['label']} ({method['value']})")
                
                return result
            else:
                self.print_error(f"Correction methods endpoint failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.print_error(f"Error testing correction methods: {e}")
            return None
    
    async def test_compliance_status(self):
        """Test compliance status endpoint"""
        self.print_header("Testing Compliance Status Endpoint")
        
        try:
            # Test with different ethical scores
            test_scores = [0.9, 0.7, 0.5]
            
            for score in test_scores:
                response = requests.get(f"{self.base_url}/ethics/compliance-status?ethical_score={score}")
                
                if response.status_code == 200:
                    result = response.json()
                    self.print_success(f"Compliance status test passed for score {score}")
                    self.print_info(f"  Score: {result['ethical_score']}")
                    self.print_info(f"  Status: {result['compliance_status']}")
                    self.print_info(f"  Risk level: {result['risk_level']}")
                    self.print_info(f"  Should stop evolution: {result['should_stop_evolution']}")
                else:
                    self.print_error(f"Compliance status failed for score {score}: {response.status_code}")
                
        except Exception as e:
            self.print_error(f"Error testing compliance status: {e}")
    
    async def test_bias_correction_test(self):
        """Test bias correction test endpoint"""
        self.print_header("Testing Bias Correction Test Endpoint")
        
        try:
            response = requests.get(f"{self.base_url}/ethics/test-bias-correction")
            
            if response.status_code == 200:
                result = response.json()
                self.print_success("Bias correction test endpoint passed")
                self.print_info(f"Test successful: {result['test_successful']}")
                self.print_info(f"Original bias detected: {result['original_bias_detected']}")
                self.print_info(f"Correction applied: {result['correction_applied']}")
                self.print_info(f"Bias reduction: {result['bias_reduction']:.3f}")
                self.print_info(f"Ethical score: {result['ethical_score']:.3f}")
                self.print_info(f"Should stop evolution: {result['should_stop_evolution']}")
                self.print_info(f"Sample size: {result['sample_size']}")
                self.print_info(f"Bias type: {result['bias_type']}")
                
                return result
            else:
                self.print_error(f"Bias correction test failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.print_error(f"Error testing bias correction test: {e}")
            return None
    
    async def test_ethics_manager_direct(self):
        """Test ethics manager directly"""
        self.print_header("Testing Ethics Manager Directly")
        
        try:
            # Create biased dataset
            data = self.create_biased_dataset()
            df = pd.DataFrame(data)
            
            # Test bias detection
            bias_metrics = ethics_manager.detect_bias(
                data=df,
                protected_attributes=['gender'],
                target_column='outcome',
                privileged_groups=[{'privileged_value': 1, 'unprivileged_value': 0}]
            )
            
            self.print_success("Direct bias detection test passed")
            self.print_info(f"Bias metrics found: {len(bias_metrics)}")
            
            for metric in bias_metrics:
                self.print_info(f"  - {metric.bias_type.value}: {metric.overall_bias_score:.3f}")
            
            # Test bias correction
            corrected_data, correction_info = ethics_manager.apply_bias_correction(
                data=df,
                protected_attributes=['gender'],
                target_column='outcome',
                privileged_groups=[{'privileged_value': 1, 'unprivileged_value': 0}]
            )
            
            self.print_success("Direct bias correction test passed")
            self.print_info(f"Correction successful: {correction_info.get('correction_successful', False)}")
            self.print_info(f"Bias reduction: {correction_info.get('bias_reduction', 0):.3f}")
            
            # Test ethical report
            report = ethics_manager.generate_ethical_report(
                data=df,
                protected_attributes=['gender'],
                target_column='outcome',
                privileged_groups=[{'privileged_value': 1, 'unprivileged_value': 0}]
            )
            
            self.print_success("Direct ethical report test passed")
            self.print_info(f"Ethical score: {report.overall_ethical_score:.3f}")
            self.print_info(f"Bias detected: {report.bias_detected}")
            self.print_info(f"Should stop evolution: {ethics_manager.should_stop_evolution(report.overall_ethical_score)}")
            
        except Exception as e:
            self.print_error(f"Error testing ethics manager directly: {e}")
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Ethics Module Test Summary")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  ❌ {result['test']}")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting Ethics Module Tests")
        print(f"Base URL: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Run tests
        await self.test_bias_detection()
        await self.test_bias_correction()
        await self.test_ethical_report()
        await self.test_ethics_dashboard()
        await self.test_bias_types()
        await self.test_correction_methods()
        await self.test_compliance_status()
        await self.test_bias_correction_test()
        await self.test_ethics_manager_direct()
        
        # Print summary
        self.print_summary()

def main():
    """Main function"""
    tester = EthicsModuleTester()
    
    try:
        asyncio.run(tester.run_all_tests())
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 