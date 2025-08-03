#!/usr/bin/env python3
"""
Simple test script for Analytics Module
"""

import sys
import os
sys.path.append('.')

from analytics import analytics_manager

def test_analytics_module():
    """Test the analytics module functionality"""
    print("🧪 Testing Analytics Module...")
    
    try:
        # Test user metrics tracking
        print("📊 Testing user metrics tracking...")
        metric = analytics_manager.track_user_metric(
            user_id="test_user_123",
            session_duration=1800.0,  # 30 minutes
            page_views=15,
            conversion_rate=0.05,  # 5%
            revenue=250.0
        )
        print(f"✅ User metric tracked: {metric.user_id}")
        
        # Test A/B test
        print("🧪 Testing A/B test...")
        ab_result = analytics_manager.run_ab_test(
            test_id="test_ab_123",
            variant_a_data={"conversion_rate": 120, "sample_size": 1000},
            variant_b_data={"conversion_rate": 150, "sample_size": 1000},
            metric="conversion_rate"
        )
        print(f"✅ A/B test completed: Winner {ab_result.winner}")
        
        # Test analytics report generation
        print("📈 Testing analytics report generation...")
        report = analytics_manager.generate_analytics_report()
        print(f"✅ Analytics report generated: {report.total_users} users")
        
        # Test dashboard data
        print("📊 Testing dashboard data...")
        dashboard = analytics_manager.get_analytics_dashboard_data()
        print(f"✅ Dashboard data generated: {dashboard['status']}")
        
        # Test data-driven decision
        print("💡 Testing data-driven decision...")
        decision = analytics_manager.make_data_driven_decision(
            category="pricing",
            data={"conversion_rate": 0.05, "revenue": 5000, "user_count": 1000},
            confidence_threshold=0.95
        )
        print(f"✅ Data-driven decision: {decision['decision']}")
        
        print("🎉 All analytics module tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Analytics module test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_analytics_module()
    exit(0 if success else 1) 