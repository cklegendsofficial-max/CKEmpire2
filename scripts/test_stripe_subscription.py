#!/usr/bin/env python3
"""
Stripe Subscription Test Script
Tests subscription creation, cancellation, and financial metrics
"""

import asyncio
import requests
import json
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from monetization import monetization_manager, SubscriptionTier, BillingCycle

class StripeSubscriptionTester:
    """Test Stripe subscription functionality"""
    
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
    
    async def test_pricing_plans(self):
        """Test pricing plans endpoint"""
        self.print_header("Testing Pricing Plans")
        
        try:
            # Test API endpoint
            response = requests.get(f"{self.base_url}/subscription/plans")
            if response.status_code == 200:
                plans = response.json()
                self.print_success(f"Retrieved {len(plans)} pricing plans")
                
                for plan in plans:
                    self.print_info(f"Plan: {plan['name']} - ${plan['price_monthly']}/month")
                
                return plans
            else:
                self.print_error(f"Failed to get pricing plans: {response.status_code}")
                return []
                
        except Exception as e:
            self.print_error(f"Error testing pricing plans: {e}")
            return []
    
    async def test_subscription_creation(self):
        """Test subscription creation"""
        self.print_header("Testing Subscription Creation")
        
        try:
            # Test data
            subscription_data = {
                "tier": "premium",
                "billing_cycle": "monthly",
                "payment_method_id": "pm_test_1234567890"
            }
            
            # Test API endpoint
            response = requests.post(
                f"{self.base_url}/subscription/subscribe",
                json=subscription_data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.print_success(f"Created subscription: {result['subscription_id']}")
                self.print_info(f"Tier: {result['tier']}, Status: {result['status']}")
                self.print_info(f"Price: ${result['price']}, Features: {len(result['features'])}")
                return result
            else:
                self.print_error(f"Failed to create subscription: {response.status_code}")
                return None
                
        except Exception as e:
            self.print_error(f"Error testing subscription creation: {e}")
            return None
    
    async def test_subscription_status(self):
        """Test subscription status endpoint"""
        self.print_header("Testing Subscription Status")
        
        try:
            response = requests.get(f"{self.base_url}/subscription/status")
            
            if response.status_code == 200:
                status = response.json()
                self.print_success("Retrieved subscription status")
                self.print_info(f"Tier: {status['tier']}, Status: {status['status']}")
                self.print_info(f"Features: {len(status['features'])}")
                return status
            else:
                self.print_error(f"Failed to get subscription status: {response.status_code}")
                return None
                
        except Exception as e:
            self.print_error(f"Error testing subscription status: {e}")
            return None
    
    async def test_subscription_cancellation(self):
        """Test subscription cancellation"""
        self.print_header("Testing Subscription Cancellation")
        
        try:
            response = requests.post(f"{self.base_url}/subscription/cancel")
            
            if response.status_code == 200:
                result = response.json()
                self.print_success("Subscription cancelled successfully")
                self.print_info(f"Status: {result['status']}")
                self.print_info(f"Cancel at period end: {result['cancel_at_period_end']}")
                return result
            else:
                self.print_error(f"Failed to cancel subscription: {response.status_code}")
                return None
                
        except Exception as e:
            self.print_error(f"Error testing subscription cancellation: {e}")
            return None
    
    async def test_financial_metrics(self):
        """Test financial metrics calculation"""
        self.print_header("Testing Financial Metrics")
        
        try:
            response = requests.get(f"{self.base_url}/subscription/metrics")
            
            if response.status_code == 200:
                metrics = response.json()
                self.print_success("Retrieved financial metrics")
                self.print_info(f"MRR: ${metrics['monthly_recurring_revenue']}")
                self.print_info(f"ARR: ${metrics['annual_recurring_revenue']}")
                self.print_info(f"Churn Rate: {metrics['churn_rate']}%")
                self.print_info(f"ROI: {metrics['roi_percentage']}%")
                return metrics
            else:
                self.print_error(f"Failed to get financial metrics: {response.status_code}")
                return None
                
        except Exception as e:
            self.print_error(f"Error testing financial metrics: {e}")
            return None
    
    async def test_user_limits(self):
        """Test user limits checking"""
        self.print_header("Testing User Limits")
        
        try:
            # Test different features
            features = ["ai_requests", "projects", "storage_gb", "team_members"]
            
            for feature in features:
                response = requests.get(f"{self.base_url}/subscription/limits?feature={feature}")
                
                if response.status_code == 200:
                    limits = response.json()
                    self.print_success(f"Checked limits for {feature}")
                    self.print_info(f"Tier: {limits['tier']}, Has Access: {limits['has_access']}")
                else:
                    self.print_error(f"Failed to check limits for {feature}: {response.status_code}")
                    
        except Exception as e:
            self.print_error(f"Error testing user limits: {e}")
    
    async def test_payment_integration(self):
        """Test payment integration"""
        self.print_header("Testing Payment Integration")
        
        try:
            response = requests.get(f"{self.base_url}/subscription/test-payment")
            
            if response.status_code == 200:
                payment_info = response.json()
                self.print_success("Payment integration test successful")
                self.print_info(f"Test Card: {payment_info['test_card']}")
                self.print_info(f"Test Amount: {payment_info['test_amount']}")
                return payment_info
            else:
                self.print_error(f"Failed to test payment integration: {response.status_code}")
                return None
                
        except Exception as e:
            self.print_error(f"Error testing payment integration: {e}")
            return None
    
    async def test_monetization_manager(self):
        """Test monetization manager directly"""
        self.print_header("Testing Monetization Manager")
        
        try:
            # Test pricing plans
            plans = await monetization_manager.get_pricing_plans()
            self.print_success(f"Retrieved {len(plans)} pricing plans from manager")
            
            # Test subscription status
            status = await monetization_manager.get_subscription_status(user_id=1, db=None)
            self.print_success("Retrieved subscription status from manager")
            self.print_info(f"Tier: {status['tier']}, Has Subscription: {status['has_subscription']}")
            
            # Test financial metrics
            metrics = await monetization_manager.calculate_financial_metrics(db=None)
            self.print_success("Calculated financial metrics from manager")
            self.print_info(f"MRR: ${metrics.monthly_recurring_revenue}")
            self.print_info(f"ROI: {metrics.roi_percentage}%")
            
        except Exception as e:
            self.print_error(f"Error testing monetization manager: {e}")
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")
        
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
        print("🚀 Starting Stripe Subscription Tests")
        print(f"Base URL: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Run tests
        await self.test_pricing_plans()
        await self.test_subscription_creation()
        await self.test_subscription_status()
        await self.test_subscription_cancellation()
        await self.test_financial_metrics()
        await self.test_user_limits()
        await self.test_payment_integration()
        await self.test_monetization_manager()
        
        # Print summary
        self.print_summary()

def main():
    """Main function"""
    tester = StripeSubscriptionTester()
    
    try:
        asyncio.run(tester.run_all_tests())
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 