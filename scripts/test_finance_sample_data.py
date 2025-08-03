#!/usr/bin/env python3
"""
Finance Features Test with Sample Data for CK Empire
Tests all finance features with realistic sample data
"""

import sys
import os
import json
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Mock config
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

def test_finance_with_sample_data():
    """Test finance features with realistic sample data"""
    print("🚀 CK Empire Finance Features Test with Sample Data")
    print("="*60)
    
    try:
        from finance import finance_manager
        print("✅ Finance manager imported successfully")
        
        # Sample data for testing
        sample_data = {
            "startup": {
                "current_revenue": 50000,
                "target_revenue": 200000,
                "current_cac": 75,
                "current_ltv": 300,
                "available_budget": 100000,
                "growth_timeline": 18
            },
            "scaleup": {
                "current_revenue": 500000,
                "target_revenue": 1000000,
                "current_cac": 120,
                "current_ltv": 800,
                "available_budget": 300000,
                "growth_timeline": 12
            },
            "enterprise": {
                "current_revenue": 2000000,
                "target_revenue": 5000000,
                "current_cac": 200,
                "current_ltv": 1500,
                "available_budget": 1000000,
                "growth_timeline": 24
            }
        }
        
        results = {}
        
        for company_type, data in sample_data.items():
            print(f"\n📊 Testing {company_type.upper()} Company Scenario:")
            print("-" * 40)
            
            # 1. ROI Analysis
            print("1️⃣ ROI Analysis:")
            roi_calc = finance_manager.calculate_roi_for_target(
                target_amount=data["target_revenue"],
                initial_investment=data["available_budget"],
                time_period=data["growth_timeline"] / 12
            )
            
            roi_percentage = roi_calc.calculate_roi()
            annualized_roi = roi_calc.calculate_annualized_roi()
            payback_period = roi_calc.calculate_payback_period()
            
            print(f"   • ROI: {roi_percentage:.2f}%")
            print(f"   • Annualized ROI: {annualized_roi:.2f}%")
            print(f"   • Payback Period: {payback_period:.1f} years")
            
            # 2. CAC/LTV Analysis
            print("2️⃣ CAC/LTV Analysis:")
            cac_ltv_calc = finance_manager.calculate_cac_ltv(
                customer_acquisition_cost=data["current_cac"],
                customer_lifetime_value=data["current_ltv"]
            )
            
            ltv_cac_ratio = cac_ltv_calc.calculate_ltv_cac_ratio()
            payback_period_cac = cac_ltv_calc.calculate_payback_period()
            profitability_score = cac_ltv_calc.get_profitability_score()
            recommendations = cac_ltv_calc.generate_recommendations()
            
            print(f"   • CAC: ${data['current_cac']}")
            print(f"   • LTV: ${data['current_ltv']}")
            print(f"   • LTV/CAC Ratio: {ltv_cac_ratio:.2f}")
            print(f"   • CAC Payback: {payback_period_cac:.1f} months")
            print(f"   • Profitability: {profitability_score}")
            print(f"   • Recommendations: {len(recommendations)} strategies")
            
            # 3. DCF Model
            print("3️⃣ DCF Model:")
            dcf_model = finance_manager.create_dcf_model(
                initial_investment=data["available_budget"],
                target_revenue=data["target_revenue"],
                growth_rate=0.20,  # 20% growth rate
                discount_rate=0.12,  # 12% discount rate
                time_period=5
            )
            
            npv = dcf_model.calculate_npv()
            irr = dcf_model.calculate_irr()
            present_value = dcf_model.calculate_present_value()
            
            print(f"   • NPV: ${npv:,.2f}")
            print(f"   • IRR: {irr:.2%}")
            print(f"   • Present Value: ${present_value:,.2f}")
            
            # 4. Financial Strategy
            print("4️⃣ Financial Strategy:")
            strategy = finance_manager.generate_financial_strategy(
                current_revenue=data["current_revenue"],
                target_revenue=data["target_revenue"],
                current_cac=data["current_cac"],
                current_ltv=data["current_ltv"],
                available_budget=data["available_budget"],
                growth_timeline=data["growth_timeline"]
            )
            
            growth_requirements = strategy.calculate_growth_requirements()
            timeline_breakdown = strategy.generate_timeline_breakdown()
            
            print(f"   • Required Investment: ${growth_requirements['required_investment']:,.2f}")
            print(f"   • Expected New Customers: {growth_requirements['required_new_customers']:,}")
            print(f"   • Expected ROI: {growth_requirements['expected_roi']:.2f}%")
            print(f"   • Risk Level: {growth_requirements['risk_level']}")
            print(f"   • Growth Strategy: {growth_requirements['growth_strategy']}")
            print(f"   • Timeline Breakdown: {len(timeline_breakdown)} months")
            
            # 5. Dashboard Graphs
            print("5️⃣ Dashboard Graphs:")
            graph_types = ["roi_trend", "cac_ltv", "revenue_forecast"]
            
            for graph_type in graph_types:
                graph_data = finance_manager.generate_dashboard_graph_data(
                    graph_type=graph_type,
                    time_period="12m",
                    include_projections=True
                )
                
                print(f"   • {graph_type.replace('_', ' ').title()}: {len(graph_data['data_points'])} data points")
                print(f"     - Trend: {graph_data['trend_analysis']}")
                print(f"     - Recommendations: {len(graph_data['recommendations'])}")
            
            # Store results
            results[company_type] = {
                "roi_analysis": {
                    "roi_percentage": roi_percentage,
                    "annualized_roi": annualized_roi,
                    "payback_period": payback_period
                },
                "cac_ltv_analysis": {
                    "cac": data["current_cac"],
                    "ltv": data["current_ltv"],
                    "ltv_cac_ratio": ltv_cac_ratio,
                    "payback_period": payback_period_cac,
                    "profitability_score": profitability_score,
                    "recommendations_count": len(recommendations)
                },
                "dcf_analysis": {
                    "npv": npv,
                    "irr": irr,
                    "present_value": present_value
                },
                "financial_strategy": {
                    "required_investment": growth_requirements['required_investment'],
                    "required_new_customers": growth_requirements['required_new_customers'],
                    "expected_roi": growth_requirements['expected_roi'],
                    "risk_level": growth_requirements['risk_level'],
                    "growth_strategy": growth_requirements['growth_strategy'],
                    "timeline_breakdown_count": len(timeline_breakdown)
                }
            }
            
            print(f"✅ {company_type.title()} analysis completed successfully!")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print("="*60)
        
        for company_type, result in results.items():
            print(f"\n{company_type.upper()}:")
            print(f"  • ROI: {result['roi_analysis']['roi_percentage']:.2f}%")
            print(f"  • LTV/CAC: {result['cac_ltv_analysis']['ltv_cac_ratio']:.2f}")
            print(f"  • NPV: ${result['dcf_analysis']['npv']:,.2f}")
            print(f"  • Risk: {result['financial_strategy']['risk_level']}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"finance_sample_data_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "sample_data": sample_data,
                "results": results,
                "summary": {
                    "total_scenarios": len(sample_data),
                    "successful_tests": len(results),
                    "features_tested": ["ROI", "CAC/LTV", "DCF", "Strategy", "Dashboard Graphs"]
                }
            }, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")
        print("\n🎉 All finance features tested successfully with sample data!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing finance features: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_finance_with_sample_data()
    sys.exit(0 if success else 1) 