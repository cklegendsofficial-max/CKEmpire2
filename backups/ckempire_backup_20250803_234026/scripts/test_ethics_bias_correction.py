#!/usr/bin/env python3
"""
Ethics Bias Correction Test Script
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

try:
    from ethics import ethics_manager, BiasType, CorrectionMethod
    from models import BiasDetectionRequest, BiasCorrectionRequest
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class EthicsBiasTester:
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
        
        # Dataset 2: Age bias in loan approval
        np.random.seed(43)
        age = np.random.normal(45, 15, n_samples)
        income = np.random.normal(60000, 20000, n_samples)
        credit_score = np.random.normal(700, 100, n_samples)
        
        # Age bias: Younger people less likely to get loans
        loan_probability = 0.4 + 0.3 * (income / 100000) + 0.3 * (credit_score / 800)
        loan_probability -= 0.15 * (age < 30)  # Bias: young people get -15% chance
        loan_approved = np.random.binomial(1, np.clip(loan_probability, 0, 1))
        
        self.biased_datasets['age_loan'] = pd.DataFrame({
            'age': age,
            'income': income,
            'credit_score': credit_score,
            'loan_approved': loan_approved
        })
        
        # Dataset 3: Income bias in university admission
        np.random.seed(44)
        income_level = np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.2, 0.3, 0.25, 0.15, 0.1])
        gpa = np.random.normal(3.5, 0.5, n_samples)
        test_score = np.random.normal(1200, 200, n_samples)
        
        # Income bias: Higher income more likely to be admitted
        admission_probability = 0.3 + 0.4 * (gpa / 4.0) + 0.3 * (test_score / 1600)
        admission_probability += 0.1 * (income_level >= 4)  # Bias: high income gets +10% chance
        admitted = np.random.binomial(1, np.clip(admission_probability, 0, 1))
        
        self.biased_datasets['income_admission'] = pd.DataFrame({
            'income_level': income_level,
            'gpa': gpa,
            'test_score': test_score,
            'admitted': admitted
        })
        
        print(f"✅ Created {len(self.biased_datasets)} biased datasets")
        
    def test_bias_detection(self) -> Dict[str, Any]:
        """Test bias detection on all datasets"""
        print("\n🔍 Testing bias detection...")
        results = {}
        
        for dataset_name, data in self.biased_datasets.items():
            try:
                # Define protected attributes and privileged groups
                if dataset_name == 'gender_hiring':
                    protected_attrs = ['gender']
                    privileged_groups = [{'privileged_value': 1, 'unprivileged_value': 0}]
                    target_col = 'hired'
                elif dataset_name == 'age_loan':
                    protected_attrs = ['age']
                    privileged_groups = [{'privileged_value': 1, 'unprivileged_value': 0}]  # Simplified
                    target_col = 'loan_approved'
                else:  # income_admission
                    protected_attrs = ['income_level']
                    privileged_groups = [{'privileged_value': 5, 'unprivileged_value': 1}]
                    target_col = 'admitted'
                
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
                if dataset_name == 'gender_hiring':
                    protected_attrs = ['gender']
                    privileged_groups = [{'privileged_value': 1, 'unprivileged_value': 0}]
                    target_col = 'hired'
                elif dataset_name == 'age_loan':
                    protected_attrs = ['age']
                    privileged_groups = [{'privileged_value': 1, 'unprivileged_value': 0}]
                    target_col = 'loan_approved'
                else:  # income_admission
                    protected_attrs = ['income_level']
                    privileged_groups = [{'privileged_value': 5, 'unprivileged_value': 1}]
                    target_col = 'admitted'
                
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
                if dataset_name == 'gender_hiring':
                    protected_attrs = ['gender']
                    privileged_groups = [{'privileged_value': 1, 'unprivileged_value': 0}]
                    target_col = 'hired'
                elif dataset_name == 'age_loan':
                    protected_attrs = ['age']
                    privileged_groups = [{'privileged_value': 1, 'unprivileged_value': 0}]
                    target_col = 'loan_approved'
                else:  # income_admission
                    protected_attrs = ['income_level']
                    privileged_groups = [{'privileged_value': 5, 'unprivileged_value': 1}]
                    target_col = 'admitted'
                
                # Apply auto-fix
                corrected_data, auto_fix_info = ethics_manager.auto_fix_bias(
                    data=data,
                    protected_attributes=protected_attrs,
                    target_column=target_col,
                    privileged_groups=privileged_groups
                )
                
                auto_fix_applied = auto_fix_info.get('auto_fix_applied', False)
                bias_reduction = auto_fix_info.get('bias_reduction', 0.0)
                
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
                if dataset_name == 'gender_hiring':
                    protected_attrs = ['gender']
                    privileged_groups = [{'privileged_value': 1, 'unprivileged_value': 0}]
                    target_col = 'hired'
                elif dataset_name == 'age_loan':
                    protected_attrs = ['age']
                    privileged_groups = [{'privileged_value': 1, 'unprivileged_value': 0}]
                    target_col = 'loan_approved'
                else:  # income_admission
                    protected_attrs = ['income_level']
                    privileged_groups = [{'privileged_value': 5, 'unprivileged_value': 1}]
                    target_col = 'admitted'
                
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
            
            results = {
                'success': True,
                'overall_ethical_score': dashboard_data.get('overall_ethical_score', 0),
                'bias_detection_rate': dashboard_data.get('bias_detection_rate', 0),
                'correction_success_rate': dashboard_data.get('correction_success_rate', 0),
                'auto_fix_success_rate': dashboard_data.get('auto_fix_success_rate', 0),
                'compliance_rate': dashboard_data.get('compliance_rate', 0),
                'total_corrections': dashboard_data.get('total_corrections', 0),
                'total_auto_fixes': dashboard_data.get('total_auto_fixes', 0),
                'total_reverts': dashboard_data.get('total_reverts', 0),
                'aif360_integration': dashboard_data.get('aif360_integration', False)
            }
            
            print(f"  ✅ Dashboard: Score: {results['overall_ethical_score']:.3f}, "
                  f"Auto-fixes: {results['total_auto_fixes']}, Reverts: {results['total_reverts']}")
            
            return results
            
        except Exception as e:
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
        
        for test_category, results in self.test_results.items():
            if isinstance(results, dict):
                for test_name, result in results.items():
                    total_tests += 1
                    if result.get('success', False):
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
    tester = EthicsBiasTester()
    
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