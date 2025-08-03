"""
Test script for monitoring system - generates sample errors and tests Sentry integration.
"""

import time
import random
import structlog
from monitoring import get_monitoring
import sentry_sdk

logger = structlog.get_logger()

def test_monitoring_system():
    """Test the monitoring system with various scenarios"""
    
    monitoring = get_monitoring()
    
    print("🧪 Testing CK Empire Builder Monitoring System")
    print("=" * 50)
    
    # Test 1: Record HTTP requests
    print("\n1. Testing HTTP request metrics...")
    for i in range(5):
        method = random.choice(['GET', 'POST', 'PUT', 'DELETE'])
        endpoint = random.choice(['/api/v1/projects', '/api/v1/revenue', '/api/v1/ai/ideas'])
        status = random.choice([200, 201, 400, 404, 500])
        duration = random.uniform(0.1, 2.0)
        
        monitoring.record_http_request(method, endpoint, status, duration)
        print(f"   Recorded: {method} {endpoint} - {status} ({duration:.3f}s)")
    
    # Test 2: Record AI requests
    print("\n2. Testing AI request metrics...")
    models = ['gpt-4', 'gpt-3.5-turbo', 'claude-3', 'llama-2']
    endpoints = ['/api/v1/ai/ideas', '/api/v1/ai/content', '/api/v1/ai/analyze']
    
    for i in range(3):
        model = random.choice(models)
        endpoint = random.choice(endpoints)
        monitoring.record_ai_request(model, endpoint)
        print(f"   Recorded AI request: {model} -> {endpoint}")
    
    # Test 3: Record ethics checks
    print("\n3. Testing ethics check metrics...")
    results = ['passed', 'failed', 'flagged', 'review_required']
    
    for i in range(4):
        result = random.choice(results)
        monitoring.record_ethics_check(result)
        print(f"   Recorded ethics check: {result}")
    
    # Test 4: Update business metrics
    print("\n4. Testing business metrics...")
    projects_count = random.randint(10, 50)
    revenue = random.uniform(10000, 100000)
    monitoring.update_business_metrics(projects_count, revenue)
    print(f"   Updated business metrics: {projects_count} projects, ${revenue:.2f} revenue")
    
    # Test 5: Record cloud backups
    print("\n5. Testing cloud backup metrics...")
    providers = ['aws', 'gcp', 'azure']
    statuses = ['success', 'failed', 'in_progress']
    
    for i in range(3):
        provider = random.choice(providers)
        status = random.choice(statuses)
        monitoring.record_cloud_backup(provider, status)
        print(f"   Recorded cloud backup: {provider} -> {status}")
    
    # Test 6: Generate sample errors for Sentry
    print("\n6. Testing Sentry error tracking...")
    
    try:
        # Simulate a database error
        raise Exception("Database connection timeout - simulated error")
    except Exception as e:
        monitoring.record_error("database_error", "/api/v1/projects", str(e))
        logger.error("Database error occurred", error=str(e))
        print(f"   Recorded database error: {e}")
    
    try:
        # Simulate an AI service error
        raise Exception("AI service rate limit exceeded - simulated error")
    except Exception as e:
        monitoring.record_error("ai_service_error", "/api/v1/ai/ideas", str(e))
        logger.error("AI service error occurred", error=str(e))
        print(f"   Recorded AI service error: {e}")
    
    try:
        # Simulate a cloud backup error
        raise Exception("Cloud backup failed - insufficient storage - simulated error")
    except Exception as e:
        monitoring.record_error("cloud_backup_error", "/api/v1/cloud/backup", str(e))
        logger.error("Cloud backup error occurred", error=str(e))
        print(f"   Recorded cloud backup error: {e}")
    
    # Test 7: Test timing measurements
    print("\n7. Testing operation timing...")
    
    with monitoring.measure_time("database_query"):
        time.sleep(random.uniform(0.1, 0.5))
        print("   Measured database query time")
    
    with monitoring.measure_time("ai_content_generation"):
        time.sleep(random.uniform(1.0, 3.0))
        print("   Measured AI content generation time")
    
    with monitoring.measure_time("cloud_backup_operation"):
        time.sleep(random.uniform(2.0, 5.0))
        print("   Measured cloud backup operation time")
    
    # Test 8: Log various events
    print("\n8. Testing event logging...")
    
    events = [
        ("user_login", {"user_id": "user123", "ip": "192.168.1.100"}),
        ("project_created", {"project_id": "proj456", "user_id": "user123"}),
        ("revenue_updated", {"amount": 5000, "currency": "USD"}),
        ("ai_model_used", {"model": "gpt-4", "tokens_used": 1500}),
        ("backup_scheduled", {"provider": "aws", "retention_days": 30})
    ]
    
    for event_type, event_data in events:
        monitoring.log_event(event_type, **event_data)
        print(f"   Logged event: {event_type}")
    
    # Test 9: Get health status
    print("\n9. Testing health check...")
    health_status = monitoring.health_check()
    print(f"   Health status: {health_status['status']}")
    for component, status in health_status['components'].items():
        print(f"   - {component}: {status}")
    
    # Test 10: Get Prometheus metrics
    print("\n10. Testing Prometheus metrics...")
    metrics = monitoring.get_metrics()
    print(f"   Generated {len(metrics)} bytes of Prometheus metrics")
    
    print("\n✅ Monitoring system test completed successfully!")
    print("📊 Check your monitoring dashboards for the collected metrics")
    print("🐛 Check Sentry for the generated error reports")

def test_sentry_integration():
    """Test Sentry integration specifically"""
    
    print("\n🔍 Testing Sentry Integration")
    print("=" * 30)
    
    # Test different types of errors
    error_types = [
        ("ValueError", "Invalid input parameter"),
        ("ConnectionError", "Database connection failed"),
        ("TimeoutError", "AI service request timeout"),
        ("PermissionError", "Insufficient permissions for cloud operation"),
        ("ResourceNotFoundError", "Project not found"),
        ("RateLimitError", "API rate limit exceeded"),
        ("ValidationError", "Data validation failed"),
        ("AuthenticationError", "Invalid authentication token")
    ]
    
    for error_class, error_message in error_types:
        try:
            # Simulate the error
            if error_class == "ValueError":
                raise ValueError(error_message)
            elif error_class == "ConnectionError":
                raise ConnectionError(error_message)
            elif error_class == "TimeoutError":
                raise TimeoutError(error_message)
            elif error_class == "PermissionError":
                raise PermissionError(error_message)
            elif error_class == "ResourceNotFoundError":
                raise Exception(f"ResourceNotFoundError: {error_message}")
            elif error_class == "RateLimitError":
                raise Exception(f"RateLimitError: {error_message}")
            elif error_class == "ValidationError":
                raise Exception(f"ValidationError: {error_message}")
            elif error_class == "AuthenticationError":
                raise Exception(f"AuthenticationError: {error_message}")
                
        except Exception as e:
            # This will be captured by Sentry
            logger.error(f"Sentry test error: {error_class}", 
                        error_class=error_class,
                        error_message=error_message,
                        test_type="sentry_integration")
            
            print(f"   Generated {error_class}: {error_message}")
    
    print("✅ Sentry integration test completed!")

if __name__ == "__main__":
    # Test the monitoring system
    test_monitoring_system()
    
    # Test Sentry integration
    test_sentry_integration()
    
    print("\n🎉 All monitoring tests completed!")
    print("📈 Check your monitoring dashboards:")
    print("   - Prometheus: http://localhost:9090")
    print("   - Grafana: http://localhost:3000")
    print("   - Kibana: http://localhost:5601")
    print("   - Sentry: https://sentry.io") 