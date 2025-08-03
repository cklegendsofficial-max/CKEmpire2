#!/usr/bin/env python3
"""
Simple Finance Features Test Script for CK Empire
"""

import sys
import os
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

def test_finance_features():
    """Test finance features"""
    print("🚀 Testing Finance Features...")
    
    try:
        from finance import finance_manager
        print("✅ Finance manager imported successfully")
        
        # Test ROI calculation
        roi_calc = finance_manager.calculate_roi_for_target(
            target_amount=20000,
            initial_investment=15000,
            time_period=1.0
        )
        
        roi_percentage = roi_calc.calculate_roi()
        print(f"✅ ROI calculation: {roi_percentage:.2f}%")
        
        # Test CAC/LTV calculation
        cac_ltv_calc = finance_manager.calculate_cac_ltv(
            customer_acquisition_cost=50,
            customer_lifetime_value=200
        )
        
        ltv_cac_ratio = cac_ltv_calc.calculate_ltv_cac_ratio()
        print(f"✅ CAC/LTV calculation: {ltv_cac_ratio:.2f} LTV/CAC ratio")
        
        # Test DCF model
        dcf_model = finance_manager.create_dcf_model(
            initial_investment=100000,
            target_revenue=200000,
            growth_rate=0.15,
            discount_rate=0.10,
            time_period=5
        )
        
        npv = dcf_model.calculate_npv()
        print(f"✅ DCF model: NPV ${npv:.2f}")
        
        # Test financial strategy
        strategy = finance_manager.generate_financial_strategy(
            current_revenue=100000,
            target_revenue=200000,
            current_cac=50,
            current_ltv=200,
            available_budget=50000,
            growth_timeline=12
        )
        
        growth_requirements = strategy.calculate_growth_requirements()
        print(f"✅ Financial strategy: {growth_requirements['risk_level']} risk")
        
        # Test dashboard graphs
        roi_trend_data = finance_manager.generate_dashboard_graph_data(
            graph_type="roi_trend",
            time_period="12m",
            include_projections=True
        )
        
        print(f"✅ Dashboard graphs: {len(roi_trend_data['data_points'])} data points")
        
        print("\n🎉 All finance features tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing finance features: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_finance_features()
    sys.exit(0 if success else 1) 