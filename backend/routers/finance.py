from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

try:
    from ..finance import finance_manager
    from ..models import (
        ROICalculationRequest,
        ROICalculationResponse,
        DCFModelRequest,
        DCFModelResponse,
        ABTestRequest,
        ABTestResponse,
        FinancialReportRequest,
        FinancialReportResponse,
        BreakEvenRequest,
        BreakEvenResponse,
        CashFlowRequest,
        CashFlowResponse,
        FinancialRatiosRequest,
        FinancialRatiosResponse
    )
except ImportError:
    finance_manager = None
    ROICalculationRequest = None
    ROICalculationResponse = None
    DCFModelRequest = None
    DCFModelResponse = None
    ABTestRequest = None
    ABTestResponse = None
    FinancialReportRequest = None
    FinancialReportResponse = None
    BreakEvenRequest = None
    BreakEvenResponse = None
    CashFlowRequest = None
    CashFlowResponse = None
    FinancialRatiosRequest = None
    FinancialRatiosResponse = None

router = APIRouter(prefix="/finance", tags=["finance"])

@router.post("/roi", response_model=ROICalculationResponse)
async def calculate_roi(request: ROICalculationRequest):
    """Calculate ROI for a target amount"""
    try:
        logging.info(f"Calculating ROI for target: ${request.target_amount}")
        
        roi_calc = finance_manager.calculate_roi_for_target(
            target_amount=request.target_amount,
            initial_investment=request.initial_investment,
            time_period=request.time_period
        )
        
        return ROICalculationResponse(
            roi_percentage=roi_calc.calculate_roi(),
            annualized_roi=roi_calc.calculate_annualized_roi(),
            payback_period=roi_calc.calculate_payback_period(),
            initial_investment=roi_calc.initial_investment,
            total_return=roi_calc.total_return,
            time_period=roi_calc.time_period,
            target_amount=request.target_amount,
            status="calculated"
        )
        
    except Exception as e:
        logging.error(f"Error calculating ROI: {e}")
        raise HTTPException(status_code=500, detail=f"ROI calculation failed: {str(e)}")

@router.post("/dcf", response_model=DCFModelResponse)
async def create_dcf_model(request: DCFModelRequest):
    """Create a DCF model for revenue estimation"""
    try:
        logging.info(f"Creating DCF model for target: ${request.target_revenue}")
        
        dcf_model = finance_manager.create_dcf_model(
            initial_investment=request.initial_investment,
            target_revenue=request.target_revenue,
            growth_rate=request.growth_rate,
            discount_rate=request.discount_rate,
            time_period=request.time_period
        )
        
        return DCFModelResponse(
            npv=dcf_model.calculate_npv(),
            irr=dcf_model.calculate_irr(),
            present_value=dcf_model.calculate_present_value(),
            projected_revenue=dcf_model.projected_revenue,
            initial_investment=dcf_model.initial_investment,
            growth_rate=dcf_model.growth_rate,
            discount_rate=dcf_model.discount_rate,
            time_period=dcf_model.time_period,
            status="created"
        )
        
    except Exception as e:
        logging.error(f"Error creating DCF model: {e}")
        raise HTTPException(status_code=500, detail=f"DCF model creation failed: {str(e)}")

@router.post("/ab-test", response_model=ABTestResponse)
async def run_ab_test(request: ABTestRequest):
    """Run A/B test analysis"""
    try:
        logging.info(f"Running A/B test for metric: {request.metric}")
        
        result = finance_manager.run_ab_test(
            variant_a_data=request.variant_a_data,
            variant_b_data=request.variant_b_data,
            metric=request.metric
        )
        
        return ABTestResponse(
            variant_a=result.variant_a,
            variant_b=result.variant_b,
            confidence_level=result.confidence_level,
            winner=result.winner,
            p_value=result.p_value,
            sample_size=result.sample_size,
            metric=request.metric,
            status="completed"
        )
        
    except Exception as e:
        logging.error(f"Error running A/B test: {e}")
        raise HTTPException(status_code=500, detail=f"A/B test failed: {str(e)}")

@router.post("/report", response_model=FinancialReportResponse)
async def generate_financial_report(request: FinancialReportRequest):
    """Generate comprehensive financial report"""
    try:
        logging.info(f"Generating financial report for target: ${request.target_amount}")
        
        report = finance_manager.generate_financial_report(
            target_amount=request.target_amount,
            initial_investment=request.initial_investment
        )
        
        return FinancialReportResponse(
            target_amount=report["target_amount"],
            roi_analysis=report["roi_analysis"],
            dcf_analysis=report["dcf_analysis"],
            break_even_analysis=report["break_even_analysis"],
            cash_flow_forecast=report["cash_flow_forecast"],
            financial_ratios=report["financial_ratios"],
            recommendations=report["recommendations"],
            timestamp=report["timestamp"],
            status="generated"
        )
        
    except Exception as e:
        logging.error(f"Error generating financial report: {e}")
        raise HTTPException(status_code=500, detail=f"Financial report generation failed: {str(e)}")

@router.post("/break-even", response_model=BreakEvenResponse)
async def calculate_break_even(request: BreakEvenRequest):
    """Calculate break-even point"""
    try:
        logging.info(f"Calculating break-even for price: ${request.price_per_unit}")
        
        break_even = finance_manager.calculate_break_even_analysis(
            fixed_costs=request.fixed_costs,
            variable_cost_per_unit=request.variable_cost_per_unit,
            price_per_unit=request.price_per_unit
        )
        
        return BreakEvenResponse(
            break_even_units=break_even["break_even_units"],
            break_even_revenue=break_even["break_even_revenue"],
            contribution_margin=break_even["contribution_margin"],
            is_profitable=break_even["is_profitable"],
            fixed_costs=request.fixed_costs,
            variable_cost_per_unit=request.variable_cost_per_unit,
            price_per_unit=request.price_per_unit,
            status="calculated"
        )
        
    except Exception as e:
        logging.error(f"Error calculating break-even: {e}")
        raise HTTPException(status_code=500, detail=f"Break-even calculation failed: {str(e)}")

@router.post("/cash-flow", response_model=CashFlowResponse)
async def calculate_cash_flow_forecast(request: CashFlowRequest):
    """Calculate cash flow forecast"""
    try:
        logging.info(f"Calculating cash flow forecast for {request.months} months")
        
        cash_flow = finance_manager.calculate_cash_flow_forecast(
            initial_cash=request.initial_cash,
            monthly_revenue=request.monthly_revenue,
            monthly_expenses=request.monthly_expenses,
            months=request.months
        )
        
        return CashFlowResponse(
            forecast=cash_flow,
            initial_cash=request.initial_cash,
            monthly_revenue=request.monthly_revenue,
            monthly_expenses=request.monthly_expenses,
            months=request.months,
            status="calculated"
        )
        
    except Exception as e:
        logging.error(f"Error calculating cash flow forecast: {e}")
        raise HTTPException(status_code=500, detail=f"Cash flow calculation failed: {str(e)}")

@router.post("/ratios", response_model=FinancialRatiosResponse)
async def calculate_financial_ratios(request: FinancialRatiosRequest):
    """Calculate key financial ratios"""
    try:
        logging.info("Calculating financial ratios")
        
        ratios = finance_manager.calculate_financial_ratios(
            revenue=request.revenue,
            expenses=request.expenses,
            assets=request.assets,
            liabilities=request.liabilities,
            equity=request.equity
        )
        
        return FinancialRatiosResponse(
            profit_margin=ratios["profit_margin"],
            return_on_assets=ratios["return_on_assets"],
            return_on_equity=ratios["return_on_equity"],
            debt_to_equity=ratios["debt_to_equity"],
            current_ratio=ratios["current_ratio"],
            quick_ratio=ratios["quick_ratio"],
            revenue=request.revenue,
            expenses=request.expenses,
            assets=request.assets,
            liabilities=request.liabilities,
            equity=request.equity,
            status="calculated"
        )
        
    except Exception as e:
        logging.error(f"Error calculating financial ratios: {e}")
        raise HTTPException(status_code=500, detail=f"Financial ratios calculation failed: {str(e)}")

@router.get("/health")
async def finance_health_check():
    """Health check for finance module"""
    try:
        # Check if finance manager is properly initialized
        dcf_models_count = len(finance_manager.dcf_models)
        roi_calculations_count = len(finance_manager.roi_calculations)
        ab_tests_count = len(finance_manager.ab_tests)
        
        return {
            "status": "healthy",
            "dcf_models_count": dcf_models_count,
            "roi_calculations_count": roi_calculations_count,
            "ab_tests_count": ab_tests_count,
            "default_discount_rate": finance_manager.default_discount_rate,
            "default_growth_rate": finance_manager.default_growth_rate,
            "default_time_period": finance_manager.default_time_period,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Finance health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Finance module unhealthy: {str(e)}")

@router.get("/metrics")
async def get_finance_metrics():
    """Get finance module metrics"""
    try:
        return {
            "total_dcf_models": len(finance_manager.dcf_models),
            "total_roi_calculations": len(finance_manager.roi_calculations),
            "total_ab_tests": len(finance_manager.ab_tests),
            "average_roi": sum([calc.calculate_roi() for calc in finance_manager.roi_calculations.values()]) / len(finance_manager.roi_calculations) if finance_manager.roi_calculations else 0,
            "average_npv": sum([model.calculate_npv() for model in finance_manager.dcf_models.values()]) / len(finance_manager.dcf_models) if finance_manager.dcf_models else 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error getting finance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get finance metrics: {str(e)}") 