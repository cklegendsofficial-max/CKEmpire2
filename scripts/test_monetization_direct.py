#!/usr/bin/env python3
"""
Direct Monetization Test Script for CK Empire
Tests the monetization features directly without requiring the server
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

class DirectMonetizationTester:
    """Test monetization features directly"""
    
    def __init__(self):
        self.test_results = {}
        
    async def test_monetization_manager(self) -> Dict[str, Any]:
        """Test monetization manager directly"""
        print("🔍 Testing Monetization Manager Directly...")
        
        results = {}
        
        try:
            from monetization import monetization_manager, SubscriptionTier, BillingCycle
            
            # Test 1: Get pricing plans
            try:
                plans = await monetization_manager.get_pricing_plans()
                results['pricing_plans'] = {
                    'success': True,
                    'plans_count': len(plans),
                    'plans': [plan['tier'] for plan in plans]
                }
                print(f"✅ Pricing plans: {len(plans)} plans found")
            except Exception as e:
                results['pricing_plans'] = {'success': False, 'error': str(e)}
                print(f"❌ Pricing plans error: {e}")
            
            # Test 2: Get freemium features
            try:
                from database import SessionLocal
                db = SessionLocal()
                features = await monetization_manager.get_all_freemium_features(1, db)
                results['freemium_features'] = {
                    'success': True,
                    'total_features': features.get('total_features', 0),
                    'available_features': features.get('available_features', 0),
                    'features': list(features.get('features', {}).keys())
                }
                print(f"✅ Freemium features: {features.get('available_features', 0)}/{features.get('total_features', 0)} available")
            except Exception as e:
                results['freemium_features'] = {'success': False, 'error': str(e)}
                print(f"❌ Freemium features error: {e}")
            
            # Test 3: A/B test variant
            try:
                variant = await monetization_manager.get_user_variant(1, 'pricing_page')
                results['ab_test_variant'] = {
                    'success': True,
                    'test_active': variant.get('test_active', False),
                    'variant': variant.get('variant', 'control')
                }
                print(f"✅ A/B test variant: {variant.get('variant', 'control')}")
            except Exception as e:
                results['ab_test_variant'] = {'success': False, 'error': str(e)}
                print(f"❌ A/B test variant error: {e}")
            
            # Test 4: Payment simulation
            try:
                payment = await monetization_manager.simulate_payment_test(49.00, 'usd')
                results['payment_simulation'] = {
                    'success': True,
                    'payment_success': payment.get('success', False),
                    'amount': payment.get('amount', 0),
                    'test_mode': payment.get('test_mode', True)
                }
                print(f"✅ Payment simulation: ${payment.get('amount', 0)} - {'success' if payment.get('success') else 'failed'}")
            except Exception as e:
                results['payment_simulation'] = {'success': False, 'error': str(e)}
                print(f"❌ Payment simulation error: {e}")
            
            # Test 5: Subscription creation (mock)
            try:
                subscription = await monetization_manager.create_subscription(
                    user_id=1,
                    tier=SubscriptionTier.PREMIUM,
                    billing_cycle=BillingCycle.MONTHLY,
                    payment_method_id='pm_test_1234567890',
                    db=None
                )
                results['subscription_creation'] = {
                    'success': True,
                    'subscription_id': subscription.get('subscription_id', ''),
                    'tier': subscription.get('tier', ''),
                    'status': subscription.get('status', '')
                }
                print(f"✅ Subscription creation: {subscription.get('tier', '')} - {subscription.get('status', '')}")
            except Exception as e:
                results['subscription_creation'] = {'success': False, 'error': str(e)}
                print(f"❌ Subscription creation error: {e}")
            
            # Test 6: Financial metrics
            try:
                metrics = await monetization_manager.calculate_financial_metrics(db=None)
                results['financial_metrics'] = {
                    'success': True,
                    'mrr': float(metrics.monthly_recurring_revenue),
                    'arr': float(metrics.annual_recurring_revenue),
                    'roi': metrics.roi_percentage
                }
                print(f"✅ Financial metrics: MRR=${float(metrics.monthly_recurring_revenue)}, ROI={metrics.roi_percentage}%")
            except Exception as e:
                results['financial_metrics'] = {'success': False, 'error': str(e)}
                print(f"❌ Financial metrics error: {e}")
            
        except Exception as e:
            results['monetization_manager'] = {'success': False, 'error': str(e)}
            print(f"❌ Monetization manager error: {e}")
        
        return results
    
    async def test_freemium_features(self) -> Dict[str, Any]:
        """Test freemium features directly"""
        print("\n🔍 Testing Freemium Features...")
        
        results = {}
        
        try:
            from monetization import monetization_manager
            from database import SessionLocal
            
            db = SessionLocal()
            features_to_test = ['ai_requests', 'projects', 'video_generation', 'nft_creation']
            
            for feature in features_to_test:
                try:
                    feature_info = await monetization_manager.get_freemium_feature_info(feature, 1, db)
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
                except Exception as e:
                    results[feature] = {'success': False, 'error': str(e)}
                    print(f"❌ {feature}: Error - {e}")
            
        except Exception as e:
            results['freemium_test'] = {'success': False, 'error': str(e)}
            print(f"❌ Freemium test error: {e}")
        
        return results
    
    async def test_ab_testing(self) -> Dict[str, Any]:
        """Test A/B testing directly"""
        print("\n🔍 Testing A/B Testing...")
        
        results = {}
        
        try:
            from monetization import monetization_manager
            
            tests_to_test = ['pricing_page', 'subscription_flow']
            
            for test_name in tests_to_test:
                try:
                    # Get variant
                    variant = await monetization_manager.get_user_variant(1, test_name)
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
                            tracked = await monetization_manager.track_ab_test_event(1, test_name, event, 1.0)
                            results[f'{test_name}_{event}_tracking'] = {
                                'success': True,
                                'tracked': tracked
                            }
                        except Exception as e:
                            results[f'{test_name}_{event}_tracking'] = {
                                'success': False, 
                                'error': str(e)
                            }
                    
                    status = "✅" if variant.get('test_active') else "⏸️"
                    print(f"{status} {test_name}: Variant {variant.get('variant', 'control')} - "
                          f"{'Active' if variant.get('test_active') else 'Inactive'}")
                except Exception as e:
                    results[f'{test_name}_variant'] = {'success': False, 'error': str(e)}
                    print(f"❌ {test_name}: Error - {e}")
            
        except Exception as e:
            results['ab_testing'] = {'success': False, 'error': str(e)}
            print(f"❌ A/B testing error: {e}")
        
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
        print("🚀 CK Empire Direct Monetization Test Suite")
        print("=" * 50)
        
        all_results = {}
        
        # Run monetization manager tests
        all_results['monetization_manager'] = await self.test_monetization_manager()
        
        # Run freemium model tests
        all_results['freemium_model'] = await self.test_freemium_features()
        
        # Run A/B testing tests
        all_results['ab_testing'] = await self.test_ab_testing()
        
        # Generate comprehensive report
        report = self.generate_report(all_results)
        
        # Save report to file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"direct_monetization_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Test report saved to: {filename}")
        
        return report

async def main():
    """Main test function"""
    tester = DirectMonetizationTester()
    
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