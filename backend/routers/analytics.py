from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

try:
    from ..analytics import analytics_manager
    from ..models import (
        UserMetricsRequest,
        UserMetricsResponse,
        AnalyticsReportResponse,
        GADataRequest,
        GADataResponse,
        DecisionRequest,
        DecisionResponse,
        AnalyticsDashboardResponse
    )
except ImportError:
    analytics_manager = None
    UserMetricsRequest = None
    UserMetricsResponse = None
    AnalyticsReportResponse = None
    GADataRequest = None
    GADataResponse = None
    DecisionRequest = None
    DecisionResponse = None
    AnalyticsDashboardResponse = None

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post("/track", response_model=UserMetricsResponse)
async def track_user_metrics(request: UserMetricsRequest):
    """Track user metrics"""
    try:
        if analytics_manager is None:
            raise HTTPException(status_code=503, detail="Analytics module not available")
            
        logging.info(f"Tracking metrics for user: {request.user_id}")
        
        metric = analytics_manager.track_user_metric(
            user_id=request.user_id,
            session_duration=request.session_duration,
            page_views=request.page_views,
            conversion_rate=request.conversion_rate,
            revenue=request.revenue
        )
        
        return UserMetricsResponse(
            user_id=metric.user_id,
            session_duration=metric.session_duration,
            page_views=metric.page_views,
            conversion_rate=metric.conversion_rate,
            revenue=metric.revenue,
            timestamp=metric.timestamp.isoformat(),
            status="tracked"
        )
        
    except Exception as e:
        logging.error(f"Error tracking user metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to track metrics: {str(e)}")

@router.get("/metrics/{user_id}", response_model=UserMetricsResponse)
async def get_user_metrics(user_id: str):
    """Get metrics for a specific user"""
    try:
        logging.info(f"Getting metrics for user: {user_id}")
        
        metric = analytics_manager.get_user_metrics(user_id)
        if not metric:
            raise HTTPException(status_code=404, detail="User metrics not found")
        
        return UserMetricsResponse(
            user_id=metric.user_id,
            session_duration=metric.session_duration,
            page_views=metric.page_views,
            conversion_rate=metric.conversion_rate,
            revenue=metric.revenue,
            timestamp=metric.timestamp.isoformat(),
            status="retrieved"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting user metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/metrics", response_model=List[UserMetricsResponse])
async def get_all_user_metrics():
    """Get all user metrics"""
    try:
        logging.info("Getting all user metrics")
        
        metrics = analytics_manager.get_all_user_metrics()
        
        return [
            UserMetricsResponse(
                user_id=metric.user_id,
                session_duration=metric.session_duration,
                page_views=metric.page_views,
                conversion_rate=metric.conversion_rate,
                revenue=metric.revenue,
                timestamp=metric.timestamp.isoformat(),
                status="retrieved"
            )
            for metric in metrics
        ]
        
    except Exception as e:
        logging.error(f"Error getting all user metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get all metrics: {str(e)}")

@router.post("/ab-test", response_model=Dict[str, Any])
async def run_ab_test(request: Dict[str, Any]):
    """Run A/B test analysis"""
    try:
        logging.info(f"Running A/B test: {request.get('test_id', 'unknown')}")
        
        result = analytics_manager.run_ab_test(
            test_id=request.get("test_id", f"ab_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            variant_a_data=request.get("variant_a_data", {}),
            variant_b_data=request.get("variant_b_data", {}),
            metric=request.get("metric", "conversion_rate")
        )
        
        return {
            "test_id": result.test_id,
            "variant_a": result.variant_a,
            "variant_b": result.variant_b,
            "confidence_level": result.confidence_level,
            "winner": result.winner,
            "p_value": result.p_value,
            "sample_size": result.sample_size,
            "metric": result.metric,
            "timestamp": result.timestamp.isoformat(),
            "status": "completed"
        }
        
    except Exception as e:
        logging.error(f"Error running A/B test: {e}")
        raise HTTPException(status_code=500, detail=f"A/B test failed: {str(e)}")

@router.get("/ab-tests", response_model=List[Dict[str, Any]])
async def get_all_ab_tests():
    """Get all A/B test results"""
    try:
        logging.info("Getting all A/B test results")
        
        results = analytics_manager.get_all_ab_tests()
        
        return [
            {
                "test_id": result.test_id,
                "variant_a": result.variant_a,
                "variant_b": result.variant_b,
                "confidence_level": result.confidence_level,
                "winner": result.winner,
                "p_value": result.p_value,
                "sample_size": result.sample_size,
                "metric": result.metric,
                "timestamp": result.timestamp.isoformat()
            }
            for result in results
        ]
        
    except Exception as e:
        logging.error(f"Error getting A/B test results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get A/B test results: {str(e)}")

@router.post("/report", response_model=AnalyticsReportResponse)
async def generate_analytics_report():
    """Generate analytics report"""
    try:
        logging.info("Generating analytics report")
        
        report = analytics_manager.generate_analytics_report()
        
        return AnalyticsReportResponse(
            total_users=report.total_users,
            total_revenue=report.total_revenue,
            average_session_duration=report.average_session_duration,
            conversion_rate=report.conversion_rate,
            top_performing_pages=report.top_performing_pages,
            user_retention_rate=report.user_retention_rate,
            revenue_per_user=report.revenue_per_user,
            timestamp=report.timestamp.isoformat(),
            status="generated"
        )
        
    except Exception as e:
        logging.error(f"Error generating analytics report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.get("/reports", response_model=List[AnalyticsReportResponse])
async def get_all_analytics_reports():
    """Get all analytics reports"""
    try:
        logging.info("Getting all analytics reports")
        
        reports = analytics_manager.get_all_analytics_reports()
        
        return [
            AnalyticsReportResponse(
                total_users=report.total_users,
                total_revenue=report.total_revenue,
                average_session_duration=report.average_session_duration,
                conversion_rate=report.conversion_rate,
                top_performing_pages=report.top_performing_pages,
                user_retention_rate=report.user_retention_rate,
                revenue_per_user=report.revenue_per_user,
                timestamp=report.timestamp.isoformat(),
                status="retrieved"
            )
            for report in reports
        ]
        
    except Exception as e:
        logging.error(f"Error getting analytics reports: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get reports: {str(e)}")

@router.post("/ga-integration", response_model=GADataResponse)
async def integrate_ga_data(request: GADataRequest):
    """Integrate Google Analytics data"""
    try:
        logging.info(f"Integrating GA data for property: {request.property_id}")
        
        ga_data = analytics_manager.integrate_ga_data(
            property_id=request.property_id,
            start_date=request.start_date,
            end_date=request.end_date,
            metrics=request.metrics
        )
        
        return GADataResponse(
            property_id=request.property_id,
            start_date=request.start_date,
            end_date=request.end_date,
            metrics=ga_data,
            status="integrated"
        )
        
    except Exception as e:
        logging.error(f"Error integrating GA data: {e}")
        raise HTTPException(status_code=500, detail=f"GA integration failed: {str(e)}")

@router.post("/decision", response_model=DecisionResponse)
async def make_data_driven_decision(request: DecisionRequest):
    """Make data-driven decision"""
    try:
        logging.info(f"Making data-driven decision for category: {request.category}")
        
        decision = analytics_manager.make_data_driven_decision(
            category=request.category,
            data=request.data,
            confidence_threshold=request.confidence_threshold
        )
        
        return DecisionResponse(
            category=request.category,
            decision=decision["decision"],
            confidence=decision["confidence"],
            reasoning=decision["reasoning"],
            data_points=decision["data_points"],
            status="completed"
        )
        
    except Exception as e:
        logging.error(f"Error making data-driven decision: {e}")
        raise HTTPException(status_code=500, detail=f"Decision making failed: {str(e)}")

@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard():
    """Get analytics dashboard data"""
    try:
        logging.info("Getting analytics dashboard data")
        
        dashboard_data = analytics_manager.get_analytics_dashboard_data()
        
        return AnalyticsDashboardResponse(
            summary=dashboard_data["summary"],
            user_metrics=dashboard_data["user_metrics"],
            ab_test_results=dashboard_data["ab_test_results"],
            top_pages=dashboard_data["top_pages"],
            revenue_trends=dashboard_data["revenue_trends"],
            conversion_funnel=dashboard_data["conversion_funnel"],
            status="retrieved"
        )
        
    except Exception as e:
        logging.error(f"Error getting analytics dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")

@router.get("/health")
async def analytics_health_check():
    """Health check for analytics module"""
    try:
        if analytics_manager is None:
            return {
                "status": "unavailable",
                "error": "Analytics module not available",
                "timestamp": datetime.now().isoformat()
            }
            
        # Check if analytics manager is properly initialized
        user_metrics_count = len(analytics_manager.user_metrics)
        ab_tests_count = len(analytics_manager.ab_tests)
        reports_count = len(analytics_manager.analytics_reports)
        
        return {
            "status": "healthy",
            "user_metrics_count": user_metrics_count,
            "ab_tests_count": ab_tests_count,
            "reports_count": reports_count,
            "default_confidence_level": analytics_manager.default_confidence_level,
            "default_sample_size": analytics_manager.default_sample_size,
            "retention_threshold": analytics_manager.retention_threshold,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Analytics health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics module unhealthy: {str(e)}")

@router.get("/metrics-summary")
async def get_analytics_metrics():
    """Get analytics module metrics"""
    try:
        summary = analytics_manager.calculate_analytics_summary()
        
        return {
            "total_users": summary["total_users"],
            "total_revenue": summary["total_revenue"],
            "average_session_duration": summary["average_session_duration"],
            "conversion_rate": summary["conversion_rate"],
            "user_retention_rate": summary["user_retention_rate"],
            "revenue_per_user": summary["revenue_per_user"],
            "top_performing_pages": summary["top_performing_pages"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error getting analytics metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics metrics: {str(e)}") 