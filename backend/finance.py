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

class FinanceManager:
    """Manages financial calculations and analysis"""
    
    def __init__(self):
        self.dcf_models = {}
        self.roi_calculations = {}
        self.ab_tests = {}
        self.financial_metrics = {}
        
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

# Global instance
finance_manager = FinanceManager() 