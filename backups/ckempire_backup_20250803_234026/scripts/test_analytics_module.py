#!/usr/bin/env python3
"""
Comprehensive Analytics Module Test Script
Tests all analytics features including A/B testing, GA integration, and data-driven decisions
"""

import sys
import os
import requests
import json
import time
from datetime import datetime, timedelta
import random

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINTS = {
    "health": "/api/v1/analytics/health",
    "track": "/api/v1/analytics/track",
    "metrics": "/api/v1/analytics/metrics",
    "ab_test": "/api/v1/analytics/ab-test",
    "ab_tests": "/api/v1/analytics/ab-tests",
    "report": "/api/v1/analytics/report",
    "reports": "/api/v1/analytics/reports",
    "ga_integration": "/api/v1/analytics/ga-integration",
    "decision": "/api/v1/analytics/decision",
    "dashboard": "/api/v1/analytics/dashboard",
    "metrics_summary": "/api/v1/analytics/metrics-summary"
}

def test_health_check():
    """Test analytics health check endpoint"""
    print("🔍 Testing Analytics Health Check...")
    
    try:
        response = requests.get(f"{BASE_URL}{API_ENDPOINTS['health']}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data.get('status', 'unknown')}")
            print(f"   - User metrics count: {data.get('user_metrics_count', 0)}")
            print(f"   - A/B tests count: {data.get('ab_tests_count', 0)}")
            print(f"   - Reports count: {data.get('reports_count', 0)}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_track_user_metrics():
    """Test user metrics tracking"""
    print("\n📊 Testing User Metrics Tracking...")
    
    try:
        # Generate mock user metrics
        mock_metrics = {
            "user_id": f"user_{int(time.time())}",
            "session_duration": random.uniform(300, 3600),  # 5-60 minutes
            "page_views": random.randint(1, 50),
            "conversion_rate": random.uniform(0.01, 0.15),  # 1-15%
            "revenue": random.uniform(10, 500)
        }
        
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['track']}", json=mock_metrics)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User metrics tracked successfully")
            print(f"   - User ID: {data.get('user_id')}")
            print(f"   - Session Duration: {data.get('session_duration', 0):.1f}s")
            print(f"   - Page Views: {data.get('page_views', 0)}")
            print(f"   - Conversion Rate: {data.get('conversion_rate', 0):.2%}")
            print(f"   - Revenue: ${data.get('revenue', 0):.2f}")
            return True
        else:
            print(f"❌ Failed to track metrics: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Metrics tracking error: {e}")
        return False

def test_get_user_metrics():
    """Test getting user metrics"""
    print("\n📈 Testing Get User Metrics...")
    
    try:
        response = requests.get(f"{BASE_URL}{API_ENDPOINTS['metrics']}")
        if response.status_code == 200:
            metrics = response.json()
            print(f"✅ Retrieved {len(metrics)} user metrics")
            if metrics:
                latest = metrics[0]
                print(f"   - Latest user: {latest.get('user_id')}")
                print(f"   - Revenue: ${latest.get('revenue', 0):.2f}")
            return True
        else:
            print(f"❌ Failed to get metrics: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get metrics error: {e}")
        return False

def test_ab_test():
    """Test A/B testing functionality"""
    print("\n🧪 Testing A/B Test...")
    
    try:
        # Generate mock A/B test data
        ab_test_data = {
            "test_id": f"ab_test_{int(time.time())}",
            "variant_a_data": {
                "conversion_rate": random.randint(50, 100),
                "sample_size": 1000
            },
            "variant_b_data": {
                "conversion_rate": random.randint(50, 100),
                "sample_size": 1000
            },
            "metric": "conversion_rate"
        }
        
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['ab_test']}", json=ab_test_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ A/B test completed successfully")
            print(f"   - Test ID: {data.get('test_id')}")
            print(f"   - Variant A Rate: {data.get('variant_a', {}).get('rate', 0):.2%}")
            print(f"   - Variant B Rate: {data.get('variant_b', {}).get('rate', 0):.2%}")
            print(f"   - Winner: {data.get('winner')}")
            print(f"   - Confidence: {data.get('confidence_level', 0):.1f}%")
            print(f"   - P-value: {data.get('p_value', 0):.4f}")
            return True
        else:
            print(f"❌ A/B test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ A/B test error: {e}")
        return False

def test_get_ab_tests():
    """Test getting all A/B test results"""
    print("\n📋 Testing Get A/B Tests...")
    
    try:
        response = requests.get(f"{BASE_URL}{API_ENDPOINTS['ab_tests']}")
        if response.status_code == 200:
            tests = response.json()
            print(f"✅ Retrieved {len(tests)} A/B test results")
            if tests:
                latest = tests[0]
                print(f"   - Latest test: {latest.get('test_id')}")
                print(f"   - Winner: {latest.get('winner')}")
                print(f"   - Confidence: {latest.get('confidence_level', 0):.1f}%")
            return True
        else:
            print(f"❌ Failed to get A/B tests: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get A/B tests error: {e}")
        return False

def test_generate_analytics_report():
    """Test analytics report generation"""
    print("\n📊 Testing Analytics Report Generation...")
    
    try:
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['report']}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics report generated successfully")
            print(f"   - Total Users: {data.get('total_users', 0)}")
            print(f"   - Total Revenue: ${data.get('total_revenue', 0):.2f}")
            print(f"   - Avg Session Duration: {data.get('average_session_duration', 0):.1f}s")
            print(f"   - Conversion Rate: {data.get('conversion_rate', 0):.2%}")
            print(f"   - User Retention: {data.get('user_retention_rate', 0):.2%}")
            print(f"   - Revenue per User: ${data.get('revenue_per_user', 0):.2f}")
            return True
        else:
            print(f"❌ Report generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Report generation error: {e}")
        return False

def test_ga_integration():
    """Test Google Analytics integration"""
    print("\n🔗 Testing GA Integration...")
    
    try:
        ga_request = {
            "property_id": "GA_PROPERTY_123",
            "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "metrics": ["page_views", "unique_visitors", "bounce_rate", "avg_session_duration"]
        }
        
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['ga_integration']}", json=ga_request)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GA integration successful")
            print(f"   - Property ID: {data.get('property_id')}")
            print(f"   - Page Views: {data.get('metrics', {}).get('page_views', 0)}")
            print(f"   - Unique Visitors: {data.get('metrics', {}).get('unique_visitors', 0)}")
            print(f"   - Bounce Rate: {data.get('metrics', {}).get('bounce_rate', 0):.2%}")
            print(f"   - Avg Session Duration: {data.get('metrics', {}).get('avg_session_duration', 0):.1f}s")
            return True
        else:
            print(f"❌ GA integration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GA integration error: {e}")
        return False

def test_data_driven_decision():
    """Test data-driven decision making"""
    print("\n💡 Testing Data-Driven Decision...")
    
    try:
        # Test different decision categories
        categories = ["pricing", "marketing", "product", "user_experience"]
        
        for category in categories:
            decision_data = {
                "category": category,
                "data": {
                    "conversion_rate": random.uniform(0.01, 0.15),
                    "revenue_per_user": random.uniform(10, 200),
                    "user_retention_rate": random.uniform(0.3, 0.8),
                    "bounce_rate": random.uniform(0.2, 0.7),
                    "avg_session_duration": random.uniform(60, 600),
                    "traffic_sources": {
                        "organic": {"visits": 1000, "conversion_rate": 0.04},
                        "direct": {"visits": 500, "conversion_rate": 0.05},
                        "social": {"visits": 200, "conversion_rate": 0.02}
                    },
                    "device_categories": {
                        "desktop": 0.6,
                        "mobile": 0.35,
                        "tablet": 0.05
                    }
                },
                "confidence_threshold": 0.95
            }
            
            response = requests.post(f"{BASE_URL}{API_ENDPOINTS['decision']}", json=decision_data)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {category.title()} decision made")
                print(f"   - Decision: {data.get('decision')}")
                print(f"   - Confidence: {data.get('confidence', 0):.2f}")
                print(f"   - Data Points: {data.get('data_points', 0)}")
                print(f"   - Reasoning: {len(data.get('reasoning', []))} recommendations")
            else:
                print(f"❌ {category} decision failed: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Data-driven decision error: {e}")
        return False

def test_analytics_dashboard():
    """Test analytics dashboard data retrieval"""
    print("\n📈 Testing Analytics Dashboard...")
    
    try:
        response = requests.get(f"{BASE_URL}{API_ENDPOINTS['dashboard']}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard data retrieved successfully")
            print(f"   - Summary available: {'summary' in data}")
            print(f"   - User metrics: {len(data.get('user_metrics', []))}")
            print(f"   - A/B test results: {len(data.get('ab_test_results', []))}")
            print(f"   - Top pages: {len(data.get('top_pages', []))}")
            print(f"   - Revenue trends: {len(data.get('revenue_trends', []))}")
            print(f"   - Conversion funnel: {len(data.get('conversion_funnel', []))}")
            return True
        else:
            print(f"❌ Dashboard retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return False

def test_metrics_summary():
    """Test metrics summary endpoint"""
    print("\n📊 Testing Metrics Summary...")
    
    try:
        response = requests.get(f"{BASE_URL}{API_ENDPOINTS['metrics_summary']}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Metrics summary retrieved")
            print(f"   - Total Users: {data.get('total_users', 0)}")
            print(f"   - Total Revenue: ${data.get('total_revenue', 0):.2f}")
            print(f"   - Conversion Rate: {data.get('conversion_rate', 0):.2%}")
            print(f"   - User Retention: {data.get('user_retention_rate', 0):.2%}")
            return True
        else:
            print(f"❌ Metrics summary failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Metrics summary error: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive analytics module test"""
    print("🚀 Starting Comprehensive Analytics Module Test")
    print("=" * 60)
    
    test_results = []
    
    # Test all endpoints
    tests = [
        ("Health Check", test_health_check),
        ("Track User Metrics", test_track_user_metrics),
        ("Get User Metrics", test_get_user_metrics),
        ("A/B Test", test_ab_test),
        ("Get A/B Tests", test_get_ab_tests),
        ("Generate Analytics Report", test_generate_analytics_report),
        ("GA Integration", test_ga_integration),
        ("Data-Driven Decision", test_data_driven_decision),
        ("Analytics Dashboard", test_analytics_dashboard),
        ("Metrics Summary", test_metrics_summary)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 ANALYTICS MODULE TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All analytics tests passed! Analytics module is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the backend server and endpoints.")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 