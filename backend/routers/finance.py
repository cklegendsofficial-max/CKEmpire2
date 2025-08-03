from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

try:
    from finance import finance_manager
    from models import (
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
        FinancialRatiosResponse,
        CACLTVRequest,
        CACLTVResponse,
        EnhancedROIRequest,
        EnhancedROIResponse,
        FinancialStrategyRequest,
        FinancialStrategyResponse,
        DashboardGraphRequest,
        DashboardGraphResponse
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
    CACLTVRequest = None
    CACLTVResponse = None
    EnhancedROIRequest = None
    EnhancedROIResponse = None
    FinancialStrategyRequest = None
    FinancialStrategyResponse = None
    DashboardGraphRequest = None
    DashboardGraphResponse = None

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

@router.post("/cac-ltv", response_model=CACLTVResponse)
async def calculate_cac_ltv(request: CACLTVRequest):
    """Calculate CAC/LTV metrics"""
    try:
        logging.info(f"Calculating CAC/LTV for CAC: ${request.customer_acquisition_cost}, LTV: ${request.customer_lifetime_value}")
        
        cac_ltv_calc = finance_manager.calculate_cac_ltv(
            customer_acquisition_cost=request.customer_acquisition_cost,
            customer_lifetime_value=request.customer_lifetime_value,
            average_order_value=request.average_order_value,
            purchase_frequency=request.purchase_frequency,
            customer_lifespan=request.customer_lifespan,
            marketing_spend=request.marketing_spend,
            new_customers=request.new_customers
        )
        
        return CACLTVResponse(
            cac=cac_ltv_calc.customer_acquisition_cost,
            ltv=cac_ltv_calc.customer_lifetime_value,
            ltv_cac_ratio=cac_ltv_calc.calculate_ltv_cac_ratio(),
            payback_period=cac_ltv_calc.calculate_payback_period(),
            profitability_score=cac_ltv_calc.get_profitability_score(),
            recommendations=cac_ltv_calc.generate_recommendations(),
            calculated_ltv=cac_ltv_calc.customer_lifetime_value,
            calculated_cac=cac_ltv_calc.customer_acquisition_cost,
            status="calculated"
        )
        
    except Exception as e:
        logging.error(f"Error calculating CAC/LTV: {e}")
        raise HTTPException(status_code=500, detail=f"CAC/LTV calculation failed: {str(e)}")

@router.post("/cac-ltv-advanced", response_model=Dict[str, Any])
async def calculate_advanced_cac_ltv(request: CACLTVRequest):
    """Calculate advanced CAC/LTV analysis with detailed insights"""
    try:
        logging.info(f"Calculating advanced CAC/LTV for CAC: ${request.customer_acquisition_cost}, LTV: ${request.customer_lifetime_value}")
        
        cac_ltv_calc = finance_manager.calculate_cac_ltv(
            customer_acquisition_cost=request.customer_acquisition_cost,
            customer_lifetime_value=request.customer_lifetime_value,
            average_order_value=request.average_order_value,
            purchase_frequency=request.purchase_frequency,
            customer_lifespan=request.customer_lifespan,
            marketing_spend=request.marketing_spend,
            new_customers=request.new_customers
        )
        
        ltv_cac_ratio = cac_ltv_calc.calculate_ltv_cac_ratio()
        payback_period = cac_ltv_calc.calculate_payback_period()
        
        # Advanced analysis
        profitability_score = cac_ltv_calc.get_profitability_score()
        recommendations = cac_ltv_calc.generate_recommendations()
        
        # Growth potential analysis
        growth_potential = "High" if ltv_cac_ratio >= 3.0 else "Medium" if ltv_cac_ratio >= 2.0 else "Low"
        
        # Scaling recommendations
        scaling_recommendations = []
        if ltv_cac_ratio >= 3.0:
            scaling_recommendations.append("Aggressive scaling recommended")
            scaling_recommendations.append("Increase marketing budget by 50-100%")
            scaling_recommendations.append("Explore new customer acquisition channels")
        elif ltv_cac_ratio >= 2.0:
            scaling_recommendations.append("Moderate scaling recommended")
            scaling_recommendations.append("Increase marketing budget by 25-50%")
            scaling_recommendations.append("Optimize existing channels")
        else:
            scaling_recommendations.append("Focus on optimization before scaling")
            scaling_recommendations.append("Reduce customer acquisition costs")
            scaling_recommendations.append("Improve customer retention")
        
        # Unit economics analysis
        unit_economics = {
            "customer_acquisition_cost": request.customer_acquisition_cost,
            "customer_lifetime_value": request.customer_lifetime_value,
            "ltv_cac_ratio": ltv_cac_ratio,
            "payback_period_months": payback_period,
            "profitability_score": profitability_score,
            "growth_potential": growth_potential
        }
        
        # Channel efficiency analysis (if marketing spend provided)
        channel_efficiency = None
        if request.marketing_spend and request.new_customers:
            cost_per_customer = request.marketing_spend / request.new_customers
            efficiency_score = "High" if cost_per_customer < request.customer_acquisition_cost else "Medium" if cost_per_customer <= request.customer_acquisition_cost * 1.2 else "Low"
            
            channel_efficiency = {
                "marketing_spend": request.marketing_spend,
                "customers_acquired": request.new_customers,
                "cost_per_customer": cost_per_customer,
                "efficiency_score": efficiency_score,
                "recommendation": "Optimize channels" if efficiency_score == "Low" else "Maintain current strategy"
            }
        
        return {
            "unit_economics": unit_economics,
            "channel_efficiency": channel_efficiency,
            "scaling_recommendations": scaling_recommendations,
            "detailed_recommendations": recommendations,
            "risk_assessment": {
                "risk_level": "Low" if ltv_cac_ratio >= 2.0 else "Medium" if ltv_cac_ratio >= 1.5 else "High",
                "sustainability_score": "High" if ltv_cac_ratio >= 3.0 else "Medium" if ltv_cac_ratio >= 2.0 else "Low",
                "scaling_readiness": "Ready" if ltv_cac_ratio >= 2.5 else "Needs optimization" if ltv_cac_ratio >= 1.5 else "Not ready"
            },
            "status": "calculated"
        }
        
    except Exception as e:
        logging.error(f"Error calculating advanced CAC/LTV: {e}")
        raise HTTPException(status_code=500, detail=f"Advanced CAC/LTV calculation failed: {str(e)}")

@router.post("/enhanced-roi", response_model=EnhancedROIResponse)
async def calculate_enhanced_roi(request: EnhancedROIRequest):
    """Calculate enhanced ROI with CAC/LTV analysis"""
    try:
        logging.info(f"Calculating enhanced ROI for target: ${request.target_amount}")
        
        enhanced_result = finance_manager.calculate_enhanced_roi(
            target_amount=request.target_amount,
            initial_investment=request.initial_investment,
            time_period=request.time_period,
            customer_acquisition_cost=request.customer_acquisition_cost,
            customer_lifetime_value=request.customer_lifetime_value,
            marketing_spend=request.marketing_spend,
            new_customers=request.new_customers
        )
        
        roi_calc = enhanced_result["roi_calculation"]
        cac_ltv_analysis = enhanced_result["cac_ltv_analysis"]
        
        # Convert CAC/LTV analysis to response model if available
        cac_ltv_response = None
        if cac_ltv_analysis:
            cac_ltv_response = CACLTVResponse(
                cac=cac_ltv_analysis.customer_acquisition_cost,
                ltv=cac_ltv_analysis.customer_lifetime_value,
                ltv_cac_ratio=cac_ltv_analysis.calculate_ltv_cac_ratio(),
                payback_period=cac_ltv_analysis.calculate_payback_period(),
                profitability_score=cac_ltv_analysis.get_profitability_score(),
                recommendations=cac_ltv_analysis.generate_recommendations(),
                calculated_ltv=cac_ltv_analysis.customer_lifetime_value,
                calculated_cac=cac_ltv_analysis.customer_acquisition_cost,
                status="calculated"
            )
        
        return EnhancedROIResponse(
            roi_percentage=roi_calc.calculate_roi(),
            annualized_roi=roi_calc.calculate_annualized_roi(),
            payback_period=roi_calc.calculate_payback_period(),
            initial_investment=roi_calc.initial_investment,
            total_return=roi_calc.total_return,
            time_period=roi_calc.time_period,
            target_amount=request.target_amount,
            cac_ltv_analysis=cac_ltv_response,
            strategy_recommendations=enhanced_result["strategy_recommendations"],
            risk_assessment=enhanced_result["risk_assessment"],
            status="calculated"
        )
        
    except Exception as e:
        logging.error(f"Error calculating enhanced ROI: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced ROI calculation failed: {str(e)}")

@router.post("/strategy", response_model=FinancialStrategyResponse)
async def generate_financial_strategy(request: FinancialStrategyRequest):
    """Generate comprehensive financial strategy"""
    try:
        logging.info(f"Generating financial strategy for revenue target: ${request.target_revenue}")
        
        strategy = finance_manager.generate_financial_strategy(
            current_revenue=request.current_revenue,
            target_revenue=request.target_revenue,
            current_cac=request.current_cac,
            current_ltv=request.current_ltv,
            available_budget=request.available_budget,
            growth_timeline=request.growth_timeline
        )
        
        growth_requirements = strategy.calculate_growth_requirements()
        timeline_breakdown = strategy.generate_timeline_breakdown()
        
        return FinancialStrategyResponse(
            recommended_investment=growth_requirements["required_investment"],
            expected_new_customers=growth_requirements["required_new_customers"],
            projected_revenue=request.target_revenue,
            expected_roi=growth_requirements["expected_roi"],
            risk_level=growth_requirements["risk_level"],
            growth_strategy=growth_requirements["growth_strategy"],
            timeline_breakdown=timeline_breakdown,
            key_metrics={
                "revenue_gap": growth_requirements["revenue_gap"],
                "ltv_cac_ratio": growth_requirements["current_ltv_cac_ratio"],
                "monthly_growth_rate": (growth_requirements["revenue_gap"] / request.current_revenue / request.growth_timeline * 100) if request.current_revenue > 0 else 0
            },
            status="generated"
        )
        
    except Exception as e:
        logging.error(f"Error generating financial strategy: {e}")
        raise HTTPException(status_code=500, detail=f"Financial strategy generation failed: {str(e)}")

@router.post("/dashboard-graph", response_model=DashboardGraphResponse)
async def generate_dashboard_graph(request: DashboardGraphRequest):
    """Generate dashboard graph data"""
    try:
        logging.info(f"Generating dashboard graph: {request.graph_type}")
        
        graph_data = finance_manager.generate_dashboard_graph_data(
            graph_type=request.graph_type,
            time_period=request.time_period,
            include_projections=request.include_projections
        )
        
        return DashboardGraphResponse(
            graph_type=graph_data["graph_type"],
            data_points=graph_data["data_points"],
            summary_metrics=graph_data["summary_metrics"],
            trend_analysis=graph_data["trend_analysis"],
            recommendations=graph_data["recommendations"],
            status="generated"
        )
        
    except Exception as e:
        logging.error(f"Error generating dashboard graph: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard graph generation failed: {str(e)}")

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

@router.post("/dcf-advanced", response_model=Dict[str, Any])
async def create_advanced_dcf_model(request: DCFModelRequest):
    """Create an advanced DCF model with detailed analysis"""
    try:
        logging.info(f"Creating advanced DCF model for target: ${request.target_revenue}")
        
        dcf_model = finance_manager.create_dcf_model(
            initial_investment=request.initial_investment,
            target_revenue=request.target_revenue,
            growth_rate=request.growth_rate,
            discount_rate=request.discount_rate,
            time_period=request.time_period
        )
        
        # Calculate additional metrics
        npv = dcf_model.calculate_npv()
        irr = dcf_model.calculate_irr()
        present_value = dcf_model.calculate_present_value()
        
        # Risk assessment
        risk_level = "Low" if npv > 0 and irr > 0.15 else "Medium" if npv > 0 else "High"
        
        # Investment recommendation
        if npv > 0 and irr > 0.20:
            recommendation = "Strong Buy - Excellent investment opportunity"
        elif npv > 0 and irr > 0.15:
            recommendation = "Buy - Good investment opportunity"
        elif npv > 0:
            recommendation = "Hold - Moderate investment opportunity"
        else:
            recommendation = "Avoid - Poor investment opportunity"
        
        # Sensitivity analysis
        sensitivity_analysis = {
            "discount_rate_impact": {
                "10%": dcf_model.calculate_npv(),
                "15%": finance_manager.create_dcf_model(
                    request.initial_investment,
                    request.target_revenue,
                    request.growth_rate,
                    0.15,
                    request.time_period
                ).calculate_npv(),
                "20%": finance_manager.create_dcf_model(
                    request.initial_investment,
                    request.target_revenue,
                    request.growth_rate,
                    0.20,
                    request.time_period
                ).calculate_npv()
            },
            "growth_rate_impact": {
                "10%": finance_manager.create_dcf_model(
                    request.initial_investment,
                    request.target_revenue,
                    0.10,
                    request.discount_rate,
                    request.time_period
                ).calculate_npv(),
                "15%": npv,
                "20%": finance_manager.create_dcf_model(
                    request.initial_investment,
                    request.target_revenue,
                    0.20,
                    request.discount_rate,
                    request.time_period
                ).calculate_npv()
            }
        }
        
        return {
            "dcf_model": {
                "npv": npv,
                "irr": irr,
                "present_value": present_value,
                "projected_revenue": dcf_model.projected_revenue,
                "initial_investment": dcf_model.initial_investment,
                "growth_rate": dcf_model.growth_rate,
                "discount_rate": dcf_model.discount_rate,
                "time_period": dcf_model.time_period
            },
            "risk_assessment": {
                "risk_level": risk_level,
                "npv_positive": npv > 0,
                "irr_acceptable": irr > 0.15,
                "payback_period": request.initial_investment / (npv / request.time_period) if npv > 0 else float('inf')
            },
            "investment_recommendation": {
                "recommendation": recommendation,
                "confidence_level": "High" if abs(irr - 0.15) > 0.05 else "Medium",
                "key_factors": [
                    f"NPV: ${npv:,.2f}",
                    f"IRR: {irr:.1%}",
                    f"Risk Level: {risk_level}"
                ]
            },
            "sensitivity_analysis": sensitivity_analysis,
            "status": "created"
        }
        
    except Exception as e:
        logging.error(f"Error creating advanced DCF model: {e}")
        raise HTTPException(status_code=500, detail=f"Advanced DCF model creation failed: {str(e)}")

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
        cac_ltv_calculations_count = len(finance_manager.cac_ltv_calculations)
        strategies_count = len(finance_manager.strategies)
        
        return {
            "status": "healthy",
            "dcf_models_count": dcf_models_count,
            "roi_calculations_count": roi_calculations_count,
            "ab_tests_count": ab_tests_count,
            "cac_ltv_calculations_count": cac_ltv_calculations_count,
            "strategies_count": strategies_count,
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
            "total_cac_ltv_calculations": len(finance_manager.cac_ltv_calculations),
            "total_strategies": len(finance_manager.strategies),
            "average_roi": sum([calc.calculate_roi() for calc in finance_manager.roi_calculations.values()]) / len(finance_manager.roi_calculations) if finance_manager.roi_calculations else 0,
            "average_npv": sum([model.calculate_npv() for model in finance_manager.dcf_models.values()]) / len(finance_manager.dcf_models) if finance_manager.dcf_models else 0,
            "average_ltv_cac_ratio": sum([calc.calculate_ltv_cac_ratio() for calc in finance_manager.cac_ltv_calculations.values()]) / len(finance_manager.cac_ltv_calculations) if finance_manager.cac_ltv_calculations else 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error getting finance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get finance metrics: {str(e)}") 