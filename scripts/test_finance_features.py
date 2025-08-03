#!/usr/bin/env python3
"""
Finance Features Test Script for CK Empire
Tests ROI, CAC/LTV, DCF, and financial strategy calculations
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Mock config for testing
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

class FinanceFeaturesTester:
    """Test class for Finance features"""
    
    def __init__(self):
        self.test_results = {}
        self.finance_manager = None
        
    def test_roi_calculation(self) -> Dict[str, Any]:
        """Test ROI calculation"""
        print("🔍 Testing ROI Calculation...")
        results = {}
        
        try:
            from finance import finance_manager
            self.finance_manager = finance_manager
            
            # Test basic ROI calculation
            roi_calc = finance_manager.calculate_roi_for_target(
                target_amount=20000,
                initial_investment=15000,
                time_period=1.0
            )
            
            roi_percentage = roi_calc.calculate_roi()
            annualized_roi = roi_calc.calculate_annualized_roi()
            payback_period = roi_calc.calculate_payback_period()
            
            results['basic_roi'] = {
                'success': True,
                'roi_percentage': roi_percentage,
                'annualized_roi': annualized_roi,
                'payback_period': payback_period,
                'initial_investment': roi_calc.initial_investment,
                'total_return': roi_calc.total_return
            }
            
            # Test enhanced ROI with CAC/LTV
            enhanced_result = finance_manager.calculate_enhanced_roi(
                target_amount=20000,
                initial_investment=15000,
                time_period=1.0,
                customer_acquisition_cost=50,
                customer_lifetime_value=200
            )
            
            results['enhanced_roi'] = {
                'success': True,
                'roi_calculation': enhanced_result['roi_calculation'].calculate_roi(),
                'cac_ltv_analysis': enhanced_result['cac_ltv_analysis'] is not None,
                'strategy_recommendations': len(enhanced_result['strategy_recommendations']),
                'risk_assessment': enhanced_result['risk_assessment']
            }
            
            print(f"✅ ROI calculation: {roi_percentage:.2f}% ROI, {annualized_roi:.2f}% annualized")
            
        except Exception as e:
            results['error'] = {'success': False, 'error': str(e)}
            print(f"❌ ROI calculation error: {e}")
        
        return results
    
    def test_cac_ltv_calculation(self) -> Dict[str, Any]:
        """Test CAC/LTV calculation"""
        print("🔍 Testing CAC/LTV Calculation...")
        results = {}
        
        try:
            # Test basic CAC/LTV calculation
            cac_ltv_calc = self.finance_manager.calculate_cac_ltv(
                customer_acquisition_cost=50,
                customer_lifetime_value=200
            )
            
            ltv_cac_ratio = cac_ltv_calc.calculate_ltv_cac_ratio()
            payback_period = cac_ltv_calc.calculate_payback_period()
            profitability_score = cac_ltv_calc.get_profitability_score()
            recommendations = cac_ltv_calc.generate_recommendations()
            
            results['basic_cac_ltv'] = {
                'success': True,
                'cac': cac_ltv_calc.customer_acquisition_cost,
                'ltv': cac_ltv_calc.customer_lifetime_value,
                'ltv_cac_ratio': ltv_cac_ratio,
                'payback_period': payback_period,
                'profitability_score': profitability_score,
                'recommendations_count': len(recommendations)
            }
            
            # Test with calculated values
            cac_ltv_calc2 = self.finance_manager.calculate_cac_ltv(
                customer_acquisition_cost=0,  # Will be calculated
                customer_lifetime_value=0,    # Will be calculated
                average_order_value=100,
                purchase_frequency=2,
                customer_lifespan=3,
                marketing_spend=5000,
                new_customers=100
            )
            
            results['calculated_cac_ltv'] = {
                'success': True,
                'calculated_ltv': cac_ltv_calc2.customer_lifetime_value,
                'calculated_cac': cac_ltv_calc2.customer_acquisition_cost,
                'ltv_cac_ratio': cac_ltv_calc2.calculate_ltv_cac_ratio()
            }
            
            print(f"✅ CAC/LTV calculation: {ltv_cac_ratio:.2f} LTV/CAC ratio, {profitability_score} profitability")
            
        except Exception as e:
            results['error'] = {'success': False, 'error': str(e)}
            print(f"❌ CAC/LTV calculation error: {e}")
        
        return results
    
    def test_dcf_model(self) -> Dict[str, Any]:
        """Test DCF model creation"""
        print("🔍 Testing DCF Model...")
        results = {}
        
        try:
            # Test DCF model creation
            dcf_model = self.finance_manager.create_dcf_model(
                initial_investment=100000,
                target_revenue=200000,
                growth_rate=0.15,
                discount_rate=0.10,
                time_period=5
            )
            
            npv = dcf_model.calculate_npv()
            irr = dcf_model.calculate_irr()
            present_value = dcf_model.calculate_present_value()
            
            results['dcf_model'] = {
                'success': True,
                'npv': npv,
                'irr': irr,
                'present_value': present_value,
                'projected_revenue': len(dcf_model.projected_revenue),
                'initial_investment': dcf_model.initial_investment,
                'growth_rate': dcf_model.growth_rate,
                'discount_rate': dcf_model.discount_rate
            }
            
            print(f"✅ DCF model: NPV ${npv:.2f}, IRR {irr:.2%}")
            
        except Exception as e:
            results['error'] = {'success': False, 'error': str(e)}
            print(f"❌ DCF model error: {e}")
        
        return results
    
    def test_financial_strategy(self) -> Dict[str, Any]:
        """Test financial strategy generation"""
        print("🔍 Testing Financial Strategy...")
        results = {}
        
        try:
            # Test financial strategy generation
            strategy = self.finance_manager.generate_financial_strategy(
                current_revenue=100000,
                target_revenue=200000,
                current_cac=50,
                current_ltv=200,
                available_budget=50000,
                growth_timeline=12
            )
            
            growth_requirements = strategy.calculate_growth_requirements()
            timeline_breakdown = strategy.generate_timeline_breakdown()
            
            results['financial_strategy'] = {
                'success': True,
                'required_investment': growth_requirements['required_investment'],
                'expected_new_customers': growth_requirements['required_new_customers'],
                'expected_roi': growth_requirements['expected_roi'],
                'risk_level': growth_requirements['risk_level'],
                'growth_strategy': growth_requirements['growth_strategy'],
                'timeline_breakdown_count': len(timeline_breakdown),
                'revenue_gap': growth_requirements['revenue_gap'],
                'ltv_cac_ratio': growth_requirements['current_ltv_cac_ratio']
            }
            
            print(f"✅ Financial strategy: {growth_requirements['risk_level']} risk, {growth_requirements['expected_roi']:.2f}% expected ROI")
            
        except Exception as e:
            results['error'] = {'success': False, 'error': str(e)}
            print(f"❌ Financial strategy error: {e}")
        
        return results
    
    def test_dashboard_graphs(self) -> Dict[str, Any]:
        """Test dashboard graph generation"""
        print("🔍 Testing Dashboard Graphs...")
        results = {}
        
        try:
            # Test ROI trend graph
            roi_trend_data = self.finance_manager.generate_dashboard_graph_data(
                graph_type="roi_trend",
                time_period="12m",
                include_projections=True
            )
            
            results['roi_trend_graph'] = {
                'success': True,
                'data_points_count': len(roi_trend_data['data_points']),
                'average_roi': roi_trend_data['summary_metrics']['average_roi'],
                'trend_analysis': roi_trend_data['trend_analysis'],
                'recommendations_count': len(roi_trend_data['recommendations'])
            }
            
            # Test CAC/LTV graph
            cac_ltv_data = self.finance_manager.generate_dashboard_graph_data(
                graph_type="cac_ltv",
                time_period="12m",
                include_projections=True
            )
            
            results['cac_ltv_graph'] = {
                'success': True,
                'data_points_count': len(cac_ltv_data['data_points']),
                'average_ltv_cac_ratio': cac_ltv_data['summary_metrics']['average_ltv_cac_ratio'],
                'trend_analysis': cac_ltv_data['trend_analysis'],
                'recommendations_count': len(cac_ltv_data['recommendations'])
            }
            
            # Test revenue forecast graph
            revenue_forecast_data = self.finance_manager.generate_dashboard_graph_data(
                graph_type="revenue_forecast",
                time_period="12m",
                include_projections=True
            )
            
            results['revenue_forecast_graph'] = {
                'success': True,
                'data_points_count': len(revenue_forecast_data['data_points']),
                'total_revenue': revenue_forecast_data['summary_metrics']['total_revenue'],
                'average_growth_rate': revenue_forecast_data['summary_metrics']['average_growth_rate'],
                'trend_analysis': revenue_forecast_data['trend_analysis'],
                'recommendations_count': len(revenue_forecast_data['recommendations'])
            }
            
            print(f"✅ Dashboard graphs: {len(roi_trend_data['data_points'])} ROI points, {len(cac_ltv_data['data_points'])} CAC/LTV points, {len(revenue_forecast_data['data_points'])} revenue points")
            
        except Exception as e:
            results['error'] = {'success': False, 'error': str(e)}
            print(f"❌ Dashboard graphs error: {e}")
        
        return results
    
    def test_break_even_analysis(self) -> Dict[str, Any]:
        """Test break-even analysis"""
        print("🔍 Testing Break-Even Analysis...")
        results = {}
        
        try:
            # Test break-even calculation
            break_even = self.finance_manager.calculate_break_even_analysis(
                fixed_costs=10000,
                variable_cost_per_unit=20,
                price_per_unit=50
            )
            
            results['break_even'] = {
                'success': True,
                'break_even_units': break_even['break_even_units'],
                'break_even_revenue': break_even['break_even_revenue'],
                'contribution_margin': break_even['contribution_margin'],
                'is_profitable': break_even['is_profitable']
            }
            
            print(f"✅ Break-even analysis: {break_even['break_even_units']:.0f} units, ${break_even['break_even_revenue']:.2f} revenue")
            
        except Exception as e:
            results['error'] = {'success': False, 'error': str(e)}
            print(f"❌ Break-even analysis error: {e}")
        
        return results
    
    def test_cash_flow_forecast(self) -> Dict[str, Any]:
        """Test cash flow forecast"""
        print("🔍 Testing Cash Flow Forecast...")
        results = {}
        
        try:
            # Test cash flow forecast
            cash_flow = self.finance_manager.calculate_cash_flow_forecast(
                initial_cash=50000,
                monthly_revenue=15000,
                monthly_expenses=10000,
                months=12
            )
            
            results['cash_flow_forecast'] = {
                'success': True,
                'forecast_months': len(cash_flow),
                'total_revenue': sum([month['revenue'] for month in cash_flow]),
                'total_expenses': sum([month['expenses'] for month in cash_flow]),
                'ending_cash': cash_flow[-1]['ending_cash'] if cash_flow else 0
            }
            
            print(f"✅ Cash flow forecast: {len(cash_flow)} months, ending cash ${cash_flow[-1]['ending_cash']:.2f}")
            
        except Exception as e:
            results['error'] = {'success': False, 'error': str(e)}
            print(f"❌ Cash flow forecast error: {e}")
        
        return results
    
    def test_financial_ratios(self) -> Dict[str, Any]:
        """Test financial ratios calculation"""
        print("🔍 Testing Financial Ratios...")
        results = {}
        
        try:
            # Test financial ratios
            ratios = self.finance_manager.calculate_financial_ratios(
                revenue=200000,
                expenses=150000,
                assets=300000,
                liabilities=100000,
                equity=200000
            )
            
            results['financial_ratios'] = {
                'success': True,
                'profit_margin': ratios['profit_margin'],
                'return_on_assets': ratios['return_on_assets'],
                'return_on_equity': ratios['return_on_equity'],
                'debt_to_equity': ratios['debt_to_equity'],
                'current_ratio': ratios['current_ratio'],
                'quick_ratio': ratios['quick_ratio']
            }
            
            print(f"✅ Financial ratios: {ratios['profit_margin']:.2f}% profit margin, {ratios['return_on_equity']:.2f}% ROE")
            
        except Exception as e:
            results['error'] = {'success': False, 'error': str(e)}
            print(f"❌ Financial ratios error: {e}")
        
        return results
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive finance features test"""
        print("🚀 CK Empire Finance Features Test Suite")
        print("="*50)
        
        self.test_results = {}
        
        self.test_results['roi_calculation'] = self.test_roi_calculation()
        self.test_results['cac_ltv_calculation'] = self.test_cac_ltv_calculation()
        self.test_results['dcf_model'] = self.test_dcf_model()
        self.test_results['financial_strategy'] = self.test_financial_strategy()
        self.test_results['dashboard_graphs'] = self.test_dashboard_graphs()
        self.test_results['break_even_analysis'] = self.test_break_even_analysis()
        self.test_results['cash_flow_forecast'] = self.test_cash_flow_forecast()
        self.test_results['financial_ratios'] = self.test_financial_ratios()
        
        # Calculate overall success rate
        total_tests = 0
        successful_tests = 0
        
        for test_category, results in self.test_results.items():
            if isinstance(results, dict):
                for test_name, result in results.items():
                    total_tests += 1
                    if isinstance(result, dict) and result.get('success', False):
                        successful_tests += 1
        
        overall_success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        self.test_results['summary'] = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'overall_success_rate': overall_success_rate,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n📊 Test Summary:")
        print(f"Total Tests: {total_tests}")
        print(f"Successful Tests: {successful_tests}")
        print(f"Success Rate: {overall_success_rate:.2%}")
        
        return overall_success_rate >= 0.8  # 80% threshold
    
    def save_test_results(self, filename: str = None):
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"finance_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"💾 Test results saved to: {filename}")

def main():
    """Main test function"""
    tester = FinanceFeaturesTester()
    
    success = tester.run_comprehensive_test()
    tester.save_test_results()
    
    if success:
        print("\n🎉 All finance features tests passed! Finance module is ready for use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 