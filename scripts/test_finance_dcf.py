#!/usr/bin/env python3
"""
Comprehensive Finance DCF Test Script
Tests all finance endpoints with sample data
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8003"
API_ENDPOINTS = {
    "health": "/api/v1/finance/health",
    "roi": "/api/v1/finance/roi",
    "cac_ltv": "/api/v1/finance/cac-ltv",
    "cac_ltv_advanced": "/api/v1/finance/cac-ltv-advanced",
    "dcf": "/api/v1/finance/dcf",
    "dcf_advanced": "/api/v1/finance/dcf-advanced",
    "enhanced_roi": "/api/v1/finance/enhanced-roi",
    "strategy": "/api/v1/finance/strategy",
    "dashboard_graph": "/api/v1/finance/dashboard-graph"
}

def test_health_check():
    """Test finance health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}{API_ENDPOINTS['health']}")
        if response.status_code == 200:
            print("✅ Health Check PASSED")
            return True
        else:
            print(f"❌ Health Check FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check ERROR: {e}")
        return False

def test_roi_calculation():
    """Test ROI calculation endpoint"""
    try:
        data = {
            "target_amount": 20000,
            "initial_investment": 10000,
            "time_period": 1.0
        }
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['roi']}", json=data)
        if response.status_code == 200:
            print("✅ ROI Calculation PASSED")
            return True
        else:
            print(f"❌ ROI Calculation FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ROI Test ERROR: {e}")
        return False

def test_cac_ltv_calculation():
    """Test CAC/LTV calculation endpoint"""
    try:
        data = {
            "customer_acquisition_cost": 50,
            "customer_lifetime_value": 200,
            "average_order_value": 100,
            "purchase_frequency": 2.0,
            "customer_lifespan": 2.0
        }
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['cac_ltv']}", json=data)
        if response.status_code == 200:
            print("✅ CAC/LTV Calculation PASSED")
            return True
        else:
            print(f"❌ CAC/LTV Calculation FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CAC/LTV Test ERROR: {e}")
        return False

def test_advanced_cac_ltv():
    """Test advanced CAC/LTV analysis endpoint"""
    try:
        data = {
            "customer_acquisition_cost": 50,
            "customer_lifetime_value": 200,
            "marketing_spend": 5000,
            "new_customers": 100
        }
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['cac_ltv_advanced']}", json=data)
        if response.status_code == 200:
            print("✅ Advanced CAC/LTV PASSED")
            return True
        else:
            print(f"❌ Advanced CAC/LTV FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Advanced CAC/LTV Test ERROR: {e}")
        return False

def test_dcf_model():
    """Test DCF model creation endpoint"""
    try:
        data = {
            "initial_investment": 10000,
            "target_revenue": 20000,
            "growth_rate": 0.15,
            "discount_rate": 0.10,
            "time_period": 5
        }
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['dcf']}", json=data)
        if response.status_code == 200:
            print("✅ DCF Model PASSED")
            return True
        else:
            print(f"❌ DCF Model FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ DCF Model Test ERROR: {e}")
        return False

def test_advanced_dcf():
    """Test advanced DCF analysis endpoint"""
    try:
        data = {
            "initial_investment": 10000,
            "target_revenue": 20000,
            "growth_rate": 0.15,
            "discount_rate": 0.10,
            "time_period": 5
        }
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['dcf_advanced']}", json=data)
        if response.status_code == 200:
            print("✅ Advanced DCF PASSED")
            return True
        else:
            print(f"❌ Advanced DCF FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Advanced DCF Test ERROR: {e}")
        return False

def test_enhanced_roi():
    """Test enhanced ROI calculation endpoint"""
    try:
        data = {
            "target_amount": 20000,
            "initial_investment": 10000,
            "time_period": 1.0,
            "customer_acquisition_cost": 50,
            "customer_lifetime_value": 200,
            "marketing_spend": 5000,
            "new_customers": 100
        }
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['enhanced_roi']}", json=data)
        if response.status_code == 200:
            print("✅ Enhanced ROI PASSED")
            return True
        else:
            print(f"❌ Enhanced ROI FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Enhanced ROI Test ERROR: {e}")
        return False

def test_financial_strategy():
    """Test financial strategy endpoint"""
    try:
        data = {
            "current_revenue": 10000,
            "target_revenue": 20000,
            "current_cac": 50,
            "current_ltv": 200,
            "available_budget": 15000,
            "growth_timeline": 12
        }
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['strategy']}", json=data)
        if response.status_code == 200:
            print("✅ Financial Strategy PASSED")
            return True
        else:
            print(f"❌ Financial Strategy FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Financial Strategy Test ERROR: {e}")
        return False

def test_dashboard_graph():
    """Test dashboard graph endpoint"""
    try:
        data = {
            "graph_type": "roi_trend",
            "time_period": "12m",
            "include_projections": True
        }
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['dashboard_graph']}", json=data)
        if response.status_code == 200:
            print("✅ Dashboard Graph PASSED")
            return True
        else:
            print(f"❌ Dashboard Graph FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard Graph Test ERROR: {e}")
        return False

def run_comprehensive_test():
    """Run all finance tests"""
    print("=" * 60)
    print("🔍 Testing Finance Health Check...")
    health_result = test_health_check()
    
    print("🔍 Testing ROI Calculation...")
    roi_result = test_roi_calculation()
    
    print("🔍 Testing CAC/LTV Calculation...")
    cac_ltv_result = test_cac_ltv_calculation()
    
    print("🔍 Testing Advanced CAC/LTV Analysis...")
    advanced_cac_ltv_result = test_advanced_cac_ltv()
    
    print("🔍 Testing DCF Model Creation...")
    dcf_result = test_dcf_model()
    
    print("🔍 Testing Advanced DCF Model...")
    advanced_dcf_result = test_advanced_dcf()
    
    print("🔍 Testing Enhanced ROI...")
    enhanced_roi_result = test_enhanced_roi()
    
    print("🔍 Testing Financial Strategy...")
    strategy_result = test_financial_strategy()
    
    print("🔍 Testing Dashboard Graph...")
    dashboard_result = test_dashboard_graph()
    
    # Calculate results
    results = {
        "health_check": health_result,
        "roi_calculation": roi_result,
        "cac_ltv_calculation": cac_ltv_result,
        "advanced_cac_ltv": advanced_cac_ltv_result,
        "dcf_model": dcf_result,
        "advanced_dcf": advanced_dcf_result,
        "enhanced_roi": enhanced_roi_result,
        "financial_strategy": strategy_result,
        "dashboard_graph": dashboard_result
    }
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100
    
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Health Check              {'✅ PASSED' if health_result else '❌ FAILED'}")
    print(f"ROI Calculation           {'✅ PASSED' if roi_result else '❌ FAILED'}")
    print(f"CAC/LTV Calculation       {'✅ PASSED' if cac_ltv_result else '❌ FAILED'}")
    print(f"Advanced CAC/LTV          {'✅ PASSED' if advanced_cac_ltv_result else '❌ FAILED'}")
    print(f"DCF Model                 {'✅ PASSED' if dcf_result else '❌ FAILED'}")
    print(f"Advanced DCF              {'✅ PASSED' if advanced_dcf_result else '❌ FAILED'}")
    print(f"Enhanced ROI              {'✅ PASSED' if enhanced_roi_result else '❌ FAILED'}")
    print(f"Financial Strategy        {'✅ PASSED' if strategy_result else '❌ FAILED'}")
    print(f"Dashboard Graph           {'✅ PASSED' if dashboard_result else '❌ FAILED'}")
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"finance_dcf_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "results": results
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    if success_rate < 100:
        print("⚠️  Some tests failed. Please check the implementation.")
    else:
        print("🎉 All tests passed successfully!")
    
    return success_rate == 100

if __name__ == "__main__":
    run_comprehensive_test() 