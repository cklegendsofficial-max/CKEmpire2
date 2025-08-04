#!/usr/bin/env python3
"""
Finance Module for CKEmpire
Handles DCF modeling, ROI calculations, and A/B testing
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
from pathlib import Path
import math

# Optional imports for advanced financial calculations
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logging.warning("Pandas not available. Advanced financial calculations will be limited.")

@dataclass
class DCFModel:
    """Discounted Cash Flow model for revenue estimation"""
    initial_investment: float
    projected_revenue: List[float]
    growth_rate: float
    discount_rate: float
    time_period: int  # years
    
    def calculate_present_value(self) -> float:
        """Calculate present value of future cash flows"""
        pv = 0
        for i, revenue in enumerate(self.projected_revenue):
            pv += revenue / ((1 + self.discount_rate) ** (i + 1))
        return pv
    
    def calculate_npv(self) -> float:
        """Calculate Net Present Value"""
        pv = self.calculate_present_value()
        return pv - self.initial_investment
    
    def calculate_irr(self) -> float:
        """Calculate Internal Rate of Return (simplified)"""
        # Simplified IRR calculation
        total_cash_flow = sum(self.projected_revenue)
        if total_cash_flow <= self.initial_investment:
            return 0.0
        
        # Simple approximation
        return (total_cash_flow - self.initial_investment) / self.initial_investment

@dataclass
class ROICalculation:
    """ROI calculation model"""
    initial_investment: float
    total_return: float
    time_period: float  # years
    
    def calculate_roi(self) -> float:
        """Calculate Return on Investment"""
        if self.initial_investment == 0:
            return 0.0
        return ((self.total_return - self.initial_investment) / self.initial_investment) * 100
    
    def calculate_annualized_roi(self) -> float:
        """Calculate annualized ROI"""
        if self.time_period == 0:
            return 0.0
        
        roi = self.calculate_roi() / 100
        annualized = ((1 + roi) ** (1 / self.time_period) - 1) * 100
        return annualized
    
    def calculate_payback_period(self) -> float:
        """Calculate payback period in years"""
        if self.total_return <= self.initial_investment:
            return float('inf')
        
        annual_return = (self.total_return - self.initial_investment) / self.time_period
        if annual_return <= 0:
            return float('inf')
        
        return self.initial_investment / annual_return

@dataclass
class ABTestResult:
    """A/B test result"""
    variant_a: Dict[str, Any]
    variant_b: Dict[str, Any]
    confidence_level: float
    winner: str
    p_value: float
    sample_size: int

@dataclass
class CACLTVCalculation:
    """CAC/LTV calculation model"""
    customer_acquisition_cost: float
    customer_lifetime_value: float
    average_order_value: Optional[float] = None
    purchase_frequency: Optional[float] = None
    customer_lifespan: Optional[float] = None
    marketing_spend: Optional[float] = None
    new_customers: Optional[int] = None
    
    def calculate_ltv_cac_ratio(self) -> float:
        """Calculate LTV/CAC ratio"""
        if self.customer_acquisition_cost == 0:
            return 0.0
        return self.customer_lifetime_value / self.customer_acquisition_cost
    
    def calculate_payback_period(self) -> float:
        """Calculate CAC payback period in months"""
        if self.customer_lifetime_value == 0:
            return float('inf')
        
        # Assuming monthly revenue from LTV
        monthly_revenue = self.customer_lifetime_value / 12  # Simplified
        if monthly_revenue == 0:
            return float('inf')
        
        return self.customer_acquisition_cost / monthly_revenue
    
    def get_profitability_score(self) -> str:
        """Get profitability assessment based on LTV/CAC ratio"""
        ratio = self.calculate_ltv_cac_ratio()
        
        if ratio >= 3.0:
            return "Excellent"
        elif ratio >= 2.0:
            return "Good"
        elif ratio >= 1.5:
            return "Acceptable"
        elif ratio >= 1.0:
            return "Marginal"
        else:
            return "Poor"
    
    def generate_recommendations(self) -> List[str]:
        """Generate strategic recommendations based on CAC/LTV analysis"""
        recommendations = []
        ratio = self.calculate_ltv_cac_ratio()
        
        if ratio < 1.0:
            recommendations.append("Critical: LTV is lower than CAC - immediate action required")
            recommendations.append("Consider reducing customer acquisition costs")
            recommendations.append("Focus on increasing customer lifetime value")
        elif ratio < 1.5:
            recommendations.append("Improve customer retention strategies")
            recommendations.append("Optimize marketing channels for better CAC")
            recommendations.append("Consider upselling and cross-selling opportunities")
        elif ratio < 2.0:
            recommendations.append("Good foundation - focus on scaling efficiently")
            recommendations.append("Test new acquisition channels")
            recommendations.append("Implement customer success programs")
        elif ratio < 3.0:
            recommendations.append("Strong performance - consider aggressive growth")
            recommendations.append("Expand to new markets or segments")
            recommendations.append("Invest in customer experience improvements")
        else:
            recommendations.append("Excellent performance - scale rapidly")
            recommendations.append("Consider premium pricing strategies")
            recommendations.append("Explore new product/service offerings")
        
        return recommendations

@dataclass
class FinancialStrategy:
    """Financial strategy model"""
    current_revenue: float
    target_revenue: float
    current_cac: float
    current_ltv: float
    available_budget: float
    growth_timeline: int  # months
    
    def calculate_growth_requirements(self) -> Dict[str, Any]:
        """Calculate growth requirements and strategy"""
        revenue_gap = self.target_revenue - self.current_revenue
        current_ltv_cac_ratio = self.current_ltv / self.current_cac if self.current_cac > 0 else 0
        
        # Calculate required new customers
        if self.current_ltv > 0:
            required_new_customers = int(revenue_gap / self.current_ltv)
        else:
            required_new_customers = 0
        
        # Calculate required investment
        required_investment = required_new_customers * self.current_cac
        
        # Calculate expected ROI
        expected_roi = ((self.target_revenue - self.current_revenue) / required_investment * 100) if required_investment > 0 else 0
        
        # Risk assessment
        risk_level = self._assess_risk(required_investment, current_ltv_cac_ratio)
        
        # Growth strategy recommendation
        growth_strategy = self._recommend_growth_strategy(required_investment, current_ltv_cac_ratio)
        
        return {
            "required_new_customers": required_new_customers,
            "required_investment": required_investment,
            "expected_roi": expected_roi,
            "risk_level": risk_level,
            "growth_strategy": growth_strategy,
            "revenue_gap": revenue_gap,
            "current_ltv_cac_ratio": current_ltv_cac_ratio
        }
    
    def _assess_risk(self, required_investment: float, ltv_cac_ratio: float) -> str:
        """Assess risk level"""
        if required_investment > self.available_budget * 2:
            return "High"
        elif required_investment > self.available_budget:
            return "Medium"
        elif ltv_cac_ratio < 1.5:
            return "Medium"
        else:
            return "Low"
    
    def _recommend_growth_strategy(self, required_investment: float, ltv_cac_ratio: float) -> str:
        """Recommend growth strategy"""
        if required_investment > self.available_budget * 2:
            return "Conservative - Focus on organic growth and efficiency improvements"
        elif required_investment > self.available_budget:
            return "Balanced - Mix of organic and paid growth with careful monitoring"
        elif ltv_cac_ratio >= 3.0:
            return "Aggressive - Scale rapidly with confidence in unit economics"
        elif ltv_cac_ratio >= 2.0:
            return "Moderate - Steady growth with optimization focus"
        else:
            return "Optimization - Focus on improving unit economics before scaling"
    
    def generate_timeline_breakdown(self) -> List[Dict[str, Any]]:
        """Generate timeline breakdown for growth"""
        timeline = []
        monthly_growth = (self.target_revenue - self.current_revenue) / self.growth_timeline
        
        for month in range(1, self.growth_timeline + 1):
            projected_revenue = self.current_revenue + (monthly_growth * month)
            projected_customers = int(projected_revenue / self.current_ltv) if self.current_ltv > 0 else 0
            
            timeline.append({
                "month": month,
                "projected_revenue": projected_revenue,
                "projected_customers": projected_customers,
                "cumulative_investment": projected_customers * self.current_cac,
                "monthly_growth_rate": (monthly_growth / self.current_revenue * 100) if self.current_revenue > 0 else 0
            })
        
        return timeline

class FinanceManager:
    """Manages financial calculations and analysis"""
    
    def __init__(self):
        self.dcf_models = {}
        self.roi_calculations = {}
        self.ab_tests = {}
        self.financial_metrics = {}
        self.cac_ltv_calculations = {}
        self.strategies = {}
        
        # Default parameters
        self.default_discount_rate = 0.10  # 10%
        self.default_growth_rate = 0.15    # 15%
        self.default_time_period = 5       # 5 years
        
    def create_dcf_model(self, 
                        initial_investment: float,
                        target_revenue: float,
                        growth_rate: float = None,
                        discount_rate: float = None,
                        time_period: int = None) -> DCFModel:
        """Create a DCF model for revenue estimation"""
        
        growth_rate = growth_rate or self.default_growth_rate
        discount_rate = discount_rate or self.default_discount_rate
        time_period = time_period or self.default_time_period
        
        # Project revenue growth
        projected_revenue = []
        current_revenue = target_revenue / time_period  # Initial annual revenue
        
        for year in range(time_period):
            projected_revenue.append(current_revenue)
            current_revenue *= (1 + growth_rate)
        
        dcf_model = DCFModel(
            initial_investment=initial_investment,
            projected_revenue=projected_revenue,
            growth_rate=growth_rate,
            discount_rate=discount_rate,
            time_period=time_period
        )
        
        model_id = f"dcf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.dcf_models[model_id] = dcf_model
        
        return dcf_model
    
    def calculate_roi_for_target(self, target_amount: float, 
                                initial_investment: float = None,
                                time_period: float = 1.0) -> ROICalculation:
        """Calculate ROI for a specific target amount"""
        
        if initial_investment is None:
            # Estimate initial investment based on target
            initial_investment = target_amount * 0.3  # 30% of target as investment
        
        roi_calc = ROICalculation(
            initial_investment=initial_investment,
            total_return=target_amount,
            time_period=time_period
        )
        
        calc_id = f"roi_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.roi_calculations[calc_id] = roi_calc
        
        return roi_calc
    
    def run_ab_test(self, 
                    variant_a_data: Dict[str, Any],
                    variant_b_data: Dict[str, Any],
                    metric: str = "conversion_rate") -> ABTestResult:
        """Run A/B test analysis"""
        
        # Extract metrics
        a_conversion = variant_a_data.get(metric, 0)
        b_conversion = variant_b_data.get(metric, 0)
        a_sample = variant_a_data.get("sample_size", 1000)
        b_sample = variant_b_data.get("sample_size", 1000)
        
        # Calculate conversion rates
        a_rate = a_conversion / a_sample if a_sample > 0 else 0
        b_rate = b_conversion / b_sample if b_sample > 0 else 0
        
        # Simplified statistical test (z-test)
        pooled_rate = (a_conversion + b_conversion) / (a_sample + b_sample)
        se = math.sqrt(pooled_rate * (1 - pooled_rate) * (1/a_sample + 1/b_sample))
        
        if se == 0:
            p_value = 1.0
            confidence_level = 0.0
        else:
            z_score = (b_rate - a_rate) / se
            p_value = 2 * (1 - self._normal_cdf(abs(z_score)))
            confidence_level = (1 - p_value) * 100
        
        # Determine winner
        winner = "B" if b_rate > a_rate else "A" if a_rate > b_rate else "Tie"
        
        result = ABTestResult(
            variant_a={"rate": a_rate, "conversions": a_conversion, "sample_size": a_sample},
            variant_b={"rate": b_rate, "conversions": b_conversion, "sample_size": b_sample},
            confidence_level=confidence_level,
            winner=winner,
            p_value=p_value,
            sample_size=a_sample + b_sample
        )
        
        test_id = f"ab_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.ab_tests[test_id] = result
        
        return result
    
    def _normal_cdf(self, x: float) -> float:
        """Approximate normal cumulative distribution function"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    def calculate_break_even_analysis(self, 
                                    fixed_costs: float,
                                    variable_cost_per_unit: float,
                                    price_per_unit: float) -> Dict[str, Any]:
        """Calculate break-even point"""
        
        if price_per_unit <= variable_cost_per_unit:
            return {
                "break_even_units": float('inf'),
                "break_even_revenue": float('inf'),
                "contribution_margin": 0,
                "is_profitable": False
            }
        
        contribution_margin = price_per_unit - variable_cost_per_unit
        break_even_units = fixed_costs / contribution_margin
        break_even_revenue = break_even_units * price_per_unit
        
        return {
            "break_even_units": break_even_units,
            "break_even_revenue": break_even_revenue,
            "contribution_margin": contribution_margin,
            "is_profitable": True
        }
    
    def calculate_cash_flow_forecast(self, 
                                   initial_cash: float,
                                   monthly_revenue: float,
                                   monthly_expenses: float,
                                   months: int = 12) -> List[Dict[str, Any]]:
        """Calculate cash flow forecast"""
        
        forecast = []
        current_cash = initial_cash
        
        for month in range(1, months + 1):
            net_cash_flow = monthly_revenue - monthly_expenses
            current_cash += net_cash_flow
            
            forecast.append({
                "month": month,
                "revenue": monthly_revenue,
                "expenses": monthly_expenses,
                "net_cash_flow": net_cash_flow,
                "ending_cash": current_cash
            })
        
        return forecast
    
    def calculate_financial_ratios(self, 
                                 revenue: float,
                                 expenses: float,
                                 assets: float,
                                 liabilities: float,
                                 equity: float) -> Dict[str, float]:
        """Calculate key financial ratios"""
        
        net_income = revenue - expenses
        
        ratios = {
            "profit_margin": (net_income / revenue * 100) if revenue > 0 else 0,
            "return_on_assets": (net_income / assets * 100) if assets > 0 else 0,
            "return_on_equity": (net_income / equity * 100) if equity > 0 else 0,
            "debt_to_equity": (liabilities / equity) if equity > 0 else float('inf'),
            "current_ratio": (assets / liabilities) if liabilities > 0 else float('inf'),
            "quick_ratio": ((assets - 0) / liabilities) if liabilities > 0 else float('inf')  # Simplified
        }
        
        return ratios
    
    def generate_financial_report(self, 
                                target_amount: float = 20000,
                                initial_investment: float = None) -> Dict[str, Any]:
        """Generate comprehensive financial report"""
        
        # Calculate ROI
        roi_calc = self.calculate_roi_for_target(target_amount, initial_investment)
        
        # Create DCF model
        dcf_model = self.create_dcf_model(
            initial_investment=roi_calc.initial_investment,
            target_revenue=target_amount
        )
        
        # Break-even analysis
        break_even = self.calculate_break_even_analysis(
            fixed_costs=roi_calc.initial_investment * 0.6,  # 60% as fixed costs
            variable_cost_per_unit=50,
            price_per_unit=100
        )
        
        # Cash flow forecast
        cash_flow = self.calculate_cash_flow_forecast(
            initial_cash=roi_calc.initial_investment,
            monthly_revenue=target_amount / 12,
            monthly_expenses=roi_calc.initial_investment * 0.1 / 12  # 10% of investment as monthly expenses
        )
        
        # Financial ratios
        ratios = self.calculate_financial_ratios(
            revenue=target_amount,
            expenses=roi_calc.initial_investment,
            assets=roi_calc.initial_investment * 1.5,
            liabilities=roi_calc.initial_investment * 0.3,
            equity=roi_calc.initial_investment * 0.7
        )
        
        return {
            "target_amount": target_amount,
            "roi_analysis": {
                "roi_percentage": roi_calc.calculate_roi(),
                "annualized_roi": roi_calc.calculate_annualized_roi(),
                "payback_period": roi_calc.calculate_payback_period(),
                "initial_investment": roi_calc.initial_investment,
                "total_return": roi_calc.total_return
            },
            "dcf_analysis": {
                "npv": dcf_model.calculate_npv(),
                "irr": dcf_model.calculate_irr(),
                "present_value": dcf_model.calculate_present_value(),
                "projected_revenue": dcf_model.projected_revenue
            },
            "break_even_analysis": break_even,
            "cash_flow_forecast": cash_flow,
            "financial_ratios": ratios,
            "recommendations": self._generate_recommendations(roi_calc, dcf_model, break_even),
            "timestamp": datetime.now().isoformat(),
            "status": "generated"
        }
    
    def _generate_recommendations(self, 
                                roi_calc: ROICalculation,
                                dcf_model: DCFModel,
                                break_even: Dict[str, Any]) -> List[str]:
        """Generate financial recommendations"""
        
        recommendations = []
        
        # ROI recommendations
        if roi_calc.calculate_roi() > 100:
            recommendations.append("Excellent ROI - Consider scaling up investment")
        elif roi_calc.calculate_roi() > 50:
            recommendations.append("Good ROI - Proceed with caution")
        elif roi_calc.calculate_roi() > 20:
            recommendations.append("Moderate ROI - Review cost structure")
        else:
            recommendations.append("Low ROI - Reconsider investment strategy")
        
        # DCF recommendations
        if dcf_model.calculate_npv() > 0:
            recommendations.append("Positive NPV - Investment is financially viable")
        else:
            recommendations.append("Negative NPV - Consider alternative investments")
        
        # Break-even recommendations
        if break_even["is_profitable"]:
            recommendations.append(f"Break-even at {break_even['break_even_units']:.0f} units")
        else:
            recommendations.append("Not profitable at current pricing")
        
        # Payback period recommendations
        payback = roi_calc.calculate_payback_period()
        if payback < 2:
            recommendations.append("Quick payback period - Low risk")
        elif payback < 5:
            recommendations.append("Moderate payback period - Manageable risk")
        else:
            recommendations.append("Long payback period - High risk")
        
        return recommendations

    def calculate_cac_ltv(self, 
                          customer_acquisition_cost: float,
                          customer_lifetime_value: float,
                          average_order_value: Optional[float] = None,
                          purchase_frequency: Optional[float] = None,
                          customer_lifespan: Optional[float] = None,
                          marketing_spend: Optional[float] = None,
                          new_customers: Optional[int] = None) -> CACLTVCalculation:
        """Calculate CAC/LTV metrics"""
        
        # Calculate LTV if not provided
        if customer_lifetime_value == 0 and average_order_value and purchase_frequency and customer_lifespan:
            customer_lifetime_value = average_order_value * purchase_frequency * customer_lifespan
        
        # Calculate CAC if not provided
        if customer_acquisition_cost == 0 and marketing_spend and new_customers:
            customer_acquisition_cost = marketing_spend / new_customers if new_customers > 0 else 0
        
        cac_ltv_calc = CACLTVCalculation(
            customer_acquisition_cost=customer_acquisition_cost,
            customer_lifetime_value=customer_lifetime_value,
            average_order_value=average_order_value,
            purchase_frequency=purchase_frequency,
            customer_lifespan=customer_lifespan,
            marketing_spend=marketing_spend,
            new_customers=new_customers
        )
        
        calc_id = f"cac_ltv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.cac_ltv_calculations[calc_id] = cac_ltv_calc
        
        return cac_ltv_calc
    
    def calculate_enhanced_roi(self, 
                              target_amount: float,
                              initial_investment: float = None,
                              time_period: float = 1.0,
                              customer_acquisition_cost: float = None,
                              customer_lifetime_value: float = None,
                              marketing_spend: float = None,
                              new_customers: int = None) -> Dict[str, Any]:
        """Calculate enhanced ROI with CAC/LTV analysis"""
        
        # Basic ROI calculation
        roi_calc = self.calculate_roi_for_target(target_amount, initial_investment, time_period)
        
        # CAC/LTV analysis if provided
        cac_ltv_analysis = None
        if customer_acquisition_cost and customer_lifetime_value:
            cac_ltv_analysis = self.calculate_cac_ltv(
                customer_acquisition_cost=customer_acquisition_cost,
                customer_lifetime_value=customer_lifetime_value,
                marketing_spend=marketing_spend,
                new_customers=new_customers
            )
        
        # Strategy recommendations
        strategy_recommendations = self._generate_enhanced_recommendations(roi_calc, cac_ltv_analysis)
        
        # Risk assessment
        risk_assessment = self._assess_enhanced_risk(roi_calc, cac_ltv_analysis)
        
        return {
            "roi_calculation": roi_calc,
            "cac_ltv_analysis": cac_ltv_analysis,
            "strategy_recommendations": strategy_recommendations,
            "risk_assessment": risk_assessment
        }
    
    def generate_financial_strategy(self,
                                   current_revenue: float,
                                   target_revenue: float,
                                   current_cac: float,
                                   current_ltv: float,
                                   available_budget: float,
                                   growth_timeline: int = 12) -> FinancialStrategy:
        """Generate comprehensive financial strategy"""
        
        strategy = FinancialStrategy(
            current_revenue=current_revenue,
            target_revenue=target_revenue,
            current_cac=current_cac,
            current_ltv=current_ltv,
            available_budget=available_budget,
            growth_timeline=growth_timeline
        )
        
        strategy_id = f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.strategies[strategy_id] = strategy
        
        return strategy
    
    def generate_dashboard_graph_data(self, 
                                     graph_type: str,
                                     time_period: str = "12m",
                                     include_projections: bool = True) -> Dict[str, Any]:
        """Generate dashboard graph data"""
        
        if graph_type == "roi_trend":
            return self._generate_roi_trend_data(time_period, include_projections)
        elif graph_type == "cac_ltv":
            return self._generate_cac_ltv_data(time_period, include_projections)
        elif graph_type == "revenue_forecast":
            return self._generate_revenue_forecast_data(time_period, include_projections)
        else:
            raise ValueError(f"Unknown graph type: {graph_type}")
    
    def _generate_roi_trend_data(self, time_period: str, include_projections: bool) -> Dict[str, Any]:
        """Generate ROI trend data for dashboard"""
        data_points = []
        
        # Historical data (mock)
        for i in range(6):
            data_points.append({
                "month": f"Month {i+1}",
                "roi_percentage": 15 + (i * 2) + (i * 0.5),  # Increasing trend
                "investment": 10000 + (i * 1000),
                "return": 11500 + (i * 1500)
            })
        
        if include_projections:
            for i in range(6, 12):
                data_points.append({
                    "month": f"Month {i+1}",
                    "roi_percentage": 25 + (i * 1.5),
                    "investment": 16000 + (i * 1200),
                    "return": 20000 + (i * 2000),
                    "projected": True
                })
        
        return {
            "graph_type": "roi_trend",
            "data_points": data_points,
            "summary_metrics": {
                "average_roi": sum([p["roi_percentage"] for p in data_points]) / len(data_points),
                "total_investment": sum([p["investment"] for p in data_points]),
                "total_return": sum([p["return"] for p in data_points])
            },
            "trend_analysis": "ROI showing positive trend with consistent growth",
            "recommendations": [
                "Continue current investment strategy",
                "Monitor for diminishing returns",
                "Consider scaling successful channels"
            ]
        }
    
    def _generate_cac_ltv_data(self, time_period: str, include_projections: bool) -> Dict[str, Any]:
        """Generate CAC/LTV data for dashboard"""
        data_points = []
        
        # Historical data (mock)
        for i in range(6):
            data_points.append({
                "month": f"Month {i+1}",
                "cac": 50 + (i * 2),
                "ltv": 200 + (i * 15),
                "ltv_cac_ratio": (200 + (i * 15)) / (50 + (i * 2)),
                "customers_acquired": 100 + (i * 10)
            })
        
        if include_projections:
            for i in range(6, 12):
                data_points.append({
                    "month": f"Month {i+1}",
                    "cac": 62 + (i * 1.5),
                    "ltv": 290 + (i * 12),
                    "ltv_cac_ratio": (290 + (i * 12)) / (62 + (i * 1.5)),
                    "customers_acquired": 160 + (i * 8),
                    "projected": True
                })
        
        return {
            "graph_type": "cac_ltv",
            "data_points": data_points,
            "summary_metrics": {
                "average_cac": sum([p["cac"] for p in data_points]) / len(data_points),
                "average_ltv": sum([p["ltv"] for p in data_points]) / len(data_points),
                "average_ltv_cac_ratio": sum([p["ltv_cac_ratio"] for p in data_points]) / len(data_points)
            },
            "trend_analysis": "LTV/CAC ratio improving, indicating better unit economics",
            "recommendations": [
                "LTV growing faster than CAC - good sign",
                "Consider increasing acquisition spend",
                "Focus on customer retention to improve LTV"
            ]
        }
    
    def _generate_revenue_forecast_data(self, time_period: str, include_projections: bool) -> Dict[str, Any]:
        """Generate revenue forecast data for dashboard"""
        data_points = []
        
        # Historical data (mock)
        for i in range(6):
            data_points.append({
                "month": f"Month {i+1}",
                "revenue": 50000 + (i * 5000),
                "growth_rate": 10 + (i * 0.5),
                "customers": 500 + (i * 50)
            })
        
        if include_projections:
            for i in range(6, 12):
                data_points.append({
                    "month": f"Month {i+1}",
                    "revenue": 80000 + (i * 6000),
                    "growth_rate": 13 + (i * 0.3),
                    "customers": 800 + (i * 40),
                    "projected": True
                })
        
        return {
            "graph_type": "revenue_forecast",
            "data_points": data_points,
            "summary_metrics": {
                "total_revenue": sum([p["revenue"] for p in data_points]),
                "average_growth_rate": sum([p["growth_rate"] for p in data_points]) / len(data_points),
                "total_customers": sum([p["customers"] for p in data_points])
            },
            "trend_analysis": "Revenue showing strong growth with increasing customer base",
            "recommendations": [
                "Revenue growth is healthy and sustainable",
                "Consider expanding to new markets",
                "Invest in customer success to maintain growth"
            ]
        }
    
    def _generate_enhanced_recommendations(self, 
                                         roi_calc: ROICalculation,
                                         cac_ltv_analysis: CACLTVCalculation = None) -> List[str]:
        """Generate enhanced recommendations combining ROI and CAC/LTV"""
        recommendations = []
        
        # ROI-based recommendations
        roi_percentage = roi_calc.calculate_roi()
        if roi_percentage > 100:
            recommendations.append("Excellent ROI - Consider scaling up investment")
        elif roi_percentage > 50:
            recommendations.append("Good ROI - Proceed with caution")
        elif roi_percentage > 20:
            recommendations.append("Moderate ROI - Review cost structure")
        else:
            recommendations.append("Low ROI - Reconsider investment strategy")
        
        # CAC/LTV-based recommendations
        if cac_ltv_analysis:
            ltv_cac_ratio = cac_ltv_analysis.calculate_ltv_cac_ratio()
            if ltv_cac_ratio >= 3.0:
                recommendations.append("Strong unit economics - scale aggressively")
            elif ltv_cac_ratio >= 2.0:
                recommendations.append("Good unit economics - steady growth")
            elif ltv_cac_ratio >= 1.5:
                recommendations.append("Acceptable unit economics - optimize before scaling")
            else:
                recommendations.append("Poor unit economics - focus on improvement")
        
        return recommendations
    
    def _assess_enhanced_risk(self, 
                             roi_calc: ROICalculation,
                             cac_ltv_analysis: CACLTVCalculation = None) -> str:
        """Assess risk level based on ROI and CAC/LTV"""
        roi_percentage = roi_calc.calculate_roi()
        
        if cac_ltv_analysis:
            ltv_cac_ratio = cac_ltv_analysis.calculate_ltv_cac_ratio()
            
            if roi_percentage < 20 or ltv_cac_ratio < 1.0:
                return "High Risk"
            elif roi_percentage < 50 or ltv_cac_ratio < 1.5:
                return "Medium Risk"
            elif roi_percentage >= 100 and ltv_cac_ratio >= 3.0:
                return "Low Risk"
            else:
                return "Moderate Risk"
        else:
            if roi_percentage < 20:
                return "High Risk"
            elif roi_percentage < 50:
                return "Medium Risk"
            else:
                return "Low Risk"

    def calculate_max_digital_income(self, 
                                   channels: List[str],
                                   monthly_views_per_channel: Dict[str, int] = None,
                                   rpm_rates: Dict[str, float] = None,
                                   affiliate_rates: Dict[str, float] = None,
                                   product_margins: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Calculate maximum digital income for multi-channel (5 channels) including ads/affiliate/products
        
        Args:
            channels: List of channel names (YouTube, TikTok, Instagram, LinkedIn, Twitter)
            monthly_views_per_channel: Dictionary of monthly views per channel
            rpm_rates: Revenue per mille (per 1000 views) for each channel
            affiliate_rates: Affiliate commission rates per channel
            product_margins: Product margin percentages per channel
            
        Returns:
            Dictionary containing total earnings breakdown and forecasts
        """
        # Default channel configurations
        default_channels = ["YouTube", "TikTok", "Instagram", "LinkedIn", "Twitter"]
        
        if not channels:
            channels = default_channels
        
        # Default monthly views per channel (if not provided)
        if monthly_views_per_channel is None:
            monthly_views_per_channel = {
                "YouTube": 50000,
                "TikTok": 100000,
                "Instagram": 75000,
                "LinkedIn": 25000,
                "Twitter": 30000
            }
        
        # Default RPM rates per channel (Revenue Per Mille - per 1000 views)
        if rpm_rates is None:
            rpm_rates = {
                "YouTube": 3.50,  # $3.50 per 1000 views
                "TikTok": 2.00,   # $2.00 per 1000 views
                "Instagram": 4.00, # $4.00 per 1000 views
                "LinkedIn": 8.00,  # $8.00 per 1000 views (higher value audience)
                "Twitter": 2.50    # $2.50 per 1000 views
            }
        
        # Default affiliate commission rates per channel
        if affiliate_rates is None:
            affiliate_rates = {
                "YouTube": 0.15,   # 15% commission
                "TikTok": 0.10,    # 10% commission
                "Instagram": 0.12, # 12% commission
                "LinkedIn": 0.20,  # 20% commission (higher value)
                "Twitter": 0.08    # 8% commission
            }
        
        # Default product margin percentages per channel
        if product_margins is None:
            product_margins = {
                "YouTube": 0.25,   # 25% margin
                "TikTok": 0.20,    # 20% margin
                "Instagram": 0.30, # 30% margin
                "LinkedIn": 0.35,  # 35% margin (premium audience)
                "Twitter": 0.18    # 18% margin
            }
        
        total_earnings = {
            "ads_revenue": 0,
            "affiliate_revenue": 0,
            "product_revenue": 0,
            "total_revenue": 0,
            "channel_breakdown": {},
            "monthly_forecast": {},
            "yearly_forecast": {},
            "roi_analysis": {},
            "recommendations": []
        }
        
        # Calculate earnings for each channel
        for channel in channels:
            monthly_views = monthly_views_per_channel.get(channel, 0)
            rpm_rate = rpm_rates.get(channel, 0)
            affiliate_rate = affiliate_rates.get(channel, 0)
            product_margin = product_margins.get(channel, 0)
            
            # Calculate ad revenue
            ad_revenue = (monthly_views / 1000) * rpm_rate
            
            # Calculate affiliate revenue (assuming 5% of viewers make purchases)
            affiliate_conversion_rate = 0.05
            affiliate_purchases = monthly_views * affiliate_conversion_rate
            average_order_value = 50  # $50 average order value
            affiliate_revenue = affiliate_purchases * average_order_value * affiliate_rate
            
            # Calculate product revenue (assuming 2% of viewers buy products)
            product_conversion_rate = 0.02
            product_purchases = monthly_views * product_conversion_rate
            average_product_value = 100  # $100 average product value
            product_revenue = product_purchases * average_product_value * product_margin
            
            # Total revenue for this channel
            channel_total = ad_revenue + affiliate_revenue + product_revenue
            
            # Store channel breakdown
            total_earnings["channel_breakdown"][channel] = {
                "monthly_views": monthly_views,
                "ad_revenue": round(ad_revenue, 2),
                "affiliate_revenue": round(affiliate_revenue, 2),
                "product_revenue": round(product_revenue, 2),
                "total_revenue": round(channel_total, 2),
                "rpm_rate": rpm_rate,
                "affiliate_rate": affiliate_rate,
                "product_margin": product_margin
            }
            
            # Add to totals
            total_earnings["ads_revenue"] += ad_revenue
            total_earnings["affiliate_revenue"] += affiliate_revenue
            total_earnings["product_revenue"] += product_revenue
            total_earnings["total_revenue"] += channel_total
        
        # Round totals
        total_earnings["ads_revenue"] = round(total_earnings["ads_revenue"], 2)
        total_earnings["affiliate_revenue"] = round(total_earnings["affiliate_revenue"], 2)
        total_earnings["product_revenue"] = round(total_earnings["product_revenue"], 2)
        total_earnings["total_revenue"] = round(total_earnings["total_revenue"], 2)
        
        # Generate monthly forecast (12 months with growth)
        monthly_growth_rate = 0.15  # 15% monthly growth
        current_monthly_revenue = total_earnings["total_revenue"]
        
        for month in range(1, 13):
            monthly_revenue = current_monthly_revenue * ((1 + monthly_growth_rate) ** (month - 1))
            total_earnings["monthly_forecast"][f"month_{month}"] = {
                "revenue": round(monthly_revenue, 2),
                "cumulative_revenue": round(sum([
                    current_monthly_revenue * ((1 + monthly_growth_rate) ** (m - 1))
                    for m in range(1, month + 1)
                ]), 2)
            }
        
        # Generate yearly forecast
        yearly_revenue = sum([
            total_earnings["monthly_forecast"][f"month_{i}"]["revenue"]
            for i in range(1, 13)
        ])
        total_earnings["yearly_forecast"] = {
            "total_revenue": round(yearly_revenue, 2),
            "average_monthly_revenue": round(yearly_revenue / 12, 2),
            "growth_rate": monthly_growth_rate * 12
        }
        
        # Calculate ROI analysis
        initial_investment = 5000  # $5000 initial investment
        roi_calc = self.calculate_roi_for_target(
            target_amount=yearly_revenue,
            initial_investment=initial_investment,
            time_period=1.0
        )
        
        total_earnings["roi_analysis"] = {
            "initial_investment": initial_investment,
            "yearly_revenue": yearly_revenue,
            "roi_percentage": roi_calc.calculate_roi(),
            "annualized_roi": roi_calc.calculate_annualized_roi(),
            "payback_period": roi_calc.calculate_payback_period()
        }
        
        # Generate recommendations
        total_earnings["recommendations"] = self._generate_digital_income_recommendations(
            total_earnings, roi_calc
        )
        
        return total_earnings
    
    def _generate_digital_income_recommendations(self, 
                                               earnings_data: Dict[str, Any],
                                               roi_calc: ROICalculation) -> List[str]:
        """Generate recommendations for digital income optimization"""
        recommendations = []
        
        total_revenue = earnings_data["total_revenue"]
        roi_percentage = roi_calc.calculate_roi()
        
        # Revenue-based recommendations
        if total_revenue < 1000:
            recommendations.append("Focus on increasing content frequency and quality")
            recommendations.append("Optimize for higher RPM channels (LinkedIn, Instagram)")
            recommendations.append("Implement affiliate marketing strategies")
        elif total_revenue < 5000:
            recommendations.append("Scale successful content formats across channels")
            recommendations.append("Diversify revenue streams with product launches")
            recommendations.append("Invest in audience growth and engagement")
        elif total_revenue < 10000:
            recommendations.append("Consider premium content and subscription models")
            recommendations.append("Expand to new channels and markets")
            recommendations.append("Optimize conversion rates for affiliate and product sales")
        else:
            recommendations.append("Excellent performance - focus on scaling and automation")
            recommendations.append("Consider building a team and outsourcing content creation")
            recommendations.append("Explore new revenue streams and partnerships")
        
        # ROI-based recommendations
        if roi_percentage > 200:
            recommendations.append("Outstanding ROI - consider aggressive scaling")
        elif roi_percentage > 100:
            recommendations.append("Strong ROI - continue current strategy with optimizations")
        elif roi_percentage > 50:
            recommendations.append("Good ROI - focus on efficiency improvements")
        else:
            recommendations.append("Low ROI - review content strategy and monetization approach")
        
        # Channel-specific recommendations
        channel_breakdown = earnings_data["channel_breakdown"]
        best_channel = max(channel_breakdown.items(), key=lambda x: x[1]["total_revenue"])
        worst_channel = min(channel_breakdown.items(), key=lambda x: x[1]["total_revenue"])
        
        recommendations.append(f"Focus on {best_channel[0]} - highest performing channel")
        recommendations.append(f"Optimize {worst_channel[0]} - lowest performing channel")
        
        return recommendations

# Global instance
finance_manager = FinanceManager() 