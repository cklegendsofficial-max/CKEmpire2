"""
Test router for generating sample errors and testing monitoring.
"""

from fastapi import APIRouter, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
import random
import time
import structlog
from monitoring import get_monitoring

logger = structlog.get_logger()
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/test/error",
    response_description="Generate test error",
    summary="Generate Test Error",
    description="Generate a sample error for testing Sentry integration"
)
@limiter.limit("5/minute")
async def generate_test_error():
    """Generate a test error for monitoring testing"""
    monitoring = get_monitoring()
    
    error_types = [
        ("database_error", "Database connection timeout"),
        ("ai_service_error", "AI service rate limit exceeded"),
        ("cloud_backup_error", "Cloud backup failed - insufficient storage"),
        ("validation_error", "Invalid input data provided"),
        ("authentication_error", "Invalid authentication token"),
        ("permission_error", "Insufficient permissions"),
        ("timeout_error", "Request timeout"),
        ("resource_not_found", "Resource not found")
    ]
    
    error_type, error_message = random.choice(error_types)
    
    # Record error in monitoring
    monitoring.record_error(error_type, "/api/v1/test/error", error_message)
    
    # Log error
    logger.error(f"Test error generated: {error_type}", 
                error_type=error_type,
                error_message=error_message,
                test_type="manual_error_generation")
    
    # Raise HTTP exception
    raise HTTPException(
        status_code=500,
        detail=f"Test error: {error_message}"
    )

@router.post("/test/metrics",
    response_description="Generate test metrics",
    summary="Generate Test Metrics",
    description="Generate sample metrics for testing monitoring"
)
@limiter.limit("10/minute")
async def generate_test_metrics():
    """Generate test metrics for monitoring testing"""
    monitoring = get_monitoring()
    
    # Generate random metrics
    projects_count = random.randint(5, 50)
    revenue = random.uniform(1000, 50000)
    
    # Update business metrics
    monitoring.update_business_metrics(projects_count, revenue)
    
    # Record some AI requests
    models = ['gpt-4', 'gpt-3.5-turbo', 'claude-3']
    endpoints = ['/api/v1/ai/ideas', '/api/v1/ai/content', '/api/v1/ai/analyze']
    
    for _ in range(3):
        model = random.choice(models)
        endpoint = random.choice(endpoints)
        monitoring.record_ai_request(model, endpoint)
    
    # Record some ethics checks
    results = ['passed', 'failed', 'flagged']
    for _ in range(2):
        result = random.choice(results)
        monitoring.record_ethics_check(result)
    
    # Record some cloud backups
    providers = ['aws', 'gcp', 'azure']
    statuses = ['success', 'failed', 'in_progress']
    
    for _ in range(2):
        provider = random.choice(providers)
        status = random.choice(statuses)
        monitoring.record_cloud_backup(provider, status)
    
    return {
        "message": "Test metrics generated successfully",
        "projects_count": projects_count,
        "revenue": revenue,
        "ai_requests": 3,
        "ethics_checks": 2,
        "cloud_backups": 2
    }

@router.post("/test/performance",
    response_description="Test performance monitoring",
    summary="Test Performance",
    description="Generate performance test scenarios"
)
@limiter.limit("5/minute")
async def test_performance():
    """Test performance monitoring with various scenarios"""
    monitoring = get_monitoring()
    
    # Test different performance scenarios
    scenarios = [
        ("fast_operation", 0.1),
        ("normal_operation", 0.5),
        ("slow_operation", 2.0),
        ("very_slow_operation", 5.0)
    ]
    
    results = []
    
    for operation, duration in scenarios:
        with monitoring.measure_time(operation):
            time.sleep(duration)
            results.append({
                "operation": operation,
                "duration": duration
            })
    
    return {
        "message": "Performance test completed",
        "scenarios": results
    }

@router.get("/test/health",
    response_description="Test health check",
    summary="Test Health Check",
    description="Test health check functionality"
)
async def test_health():
    """Test health check functionality"""
    monitoring = get_monitoring()
    
    # Get monitoring health status
    health_status = monitoring.health_check()
    
    return {
        "message": "Health check test",
        "monitoring_health": health_status,
        "timestamp": "2024-01-01T00:00:00Z"
    }

@router.get("/test/logs",
    response_description="Generate test logs",
    summary="Generate Test Logs",
    description="Generate various types of logs for testing"
)
@limiter.limit("10/minute")
async def generate_test_logs():
    """Generate test logs for ELK stack testing"""
    monitoring = get_monitoring()
    
    # Generate different types of events
    events = [
        ("user_login", {"user_id": "test_user_123", "ip": "192.168.1.100"}),
        ("project_created", {"project_id": "test_proj_456", "user_id": "test_user_123"}),
        ("revenue_updated", {"amount": 5000, "currency": "USD"}),
        ("ai_model_used", {"model": "gpt-4", "tokens_used": 1500}),
        ("backup_scheduled", {"provider": "aws", "retention_days": 30}),
        ("error_occurred", {"error_type": "test_error", "severity": "warning"}),
        ("performance_issue", {"operation": "database_query", "duration": 2.5}),
        ("security_event", {"event_type": "failed_login", "ip": "192.168.1.200"})
    ]
    
    for event_type, event_data in events:
        monitoring.log_event(event_type, **event_data)
    
    return {
        "message": "Test logs generated successfully",
        "events_generated": len(events),
        "event_types": [event[0] for event in events]
    } 