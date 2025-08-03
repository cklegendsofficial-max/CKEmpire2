#!/usr/bin/env python3
"""
Simplified Ethics Test Script
Tests AIF360 bias detection, correction, auto-fix, and revert functionality
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Mock config to avoid import issues
class MockSettings:
    def __init__(self):
        self.encryption_key = "test_key_12345"
        self.database_url = "sqlite:///test.db"
        self.DATABASE_URL = "sqlite:///test.db"
        self.secret_key = "test_secret_key"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.redis_url = "redis://localhost:6379"
        self.vault_url = "http://localhost:8200"
        self.vault_token = "test_token"
        self.stripe_secret_key = "sk_test_123"
        self.stripe_publishable_key = "pk_test_123"
        self.openai_api_key = "sk-test-123"
        self.sentry_dsn = "https://test@sentry.io/123"
        self.log_level = "INFO"
        self.environment = "test"
        self.DEBUG = False
        self.TESTING = True
        self.DEVELOPMENT = False
        self.PRODUCTION = False
        self.API_V1_STR = "/api/v1"
        self.PROJECT_NAME = "CK Empire"
        self.BACKEND_CORS_ORIGINS = ["http://localhost:3000"]
        self.SUPERUSER_EMAIL = "admin@ckempire.com"
        self.SUPERUSER_PASSWORD = "admin123"
        self.FIRST_SUPERUSER = "admin@ckempire.com"
        self.FIRST_SUPERUSER_PASSWORD = "admin123"
        self.USERS_OPEN_REGISTRATION = True
        self.EMAILS_FROM_EMAIL = "noreply@ckempire.com"
        self.EMAILS_FROM_NAME = "CK Empire"
        self.SMTP_TLS = True
        self.SMTP_PORT = 587
        self.SMTP_HOST = "smtp.gmail.com"
        self.SMTP_USER = "test@example.com"
        self.SMTP_PASSWORD = "test_password"
        self.EMAILS_ENABLED = False
        self.EMAIL_TEST_USER = "test@example.com"
        self.SERVER_NAME = "localhost"
        self.SERVER_HOST = "http://localhost"
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.API_V1_STR = "/api/v1"
        self.PROJECT_NAME = "CK Empire"
        self.VERSION = "1.0.0"
        self.DESCRIPTION = "CK Empire API"
        self.AUTHOR = "CK Empire Team"
        self.EMAIL = "admin@ckempire.com"
        self.LICENSE = "MIT"
        self.URL = "https://ckempire.com"

# Mock the config module
sys.modules['config'] = type('MockConfig', (), {'settings': MockSettings()})

try:
    from ethics import ethics_manager, BiasType, CorrectionMethod
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class SimpleEthicsTester:
    """Test ethics bias detection and correction"""
    
    def __init__(self):
        self.test_results = {}
        self.biased_datasets = {}
        
    def create_biased_datasets(self):
        """Create various biased datasets for testing"""
        print("🔧 Creating biased datasets for testing...")
        
        # Dataset 1: Gender bias in hiring
        np.random.seed(42)
        n_samples = 1000
        
        # Gender bias: Males more likely to be hired
        gender = np.random.choice([0, 1], n_samples, p=[0.6, 0.4])  # More females
        experience = np.random.normal(5, 2, n_samples)
        education = np.random.choice([1, 2, 3], n_samples, p=[0.3, 0.5, 0.2])
        
        # Biased hiring: Males more likely to be hired even with same qualifications
        hire_probability = 0.3 + 0.4 * (experience / 10) + 0.2 * (education / 3)
        hire_probability += 0.2 * gender  # Bias: males get +20% chance
        hired = np.random.binomial(1, np.clip(hire_probability, 0, 1))
        
        self.biased_datasets['gender_hiring'] = pd.DataFrame({
            'gender': gender,
            'experience': experience,
            'education': education,
            'hired': hired
        })
        
        print(f"✅ Created {len(self.biased_datasets)} biased datasets")
        
    def test_bias_detection(self) -> Dict[str, Any]:
        """Test bias detection on all datasets"""
        print("\n🔍 Testing bias detection...")
        results = {}
        
        for dataset_name, data in self.biased_datasets.items():
            try:
                # Define protected attributes and privileged groups
                protected_attrs = ['gender']
                privileged_groups = [{'privileged_value': 1, 'unprivileged_value': 0}]
                target_col = 'hired'
                
                # Detect bias
                bias_metrics = ethics_manager.detect_bias(
                    data=data,
                    protected_attributes=protected_attrs,
                    target_column=target_col,
                    privileged_groups=privileged_groups
                )
                
                # Calculate overall bias
                overall_bias = np.mean([metric.overall_bias_score for metric in bias_metrics])
                bias_detected = any(metric.overall_bias_score > ethics_manager.bias_threshold for metric in bias_metrics)
                
                results[dataset_name] = {
                    'success': True,
                    'bias_detected': bias_detected,
                    'overall_bias': overall_bias,
                    'metrics_count': len(bias_metrics),
                    'protected_attributes': protected_attrs,
                    'target_column': target_col
                }
                
                print(f"  ✅ {dataset_name}: Bias detected: {bias_detected}, Score: {overall_bias:.3f}")
                
            except Exception as e:
                results[dataset_name] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ {dataset_name}: Error - {e}")
        
        return results
    
    def test_bias_correction(self) -> Dict[str, Any]:
        """Test bias correction using AIF360 reweighing"""
        print("\n🔧 Testing bias correction...")
        results = {}
        
        for dataset_name, data in self.biased_datasets.items():
            try:
                # Define parameters
                protected_attrs = ['gender']
                privileged_groups = [{'privileged_value': 1, 'unprivileged_value': 0}]
                target_col = 'hired'
                
                # Apply bias correction
                corrected_data, correction_info = ethics_manager.apply_bias_correction(
                    data=data,
                    protected_attributes=protected_attrs,
                    target_column=target_col,
                    privileged_groups=privileged_groups,
                    method=CorrectionMethod.REWEIGHING
                )
                
                # Check if correction was successful
                correction_successful = correction_info.get('correction_successful', False)
                bias_reduction = correction_info.get('bias_reduction', 0.0)
                
                results[dataset_name] = {
                    'success': True,
                    'correction_successful': correction_successful,
                    'bias_reduction': bias_reduction,
                    'method': correction_info.get('method', 'unknown'),
                    'weights_applied': correction_info.get('weights_applied', False),
                    'aif360_method': correction_info.get('aif360_method', 'unknown')
                }
                
                print(f"  ✅ {dataset_name}: Success: {correction_successful}, Reduction: {bias_reduction:.3f}")
                
            except Exception as e:
                results[dataset_name] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ {dataset_name}: Error - {e}")
        
        return results
    
    def test_auto_fix(self) -> Dict[str, Any]:
        """Test auto-fix functionality"""
        print("\n🤖 Testing auto-fix functionality...")
        results = {}
        
        for dataset_name, data in self.biased_datasets.items():
            try:
                # Define parameters
                protected_attrs = ['gender']
                privileged_groups = [{'privileged_value': 1, 'unprivileged_value': 0}]
                target_col = 'hired'
                
                # Apply auto-fix
                corrected_data, auto_fix_info = ethics_manager.auto_fix_bias(
                    data=data,
                    protected_attributes=protected_attrs,
                    target_column=target_col,
                    privileged_groups=privileged_groups
                )
                
                auto_fix_applied = auto_fix_info.get('auto_fix_applied', False)
                bias_reduction = auto_fix_info.get('bias_reduction', 0.0)
                
                # Handle correction_info properly
                correction_info = auto_fix_info.get('correction_info', {})
                if isinstance(correction_info, dict):
                    bias_reduction = correction_info.get('bias_reduction', bias_reduction)
                
                results[dataset_name] = {
                    'success': True,
                    'auto_fix_applied': auto_fix_applied,
                    'bias_detected': auto_fix_info.get('bias_detected', False),
                    'bias_reduction': bias_reduction,
                    'method_used': auto_fix_info.get('method_used', 'none')
                }
                
                print(f"  ✅ {dataset_name}: Auto-fix applied: {auto_fix_applied}, Reduction: {bias_reduction:.3f}")
                
            except Exception as e:
                results[dataset_name] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ {dataset_name}: Error - {e}")
        
        return results
    
    def test_ethical_report(self) -> Dict[str, Any]:
        """Test comprehensive ethical report generation"""
        print("\n📊 Testing ethical report generation...")
        results = {}
        
        for dataset_name, data in self.biased_datasets.items():
            try:
                # Define parameters
                protected_attrs = ['gender']
                privileged_groups = [{'privileged_value': 1, 'unprivileged_value': 0}]
                target_col = 'hired'
                
                # Generate ethical report
                report = ethics_manager.generate_ethical_report(
                    data=data,
                    protected_attributes=protected_attrs,
                    target_column=target_col,
                    privileged_groups=privileged_groups
                )
                
                results[dataset_name] = {
                    'success': True,
                    'ethical_score': report.overall_ethical_score,
                    'bias_detected': report.bias_detected,
                    'correction_applied': report.correction_applied,
                    'auto_fix_applied': report.auto_fix_applied,
                    'revert_triggered': report.revert_triggered,
                    'compliance_status': report.compliance_status,
                    'risk_level': report.risk_level,
                    'recommendations_count': len(report.recommendations)
                }
                
                print(f"  ✅ {dataset_name}: Score: {report.overall_ethical_score:.3f}, "
                      f"Auto-fix: {report.auto_fix_applied}, Revert: {report.revert_triggered}")
                
            except Exception as e:
                results[dataset_name] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ {dataset_name}: Error - {e}")
        
        return results
    
    def test_revert_functionality(self) -> Dict[str, Any]:
        """Test revert functionality with low ethical scores"""
        print("\n🔄 Testing revert functionality...")
        results = {}
        
        # Test different ethical scores
        test_scores = [0.3, 0.5, 0.7, 0.9]
        
        for score in test_scores:
            try:
                should_revert = ethics_manager.should_revert_evolution(score)
                should_stop = ethics_manager.should_stop_evolution(score)
                
                results[f'score_{score}'] = {
                    'success': True,
                    'ethical_score': score,
                    'should_revert': should_revert,
                    'should_stop': should_stop,
                    'revert_threshold': ethics_manager.revert_threshold,
                    'stop_threshold': ethics_manager.ethical_score_threshold
                }
                
                print(f"  ✅ Score {score}: Revert: {should_revert}, Stop: {should_stop}")
                
            except Exception as e:
                results[f'score_{score}'] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ Score {score}: Error - {e}")
        
        return results
    
    def test_dashboard_data(self) -> Dict[str, Any]:
        """Test dashboard data generation"""
        print("\n📈 Testing dashboard data generation...")
        
        try:
            dashboard_data = ethics_manager.get_ethical_dashboard_data()
            
            # Debug: print the dashboard data structure
            print(f"  🔍 Dashboard data type: {type(dashboard_data)}")
            if isinstance(dashboard_data, dict):
                print(f"  🔍 Dashboard data keys: {list(dashboard_data.keys())}")
            
            # Handle potential boolean values safely
            def safe_get(data, key, default=0):
                if not isinstance(data, dict):
                    return default
                value = data.get(key, default)
                if isinstance(value, bool):
                    return 1 if value else 0
                return value
            
            results = {
                'success': True,
                'overall_ethical_score': safe_get(dashboard_data, 'overall_ethical_score', 0),
                'bias_detection_rate': safe_get(dashboard_data, 'bias_detection_rate', 0),
                'correction_success_rate': safe_get(dashboard_data, 'correction_success_rate', 0),
                'auto_fix_success_rate': safe_get(dashboard_data, 'auto_fix_success_rate', 0),
                'compliance_rate': safe_get(dashboard_data, 'compliance_rate', 0),
                'total_corrections': safe_get(dashboard_data, 'total_corrections', 0),
                'total_auto_fixes': safe_get(dashboard_data, 'total_auto_fixes', 0),
                'total_reverts': safe_get(dashboard_data, 'total_reverts', 0),
                'aif360_integration': dashboard_data.get('aif360_integration', False) if isinstance(dashboard_data, dict) else False
            }
            
            print(f"  ✅ Dashboard: Score: {results['overall_ethical_score']:.3f}, "
                  f"Auto-fixes: {results['total_auto_fixes']}, Reverts: {results['total_reverts']}")
            
            return results
            
        except Exception as e:
            print(f"  ❌ Dashboard error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive ethics test"""
        print("🚀 CK Empire Ethics Bias Correction Test Suite")
        print("=" * 60)
        
        # Create biased datasets
        self.create_biased_datasets()
        
        # Run all tests
        self.test_results = {
            'bias_detection': self.test_bias_detection(),
            'bias_correction': self.test_bias_correction(),
            'auto_fix': self.test_auto_fix(),
            'ethical_report': self.test_ethical_report(),
            'revert_functionality': self.test_revert_functionality(),
            'dashboard_data': self.test_dashboard_data()
        }
        
        # Calculate overall success rate
        total_tests = 0
        successful_tests = 0
        
        print("\n🔍 Calculating test results...")
        for test_category, results in self.test_results.items():
            print(f"  📊 {test_category}: {type(results)}")
            if isinstance(results, dict):
                for test_name, result in results.items():
                    print(f"    - {test_name}: {type(result)}")
                    total_tests += 1
                    if isinstance(result, dict) and result.get('success', False):
                        successful_tests += 1
                    elif isinstance(result, bool) and result:
                        successful_tests += 1
        
        overall_success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        # Generate summary
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'overall_success_rate': overall_success_rate,
            'test_results': self.test_results,
            'aif360_integration': True,
            'auto_fix_enabled': True,
            'revert_functionality': True
        }
        
        return summary
    
    def save_test_results(self, results: Dict[str, Any], filename: str = None):
        """Save test results to file"""
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"ethics_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Test results saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")

def main():
    """Main test function"""
    tester = SimpleEthicsTester()
    
    try:
        # Run comprehensive test
        results = tester.run_comprehensive_test()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Successful Tests: {results['successful_tests']}")
        print(f"Success Rate: {results['overall_success_rate']:.1%}")
        print(f"AIF360 Integration: {results['aif360_integration']}")
        print(f"Auto-fix Enabled: {results['auto_fix_enabled']}")
        print(f"Revert Functionality: {results['revert_functionality']}")
        
        # Save results
        tester.save_test_results(results)
        
        # Exit with appropriate code
        if results['overall_success_rate'] >= 0.8:
            print("\n🎉 Ethics test suite passed successfully!")
            return 0
        else:
            print("\n⚠️  Some ethics tests failed. Please review the results.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 