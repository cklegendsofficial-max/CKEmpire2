#!/usr/bin/env python3
"""
Simple test to check analytics module imports
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_analytics_import():
    """Test if analytics module can be imported"""
    try:
        print("Testing analytics module import...")
        from analytics import analytics_manager
        print("✅ Analytics module imported successfully")
        
        # Test basic functionality
        print("Testing analytics manager functionality...")
        metric = analytics_manager.track_user_metric(
            user_id="test_user",
            session_duration=1800.0,
            page_views=15,
            conversion_rate=0.05,
            revenue=250.0
        )
        print(f"✅ User metric tracked: {metric.user_id}")
        
        # Test A/B test
        ab_result = analytics_manager.run_ab_test(
            test_id="test_ab",
            variant_a_data={"conversion_rate": 120, "sample_size": 1000},
            variant_b_data={"conversion_rate": 150, "sample_size": 1000},
            metric="conversion_rate"
        )
        print(f"✅ A/B test completed: {ab_result.winner}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics import failed: {e}")
        return False

def test_models_import():
    """Test if analytics models can be imported"""
    try:
        print("Testing analytics models import...")
        from models import (
            UserMetricsRequest,
            UserMetricsResponse,
            AnalyticsReportResponse,
            GADataRequest,
            GADataResponse,
            DecisionRequest,
            DecisionResponse,
            AnalyticsDashboardResponse
        )
        print("✅ Analytics models imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Analytics models import failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Analytics Module Imports")
    print("=" * 40)
    
    success1 = test_analytics_import()
    success2 = test_models_import()
    
    if success1 and success2:
        print("\n🎉 All imports successful!")
    else:
        print("\n❌ Some imports failed!") 