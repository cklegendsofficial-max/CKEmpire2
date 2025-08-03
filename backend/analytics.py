#!/usr/bin/env python3
"""
Analytics Module for CKEmpire
Handles user metrics, GA integration, A/B testing, and data-driven decisions
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
import random

# Optional imports for advanced analytics
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logging.warning("Pandas not available. Advanced analytics will be limited.")

@dataclass
class UserMetrics:
    """User metrics data structure"""
    user_id: str
    session_duration: float
    page_views: int
    conversion_rate: float
    revenue: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "session_duration": self.session_duration,
            "page_views": self.page_views,
            "conversion_rate": self.conversion_rate,
            "revenue": self.revenue,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class ABTestResult:
    """A/B test result for analytics"""
    test_id: str
    variant_a: Dict[str, Any]
    variant_b: Dict[str, Any]
    confidence_level: float
    winner: str
    p_value: float
    sample_size: int
    metric: str
    timestamp: datetime

@dataclass
class AnalyticsReport:
    """Analytics report data structure"""
    total_users: int
    total_revenue: float
    average_session_duration: float
    conversion_rate: float
    top_performing_pages: List[str]
    user_retention_rate: float
    revenue_per_user: float
    timestamp: datetime

class AnalyticsManager:
    """Manages analytics and user metrics"""
    
    def __init__(self):
        self.user_metrics = {}
        self.ab_tests = {}
        self.analytics_reports = {}
        self.ga_data = {}
        
        # Default parameters
        self.default_confidence_level = 0.95
        self.default_sample_size = 1000
        self.retention_threshold = 0.7
        
    def track_user_metric(self, 
                          user_id: str,
                          session_duration: float,
                          page_views: int,
                          conversion_rate: float,
                          revenue: float) -> UserMetrics:
        """Track user metrics"""
        
        metric = UserMetrics(
            user_id=user_id,
            session_duration=session_duration,
            page_views=page_views,
            conversion_rate=conversion_rate,
            revenue=revenue,
            timestamp=datetime.now()
        )
        
        self.user_metrics[user_id] = metric
        return metric
    
    def get_user_metrics(self, user_id: str) -> Optional[UserMetrics]:
        """Get metrics for a specific user"""
        return self.user_metrics.get(user_id)
    
    def get_all_user_metrics(self) -> List[UserMetrics]:
        """Get all user metrics"""
        return list(self.user_metrics.values())
    
    def calculate_analytics_summary(self) -> Dict[str, Any]:
        """Calculate analytics summary"""
        if not self.user_metrics:
            return {
                "total_users": 0,
                "total_revenue": 0.0,
                "average_session_duration": 0.0,
                "conversion_rate": 0.0,
                "top_performing_pages": [],
                "user_retention_rate": 0.0,
                "revenue_per_user": 0.0
            }
        
        metrics_list = list(self.user_metrics.values())
        
        total_users = len(metrics_list)
        total_revenue = sum(m.revenue for m in metrics_list)
        average_session_duration = sum(m.session_duration for m in metrics_list) / total_users
        conversion_rate = sum(m.conversion_rate for m in metrics_list) / total_users
        revenue_per_user = total_revenue / total_users if total_users > 0 else 0
        
        # Calculate retention rate (simplified)
        recent_users = [m for m in metrics_list if m.timestamp > datetime.now() - timedelta(days=30)]
        user_retention_rate = len(recent_users) / total_users if total_users > 0 else 0
        
        # Mock top performing pages
        top_performing_pages = ["/dashboard", "/analytics", "/finance", "/ai", "/subscription"]
        
        return {
            "total_users": total_users,
            "total_revenue": total_revenue,
            "average_session_duration": average_session_duration,
            "conversion_rate": conversion_rate,
            "top_performing_pages": top_performing_pages,
            "user_retention_rate": user_retention_rate,
            "revenue_per_user": revenue_per_user
        }
    
    def run_ab_test(self, 
                    test_id: str,
                    variant_a_data: Dict[str, Any],
                    variant_b_data: Dict[str, Any],
                    metric: str = "conversion_rate") -> ABTestResult:
        """Run A/B test analysis"""
        
        # Extract metrics
        a_conversion = variant_a_data.get(metric, 0)
        b_conversion = variant_b_data.get(metric, 0)
        a_sample = variant_a_data.get("sample_size", self.default_sample_size)
        b_sample = variant_b_data.get("sample_size", self.default_sample_size)
        
        # Calculate conversion rates
        a_rate = a_conversion / a_sample if a_sample > 0 else 0
        b_rate = b_conversion / b_sample if b_sample > 0 else 0
        
        # Statistical test (z-test)
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
            test_id=test_id,
            variant_a={"rate": a_rate, "conversions": a_conversion, "sample_size": a_sample},
            variant_b={"rate": b_rate, "conversions": b_conversion, "sample_size": b_sample},
            confidence_level=confidence_level,
            winner=winner,
            p_value=p_value,
            sample_size=a_sample + b_sample,
            metric=metric,
            timestamp=datetime.now()
        )
        
        self.ab_tests[test_id] = result
        return result
    
    def _normal_cdf(self, x: float) -> float:
        """Approximate normal cumulative distribution function"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    def get_ab_test_result(self, test_id: str) -> Optional[ABTestResult]:
        """Get A/B test result"""
        return self.ab_tests.get(test_id)
    
    def get_all_ab_tests(self) -> List[ABTestResult]:
        """Get all A/B test results"""
        return list(self.ab_tests.values())
    
    def generate_analytics_report(self) -> AnalyticsReport:
        """Generate comprehensive analytics report"""
        
        summary = self.calculate_analytics_summary()
        
        report = AnalyticsReport(
            total_users=summary["total_users"],
            total_revenue=summary["total_revenue"],
            average_session_duration=summary["average_session_duration"],
            conversion_rate=summary["conversion_rate"],
            top_performing_pages=summary["top_performing_pages"],
            user_retention_rate=summary["user_retention_rate"],
            revenue_per_user=summary["revenue_per_user"],
            timestamp=datetime.now()
        )
        
        report_id = f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.analytics_reports[report_id] = report
        
        return report
    
    def get_analytics_report(self, report_id: str) -> Optional[AnalyticsReport]:
        """Get analytics report by ID"""
        return self.analytics_reports.get(report_id)
    
    def get_all_analytics_reports(self) -> List[AnalyticsReport]:
        """Get all analytics reports"""
        return list(self.analytics_reports.values())
    
    def integrate_ga_data(self, 
                          property_id: str,
                          start_date: str,
                          end_date: str,
                          metrics: List[str]) -> Dict[str, Any]:
        """Integrate Google Analytics data"""
        
        # Mock GA data integration
        ga_data = {
            "page_views": 15000,
            "unique_visitors": 5000,
            "bounce_rate": 0.45,
            "avg_session_duration": 180.0,
            "conversion_rate": 0.03,
            "revenue": 5000.0,
            "top_pages": ["/dashboard", "/analytics", "/finance"],
            "traffic_sources": {
                "organic": {"visits": 3000, "conversion_rate": 0.04},
                "direct": {"visits": 1500, "conversion_rate": 0.05},
                "social": {"visits": 500, "conversion_rate": 0.02}
            },
            "device_categories": {
                "desktop": 0.6,
                "mobile": 0.35,
                "tablet": 0.05
            }
        }
        
        self.ga_data[property_id] = ga_data
        
        return ga_data
    
    def make_data_driven_decision(self, 
                                  category: str,
                                  data: Dict[str, Any],
                                  confidence_threshold: float = 0.95) -> Dict[str, Any]:
        """Make data-driven decisions based on analytics"""
        
        decisions = {
            "pricing": self._make_pricing_decision,
            "marketing": self._make_marketing_decision,
            "product": self._make_product_decision,
            "user_experience": self._make_ux_decision
        }
        
        decision_func = decisions.get(category)
        if decision_func:
            result = decision_func(data)
            # Update result to match expected interface
            result.update({
                "category": category,
                "decision": result.get("decision_type", category),
                "reasoning": result.get("recommendations", []),
                "data_points": len(data),
                "confidence": result.get("confidence", 0.8)
            })
            return result
        else:
            return {
                "category": category,
                "decision": "no_decision",
                "reasoning": [f"Unknown decision category: {category}"],
                "data_points": len(data),
                "confidence": 0.0
            }
    
    def _make_pricing_decision(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make pricing decisions based on analytics"""
        
        conversion_rate = data.get("conversion_rate", 0.0)
        revenue_per_user = data.get("revenue_per_user", 0.0)
        user_retention = data.get("user_retention_rate", 0.0)
        
        recommendations = []
        
        if conversion_rate < 0.02:
            recommendations.append("Consider lowering prices to increase conversion")
        elif conversion_rate > 0.05:
            recommendations.append("Consider raising prices to maximize revenue")
        
        if revenue_per_user < 50:
            recommendations.append("Implement premium features to increase ARPU")
        
        if user_retention < 0.6:
            recommendations.append("Focus on user engagement and retention strategies")
        
        return {
            "decision_type": "pricing",
            "recommendations": recommendations,
            "confidence": min(conversion_rate * 10, 1.0),
            "expected_impact": "revenue_optimization"
        }
    
    def _make_marketing_decision(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make marketing decisions based on analytics"""
        
        traffic_sources = data.get("traffic_sources", {})
        conversion_rate = data.get("conversion_rate", 0.0)
        
        recommendations = []
        
        # Analyze traffic sources
        if traffic_sources:
            best_source = max(traffic_sources.items(), key=lambda x: x[1].get("conversion_rate", 0))
            recommendations.append(f"Focus marketing budget on {best_source[0]} (best converting)")
        
        if conversion_rate < 0.02:
            recommendations.append("Improve landing page optimization")
        
        return {
            "decision_type": "marketing",
            "recommendations": recommendations,
            "confidence": 0.8,
            "expected_impact": "customer_acquisition"
        }
    
    def _make_product_decision(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make product decisions based on analytics"""
        
        top_pages = data.get("top_pages", [])
        session_duration = data.get("avg_session_duration", 0.0)
        
        recommendations = []
        
        if session_duration < 120:  # Less than 2 minutes
            recommendations.append("Improve user engagement and feature discovery")
        
        if "/dashboard" in top_pages:
            recommendations.append("Dashboard is popular - enhance with more features")
        
        return {
            "decision_type": "product",
            "recommendations": recommendations,
            "confidence": 0.7,
            "expected_impact": "user_engagement"
        }
    
    def _make_ux_decision(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make UX decisions based on analytics"""
        
        bounce_rate = data.get("bounce_rate", 0.0)
        device_categories = data.get("device_categories", {})
        
        recommendations = []
        
        if bounce_rate > 0.6:
            recommendations.append("Improve page load speed and content relevance")
        
        if device_categories.get("mobile", 0) > 0.5:
            recommendations.append("Optimize mobile experience")
        
        return {
            "decision_type": "user_experience",
            "recommendations": recommendations,
            "confidence": 0.9,
            "expected_impact": "user_satisfaction"
        }
    
    def get_analytics_dashboard_data(self) -> Dict[str, Any]:
        """Get data for analytics dashboard"""
        
        summary = self.calculate_analytics_summary()
        recent_ab_tests = [test for test in self.ab_tests.values() 
                          if test.timestamp > datetime.now() - timedelta(days=7)]
        
        return {
            "summary": summary,
            "user_metrics": list(self.user_metrics.values()),
            "ab_test_results": list(self.ab_tests.values()),
            "top_pages": summary.get("top_performing_pages", []),
            "revenue_trends": [12000, 15000, 18000, 22000, 25000, 28000],
            "conversion_funnel": [1000, 700, 350, 175],
            "status": "retrieved",
            "timestamp": datetime.now().isoformat()
        }

# Global instance
analytics_manager = AnalyticsManager() 