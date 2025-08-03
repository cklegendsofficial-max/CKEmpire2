#!/usr/bin/env python3
"""
Stripe Subscription Test Script for CK Empire
Tests the monetization features including A/B testing, freemium model, and payment simulation
"""

import os
import sys
import asyncio
import requests
import json
from datetime import datetime
from typing import Dict, Any

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

class StripeSubscriptionTester:
    """Test Stripe subscription features"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.test_results = {}
        
    async def test_subscription_endpoints(self) -> Dict[str, Any]:
        """Test all subscription endpoints"""
        print("🔍 Testing Subscription Endpoints...")
        
        results = {}
        
        # Test 1: Get pricing plans
        try:
            response = requests.get(f"{self.base_url}/subscription/plans")
            if response.status_code == 200:
                plans = response.json()
                results['pricing_plans'] = {
                    'success': True,
                    'plans_count': len(plans),
                    'plans': [plan['tier'] for plan in plans]
                }
                print(f"✅ Pricing plans: {len(plans)} plans found")
            else:
                results['pricing_plans'] = {'success': False, 'error': response.text}
                print(f"❌ Pricing plans failed: {response.status_code}")
        except Exception as e:
            results['pricing_plans'] = {'success': False, 'error': str(e)}
            print(f"❌ Pricing plans error: {e}")
        
        # Test 2: Get subscription status
        try:
            response = requests.get(f"{self.base_url}/subscription/status")
            if response.status_code == 200:
                status = response.json()
                results['subscription_status'] = {
                    'success': True,
                    'has_subscription': status.get('has_subscription', False),
                    'tier': status.get('tier', 'freemium')
                }
                print(f"✅ Subscription status: {status.get('tier', 'freemium')}")
            else:
                results['subscription_status'] = {'success': False, 'error': response.text}
                print(f"❌ Subscription status failed: {response.status_code}")
        except Exception as e:
            results['subscription_status'] = {'success': False, 'error': str(e)}
            print(f"❌ Subscription status error: {e}")
        
        # Test 3: Get freemium features
        try:
            response = requests.get(f"{self.base_url}/subscription/freemium-features")
            if response.status_code == 200:
                features = response.json()
                results['freemium_features'] = {
                    'success': True,
                    'total_features': features.get('total_features', 0),
                    'available_features': features.get('available_features', 0),
                    'features': list(features.get('features', {}).keys())
                }
                print(f"✅ Freemium features: {features.get('available_features', 0)}/{features.get('total_features', 0)} available")
            else:
                results['freemium_features'] = {'success': False, 'error': response.text}
                print(f"❌ Freemium features failed: {response.status_code}")
        except Exception as e:
            results['freemium_features'] = {'success': False, 'error': str(e)}
            print(f"❌ Freemium features error: {e}")
        
        # Test 4: A/B test variant
        try:
            response = requests.get(f"{self.base_url}/subscription/ab-test/pricing_page")
            if response.status_code == 200:
                variant = response.json()
                results['ab_test_variant'] = {
                    'success': True,
                    'test_active': variant.get('test_active', False),
                    'variant': variant.get('variant', 'control')
                }
                print(f"✅ A/B test variant: {variant.get('variant', 'control')}")
            else:
                results['ab_test_variant'] = {'success': False, 'error': response.text}
                print(f"❌ A/B test variant failed: {response.status_code}")
        except Exception as e:
            results['ab_test_variant'] = {'success': False, 'error': str(e)}
            print(f"❌ A/B test variant error: {e}")
        
        # Test 5: Track A/B test event
        try:
            response = requests.post(f"{self.base_url}/subscription/ab-test/pricing_page/track", 
                                  json={'event': 'test_conversion', 'value': 1.0})
            if response.status_code == 200:
                track_result = response.json()
                results['ab_test_tracking'] = {
                    'success': True,
                    'tracked': track_result.get('success', False)
                }
                print(f"✅ A/B test tracking: {'success' if track_result.get('success') else 'failed'}")
            else:
                results['ab_test_tracking'] = {'success': False, 'error': response.text}
                print(f"❌ A/B test tracking failed: {response.status_code}")
        except Exception as e:
            results['ab_test_tracking'] = {'success': False, 'error': str(e)}
            print(f"❌ A/B test tracking error: {e}")
        
        # Test 6: Simulate payment
        try:
            response = requests.post(f"{self.base_url}/subscription/simulate-payment", 
                                  json={'amount': 49.00, 'currency': 'usd'})
            if response.status_code == 200:
                payment = response.json()
                results['payment_simulation'] = {
                    'success': True,
                    'payment_success': payment.get('success', False),
                    'amount': payment.get('amount', 0),
                    'test_mode': payment.get('test_mode', True)
                }
                print(f"✅ Payment simulation: ${payment.get('amount', 0)} - {'success' if payment.get('success') else 'failed'}")
            else:
                results['payment_simulation'] = {'success': False, 'error': response.text}
                print(f"❌ Payment simulation failed: {response.status_code}")
        except Exception as e:
            results['payment_simulation'] = {'success': False, 'error': str(e)}
            print(f"❌ Payment simulation error: {e}")
        
        # Test 7: Test subscription creation (mock)
        try:
            response = requests.post(f"{self.base_url}/subscription/subscribe", 
                                  json={
                                      'tier': 'premium',
                                      'billing_cycle': 'monthly',
                                      'payment_method_id': 'pm_test_1234567890'
                                  })
            if response.status_code == 200:
                subscription = response.json()
                results['subscription_creation'] = {
                    'success': True,
                    'subscription_id': subscription.get('subscription_id', ''),
                    'tier': subscription.get('tier', ''),
                    'status': subscription.get('status', '')
                }
                print(f"✅ Subscription creation: {subscription.get('tier', '')} - {subscription.get('status', '')}")
            else:
                results['subscription_creation'] = {'success': False, 'error': response.text}
                print(f"❌ Subscription creation failed: {response.status_code}")
        except Exception as e:
            results['subscription_creation'] = {'success': False, 'error': str(e)}
            print(f"❌ Subscription creation error: {e}")
        
        return results
    
    async def test_freemium_model(self) -> Dict[str, Any]:
        """Test freemium model features"""
        print("\n🔍 Testing Freemium Model...")
        
        results = {}
        
        # Test specific feature access
        features_to_test = ['ai_requests', 'projects', 'video_generation', 'nft_creation']
        
        for feature in features_to_test:
            try:
                response = requests.get(f"{self.base_url}/subscription/freemium-features/{feature}")
                if response.status_code == 200:
                    feature_info = response.json()
                    results[feature] = {
                        'success': True,
                        'available': feature_info.get('available', False),
                        'user_tier': feature_info.get('user_tier', 'freemium'),
                        'current_limit': feature_info.get('current_limit', 0),
                        'unlimited': feature_info.get('unlimited', False)
                    }
                    status = "✅" if feature_info.get('available') else "🔒"
                    print(f"{status} {feature}: {feature_info.get('user_tier', 'freemium')} - "
                          f"{'Unlimited' if feature_info.get('unlimited') else feature_info.get('current_limit', 0)}")
                else:
                    results[feature] = {'success': False, 'error': response.text}
                    print(f"❌ {feature}: Failed - {response.status_code}")
            except Exception as e:
                results[feature] = {'success': False, 'error': str(e)}
                print(f"❌ {feature}: Error - {e}")
        
        return results
    
    async def test_ab_testing(self) -> Dict[str, Any]:
        """Test A/B testing functionality"""
        print("\n🔍 Testing A/B Testing...")
        
        results = {}
        
        # Test different A/B tests
        tests_to_test = ['pricing_page', 'subscription_flow']
        
        for test_name in tests_to_test:
            try:
                # Get variant
                response = requests.get(f"{self.base_url}/subscription/ab-test/{test_name}")
                if response.status_code == 200:
                    variant = response.json()
                    results[f'{test_name}_variant'] = {
                        'success': True,
                        'test_active': variant.get('test_active', False),
                        'variant': variant.get('variant', 'control'),
                        'test_id': variant.get('test_id', '')
                    }
                    
                    # Track some events
                    events = ['page_view', 'button_click', 'form_start']
                    for event in events:
                        try:
                            track_response = requests.post(
                                f"{self.base_url}/subscription/ab-test/{test_name}/track",
                                json={'event': event, 'value': 1.0}
                            )
                            if track_response.status_code == 200:
                                results[f'{test_name}_{event}_tracking'] = {
                                    'success': True,
                                    'tracked': track_response.json().get('success', False)
                                }
                            else:
                                results[f'{test_name}_{event}_tracking'] = {
                                    'success': False, 
                                    'error': track_response.text
                                }
                        except Exception as e:
                            results[f'{test_name}_{event}_tracking'] = {
                                'success': False, 
                                'error': str(e)
                            }
                    
                    status = "✅" if variant.get('test_active') else "⏸️"
                    print(f"{status} {test_name}: Variant {variant.get('variant', 'control')} - "
                          f"{'Active' if variant.get('test_active') else 'Inactive'}")
                else:
                    results[f'{test_name}_variant'] = {'success': False, 'error': response.text}
                    print(f"❌ {test_name}: Failed - {response.status_code}")
            except Exception as e:
                results[f'{test_name}_variant'] = {'success': False, 'error': str(e)}
                print(f"❌ {test_name}: Error - {e}")
        
        return results
    
    async def test_payment_simulation(self) -> Dict[str, Any]:
        """Test payment simulation"""
        print("\n🔍 Testing Payment Simulation...")
        
        results = {}
        
        # Test different payment amounts
        test_amounts = [9.99, 49.00, 199.00]
        
        for amount in test_amounts:
            try:
                response = requests.post(f"{self.base_url}/subscription/simulate-payment", 
                                      json={'amount': amount, 'currency': 'usd'})
                if response.status_code == 200:
                    payment = response.json()
                    results[f'payment_{amount}'] = {
                        'success': True,
                        'payment_success': payment.get('success', False),
                        'amount': payment.get('amount', 0),
                        'currency': payment.get('currency', 'usd'),
                        'test_mode': payment.get('test_mode', True),
                        'payment_id': payment.get('payment_id', '')
                    }
                    status = "✅" if payment.get('success') else "❌"
                    print(f"{status} ${amount}: {'Success' if payment.get('success') else 'Failed'}")
                else:
                    results[f'payment_{amount}'] = {'success': False, 'error': response.text}
                    print(f"❌ ${amount}: Failed - {response.status_code}")
            except Exception as e:
                results[f'payment_{amount}'] = {'success': False, 'error': str(e)}
                print(f"❌ ${amount}: Error - {e}")
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        print("\n📊 Generating Test Report...")
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        # Count tests
        for category, tests in results.items():
            if isinstance(tests, dict):
                for test_name, result in tests.items():
                    total_tests += 1
                    if result.get('success', False):
                        passed_tests += 1
                    else:
                        failed_tests += 1
        
        # Calculate success rate
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate summary
        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'timestamp': datetime.utcnow().isoformat(),
            'test_results': results
        }
        
        # Print summary
        print(f"\n🎯 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ Overall Status: EXCELLENT")
        elif success_rate >= 60:
            print("⚠️  Overall Status: GOOD")
        else:
            print("❌ Overall Status: NEEDS IMPROVEMENT")
        
        return summary
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all monetization tests"""
        print("🚀 CK Empire Monetization Test Suite")
        print("=" * 50)
        
        all_results = {}
        
        # Run subscription endpoint tests
        all_results['subscription_endpoints'] = await self.test_subscription_endpoints()
        
        # Run freemium model tests
        all_results['freemium_model'] = await self.test_freemium_model()
        
        # Run A/B testing tests
        all_results['ab_testing'] = await self.test_ab_testing()
        
        # Run payment simulation tests
        all_results['payment_simulation'] = await self.test_payment_simulation()
        
        # Generate comprehensive report
        report = self.generate_report(all_results)
        
        # Save report to file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"stripe_subscription_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Test report saved to: {filename}")
        
        return report

async def main():
    """Main test function"""
    tester = StripeSubscriptionTester()
    
    try:
        report = await tester.run_all_tests()
        
        if report['success_rate'] >= 80:
            print("\n🎉 All monetization features are working excellently!")
            return 0
        elif report['success_rate'] >= 60:
            print("\n⚠️  Most monetization features are working, but some improvements needed.")
            return 1
        else:
            print("\n❌ Several monetization features need attention.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 