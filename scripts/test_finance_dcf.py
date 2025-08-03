#!/usr/bin/env python3
"""
Test script for Finance DCF Model with sample data
Tests ROI, CAC/LTV, and DCF calculations
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# API Configuration
BASE_URL = "http://localhost:8000"
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

def test_roi_calculation():
    """Test ROI calculation with sample data"""
    print("🔍 Testing ROI Calculation...")
    
    sample_data = {
        "target_amount": 50000,
        "initial_investment": 20000,
        "time_period": 2.0
    }
    
    try:
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['roi']}", json=sample_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ROI Test PASSED")
            print(f"   ROI Percentage: {result['roi_percentage']:.2f}%")
            print(f"   Annualized ROI: {result['annualized_roi']:.2f}%")
            print(f"   Payback Period: {result['payback_period']:.1f} years")
            return True
        else:
            print(f"❌ ROI Test FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ROI Test ERROR: {e}")
        return False

def test_cac_ltv_calculation():
    """Test CAC/LTV calculation with sample data"""
    print("\n🔍 Testing CAC/LTV Calculation...")
    
    sample_data = {
        "customer_acquisition_cost": 150,
        "customer_lifetime_value": 450,
        "marketing_spend": 15000,
        "new_customers": 100
    }
    
    try:
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['cac_ltv']}", json=sample_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ CAC/LTV Test PASSED")
            print(f"   LTV/CAC Ratio: {result['ltv_cac_ratio']:.2f}")
            print(f"   Payback Period: {result['payback_period']:.1f} months")
            print(f"   Profitability Score: {result['profitability_score']}")
            return True
        else:
            print(f"❌ CAC/LTV Test FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CAC/LTV Test ERROR: {e}")
        return False

def test_cac_ltv_advanced():
    """Test advanced CAC/LTV analysis"""
    print("\n🔍 Testing Advanced CAC/LTV Analysis...")
    
    sample_data = {
        "customer_acquisition_cost": 150,
        "customer_lifetime_value": 450,
        "marketing_spend": 15000,
        "new_customers": 100
    }
    
    try:
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['cac_ltv_advanced']}", json=sample_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Advanced CAC/LTV Test PASSED")
            print(f"   Growth Potential: {result['unit_economics']['growth_potential']}")
            print(f"   Risk Level: {result['risk_assessment']['risk_level']}")
            print(f"   Scaling Readiness: {result['risk_assessment']['scaling_readiness']}")
            print(f"   Scaling Recommendations: {len(result['scaling_recommendations'])} items")
            return True
        else:
            print(f"❌ Advanced CAC/LTV Test FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Advanced CAC/LTV Test ERROR: {e}")
        return False

def test_dcf_model():
    """Test DCF model creation"""
    print("\n🔍 Testing DCF Model Creation...")
    
    sample_data = {
        "initial_investment": 100000,
        "target_revenue": 300000,
        "growth_rate": 0.15,
        "discount_rate": 0.10,
        "time_period": 5
    }
    
    try:
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['dcf']}", json=sample_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ DCF Model Test PASSED")
            print(f"   NPV: ${result['npv']:,.2f}")
            print(f"   IRR: {result['irr']:.1%}")
            print(f"   Present Value: ${result['present_value']:,.2f}")
            print(f"   Projected Revenue Years: {len(result['projected_revenue'])}")
            return True
        else:
            print(f"❌ DCF Model Test FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ DCF Model Test ERROR: {e}")
        return False

def test_dcf_advanced():
    """Test advanced DCF model with detailed analysis"""
    print("\n🔍 Testing Advanced DCF Model...")
    
    sample_data = {
        "initial_investment": 100000,
        "target_revenue": 300000,
        "growth_rate": 0.15,
        "discount_rate": 0.10,
        "time_period": 5
    }
    
    try:
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['dcf_advanced']}", json=sample_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Advanced DCF Test PASSED")
            print(f"   Risk Level: {result['risk_assessment']['risk_level']}")
            print(f"   Recommendation: {result['investment_recommendation']['recommendation']}")
            print(f"   Confidence Level: {result['investment_recommendation']['confidence_level']}")
            print(f"   Sensitivity Analysis: {len(result['sensitivity_analysis']['discount_rate_impact'])} scenarios")
            return True
        else:
            print(f"❌ Advanced DCF Test FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Advanced DCF Test ERROR: {e}")
        return False

def test_enhanced_roi():
    """Test enhanced ROI with CAC/LTV analysis"""
    print("\n🔍 Testing Enhanced ROI...")
    
    sample_data = {
        "target_amount": 50000,
        "initial_investment": 20000,
        "time_period": 2.0,
        "customer_acquisition_cost": 150,
        "customer_lifetime_value": 450,
        "marketing_spend": 15000,
        "new_customers": 100
    }
    
    try:
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['enhanced_roi']}", json=sample_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Enhanced ROI Test PASSED")
            print(f"   ROI Percentage: {result['roi_percentage']:.2f}%")
            print(f"   Risk Assessment: {result['risk_assessment']}")
            print(f"   Strategy Recommendations: {len(result['strategy_recommendations'])} items")
            return True
        else:
            print(f"❌ Enhanced ROI Test FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Enhanced ROI Test ERROR: {e}")
        return False

def test_financial_strategy():
    """Test financial strategy generation"""
    print("\n🔍 Testing Financial Strategy...")
    
    sample_data = {
        "current_revenue": 100000,
        "target_revenue": 250000,
        "current_cac": 200,
        "current_ltv": 600,
        "available_budget": 50000,
        "growth_timeline": 12
    }
    
    try:
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['strategy']}", json=sample_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Financial Strategy Test PASSED")
            print(f"   Recommended Investment: ${result['recommended_investment']:,.2f}")
            print(f"   Expected New Customers: {result['expected_new_customers']}")
            print(f"   Risk Level: {result['risk_level']}")
            print(f"   Growth Strategy: {result['growth_strategy']}")
            return True
        else:
            print(f"❌ Financial Strategy Test FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Financial Strategy Test ERROR: {e}")
        return False

def test_dashboard_graph():
    """Test dashboard graph generation"""
    print("\n🔍 Testing Dashboard Graph...")
    
    sample_data = {
        "graph_type": "roi_trend",
        "time_period": "12m",
        "include_projections": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}{API_ENDPOINTS['dashboard_graph']}", json=sample_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Dashboard Graph Test PASSED")
            print(f"   Graph Type: {result['graph_type']}")
            print(f"   Data Points: {len(result['data_points'])}")
            print(f"   Summary Metrics: {len(result['summary_metrics'])} items")
            print(f"   Recommendations: {len(result['recommendations'])} items")
            return True
        else:
            print(f"❌ Dashboard Graph Test FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard Graph Test ERROR: {e}")
        return False

def test_health_check():
    """Test finance module health check"""
    print("\n🔍 Testing Finance Health Check...")
    
    try:
        response = requests.get(f"{BASE_URL}{API_ENDPOINTS['health']}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health Check PASSED")
            print(f"   Status: {result['status']}")
            print(f"   DCF Models: {result['dcf_models_count']}")
            print(f"   ROI Calculations: {result['roi_calculations_count']}")
            print(f"   CAC/LTV Calculations: {result['cac_ltv_calculations_count']}")
            return True
        else:
            print(f"❌ Health Check FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check ERROR: {e}")
        return False

def run_comprehensive_test():
    """Run all finance tests"""
    print("🚀 Starting Comprehensive Finance Module Test")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("ROI Calculation", test_roi_calculation),
        ("CAC/LTV Calculation", test_cac_ltv_calculation),
        ("Advanced CAC/LTV", test_cac_ltv_advanced),
        ("DCF Model", test_dcf_model),
        ("Advanced DCF", test_dcf_advanced),
        ("Enhanced ROI", test_enhanced_roi),
        ("Financial Strategy", test_financial_strategy),
        ("Dashboard Graph", test_dashboard_graph)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"finance_dcf_test_results_{timestamp}.json"
    
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total,
        "passed_tests": passed,
        "success_rate": passed/total*100,
        "results": [
            {
                "test_name": test_name,
                "status": "PASSED" if success else "FAILED"
            }
            for test_name, success in results
        ]
    }
    
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    if passed == total:
        print("🎉 All tests passed! Finance module is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 