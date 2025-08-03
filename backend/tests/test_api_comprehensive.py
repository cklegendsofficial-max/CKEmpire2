import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

@pytest.mark.api
@pytest.mark.unit
class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_check_success(self, client, mock_monitoring):
        """Test successful health check"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "cloud_enabled" in data
        assert "monitoring" in data
        assert "timestamp" in data
    
    def test_health_check_database_failure(self, client, mock_monitoring):
        """Test health check with database failure"""
        with patch('main.get_db') as mock_db:
            mock_db.side_effect = Exception("Database connection failed")
            
            response = client.get("/health")
            
            assert response.status_code == 503
            data = response.json()
            assert "Service unhealthy" in data["detail"]
    
    def test_metrics_endpoint_success(self, client, mock_monitoring):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "consciousness_score" in data
        assert "total_revenue" in data
        assert "active_agents" in data
        assert "total_projects" in data
        assert "total_content" in data
        assert "cloud_provider" in data
        assert "cloud_enabled" in data
        assert "prometheus_metrics" in data
    
    def test_metrics_endpoint_failure(self, client, mock_monitoring):
        """Test metrics endpoint with failure"""
        with patch('main.get_db') as mock_db:
            mock_db.side_effect = Exception("Database error")
            
            response = client.get("/metrics")
            
            assert response.status_code == 500
            data = response.json()
            assert "Failed to get metrics" in data["detail"]

@pytest.mark.api
@pytest.mark.unit
class TestProjectEndpoints:
    """Test project-related endpoints"""
    
    def test_create_project_success(self, client, auth_headers, sample_project_data):
        """Test successful project creation"""
        response = client.post("/api/v1/projects/", json=sample_project_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_project_data["name"]
        assert data["description"] == sample_project_data["description"]
        assert data["status"] == sample_project_data["status"]
        assert data["budget"] == sample_project_data["budget"]
        assert data["revenue"] == sample_project_data["revenue"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_project_missing_required_fields(self, client, auth_headers):
        """Test project creation with missing required fields"""
        incomplete_data = {"description": "Test description"}
        
        response = client.post("/api/v1/projects/", json=incomplete_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_create_project_invalid_status(self, client, auth_headers):
        """Test project creation with invalid status"""
        invalid_data = {
            "name": "Test Project",
            "status": "invalid_status",
            "description": "Test description"
        }
        
        response = client.post("/api/v1/projects/", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_get_project_success(self, client, auth_headers, create_test_project):
        """Test successful project retrieval"""
        project = create_test_project(name="Test Project", status="active")
        
        response = client.get(f"/api/v1/projects/{project.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project.id
        assert data["name"] == project.name
        assert data["status"] == project.status
    
    def test_get_project_not_found(self, client, auth_headers):
        """Test project retrieval with non-existent ID"""
        response = client.get("/api/v1/projects/999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "Project not found" in data["detail"]
    
    def test_get_all_projects_success(self, client, auth_headers, create_test_project):
        """Test successful retrieval of all projects"""
        # Create multiple projects
        project1 = create_test_project(name="Project 1", status="active")
        project2 = create_test_project(name="Project 2", status="completed")
        project3 = create_test_project(name="Project 3", status="active")
        
        response = client.get("/api/v1/projects/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
    
    def test_get_projects_by_status(self, client, auth_headers, create_test_project):
        """Test getting projects by status"""
        # Create projects with different statuses
        active_project = create_test_project(name="Active Project", status="active")
        completed_project = create_test_project(name="Completed Project", status="completed")
        
        response = client.get("/api/v1/projects/?status=active", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert all(project["status"] == "active" for project in data)
    
    def test_update_project_success(self, client, auth_headers, create_test_project):
        """Test successful project update"""
        project = create_test_project(name="Original Name", status="active")
        
        update_data = {
            "name": "Updated Name",
            "status": "completed",
            "budget": 2000.0
        }
        
        response = client.put(f"/api/v1/projects/{project.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["status"] == "completed"
        assert data["budget"] == 2000.0
    
    def test_update_project_not_found(self, client, auth_headers):
        """Test project update with non-existent ID"""
        update_data = {"name": "Updated Name"}
        
        response = client.put("/api/v1/projects/999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "Project not found" in data["detail"]
    
    def test_delete_project_success(self, client, auth_headers, create_test_project):
        """Test successful project deletion"""
        project = create_test_project(name="To Delete", status="active")
        
        response = client.delete(f"/api/v1/projects/{project.id}", headers=auth_headers)
        
        assert response.status_code == 204
    
    def test_delete_project_not_found(self, client, auth_headers):
        """Test project deletion with non-existent ID"""
        response = client.delete("/api/v1/projects/999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "Project not found" in data["detail"]

@pytest.mark.api
@pytest.mark.unit
class TestContentEndpoints:
    """Test content-related endpoints"""
    
    def test_create_content_success(self, client, auth_headers, create_test_project, sample_content_data):
        """Test successful content creation"""
        project = create_test_project(name="Test Project", status="active")
        content_data = {**sample_content_data, "project_id": project.id}
        
        response = client.post("/api/v1/content/", json=content_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == content_data["title"]
        assert data["content_type"] == content_data["content_type"]
        assert data["content_data"] == content_data["content_data"]
        assert data["project_id"] == project.id
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_content_invalid_project(self, client, auth_headers, sample_content_data):
        """Test content creation with invalid project ID"""
        content_data = {**sample_content_data, "project_id": 999}
        
        response = client.post("/api/v1/content/", json=content_data, headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "Project not found" in data["detail"]
    
    def test_get_content_success(self, client, auth_headers, create_test_project, create_test_content):
        """Test successful content retrieval"""
        project = create_test_project(name="Test Project", status="active")
        content = create_test_content(project_id=project.id, title="Test Content", content_type="blog", content_data="Test content")
        
        response = client.get(f"/api/v1/content/{content.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == content.id
        assert data["title"] == content.title
        assert data["content_type"] == content.content_type
    
    def test_get_content_not_found(self, client, auth_headers):
        """Test content retrieval with non-existent ID"""
        response = client.get("/api/v1/content/999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "Content not found" in data["detail"]
    
    def test_get_content_by_project(self, client, auth_headers, create_test_project, create_test_content):
        """Test getting content by project"""
        project = create_test_project(name="Test Project", status="active")
        content1 = create_test_content(project_id=project.id, title="Content 1", content_type="blog", content_data="Content 1")
        content2 = create_test_content(project_id=project.id, title="Content 2", content_type="article", content_data="Content 2")
        
        response = client.get(f"/api/v1/projects/{project.id}/content", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(content["project_id"] == project.id for content in data)
    
    def test_update_content_success(self, client, auth_headers, create_test_project, create_test_content):
        """Test successful content update"""
        project = create_test_project(name="Test Project", status="active")
        content = create_test_content(project_id=project.id, title="Original Title", content_type="blog", content_data="Original content")
        
        update_data = {
            "title": "Updated Title",
            "content_data": "Updated content",
            "status": "published"
        }
        
        response = client.put(f"/api/v1/content/{content.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["content_data"] == "Updated content"
        assert data["status"] == "published"
    
    def test_delete_content_success(self, client, auth_headers, create_test_project, create_test_content):
        """Test successful content deletion"""
        project = create_test_project(name="Test Project", status="active")
        content = create_test_content(project_id=project.id, title="To Delete", content_type="blog", content_data="To delete")
        
        response = client.delete(f"/api/v1/content/{content.id}", headers=auth_headers)
        
        assert response.status_code == 204

@pytest.mark.api
@pytest.mark.unit
class TestRevenueEndpoints:
    """Test revenue-related endpoints"""
    
    def test_create_revenue_success(self, client, auth_headers, create_test_project, sample_revenue_data):
        """Test successful revenue creation"""
        project = create_test_project(name="Test Project", status="active")
        revenue_data = {**sample_revenue_data, "project_id": project.id}
        
        response = client.post("/api/v1/revenue/", json=revenue_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == revenue_data["amount"]
        assert data["source"] == revenue_data["source"]
        assert data["description"] == revenue_data["description"]
        assert data["project_id"] == project.id
        assert "id" in data
        assert "created_at" in data
    
    def test_get_revenue_success(self, client, auth_headers, create_test_project, create_test_revenue):
        """Test successful revenue retrieval"""
        project = create_test_project(name="Test Project", status="active")
        revenue = create_test_revenue(project_id=project.id, amount=100.0, source="test", description="Test revenue")
        
        response = client.get(f"/api/v1/revenue/{revenue.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == revenue.id
        assert data["amount"] == revenue.amount
        assert data["source"] == revenue.source
    
    def test_get_revenue_by_project(self, client, auth_headers, create_test_project, create_test_revenue):
        """Test getting revenue by project"""
        project = create_test_project(name="Test Project", status="active")
        revenue1 = create_test_revenue(project_id=project.id, amount=100.0, source="source1", description="Revenue 1")
        revenue2 = create_test_revenue(project_id=project.id, amount=200.0, source="source2", description="Revenue 2")
        
        response = client.get(f"/api/v1/projects/{project.id}/revenue", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(rev["project_id"] == project.id for rev in data)

@pytest.mark.api
@pytest.mark.unit
class TestAIEndpoints:
    """Test AI-related endpoints"""
    
    def test_generate_content_success(self, client, auth_headers, mock_ai_processor, sample_ai_request_data):
        """Test successful content generation"""
        response = client.post("/api/v1/ai/generate", json=sample_ai_request_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "tokens_used" in data
        assert "model" in data
        assert "cost" in data
    
    def test_generate_content_missing_prompt(self, client, auth_headers):
        """Test content generation with missing prompt"""
        incomplete_data = {"model": "gpt-4", "max_tokens": 500}
        
        response = client.post("/api/v1/ai/generate", json=incomplete_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_analyze_sentiment_success(self, client, auth_headers, mock_ai_processor):
        """Test successful sentiment analysis"""
        sentiment_data = {"text": "This is a positive review about our product."}
        
        response = client.post("/api/v1/ai/sentiment", json=sentiment_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data
        assert "confidence" in data
        assert "score" in data
    
    def test_ai_processor_error(self, client, auth_headers, mock_ai_processor):
        """Test AI processor error handling"""
        mock_ai_processor.return_value.generate_content.side_effect = Exception("AI service error")
        
        response = client.post("/api/v1/ai/generate", json={"prompt": "Test prompt"}, headers=auth_headers)
        
        assert response.status_code == 500
        data = response.json()
        assert "AI processing failed" in data["detail"]

@pytest.mark.api
@pytest.mark.unit
class TestEthicsEndpoints:
    """Test ethics-related endpoints"""
    
    def test_check_content_ethics_success(self, client, auth_headers, mock_ethics_processor, sample_ethics_check_data):
        """Test successful ethics check"""
        response = client.post("/api/v1/ethics/check", json=sample_ethics_check_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "is_ethical" in data
        assert "confidence" in data
        assert "issues" in data
        assert "recommendations" in data
    
    def test_audit_decision_success(self, client, auth_headers, mock_ethics_processor):
        """Test successful audit decision"""
        audit_data = {
            "content": "Test content for audit",
            "content_type": "blog",
            "project_id": 1,
            "user_id": 1
        }
        
        response = client.post("/api/v1/ethics/audit", json=audit_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "decision" in data
        assert "reason" in data
        assert "confidence" in data
    
    def test_ethics_processor_error(self, client, auth_headers, mock_ethics_processor):
        """Test ethics processor error handling"""
        mock_ethics_processor.return_value.check_content.side_effect = Exception("Ethics service error")
        
        response = client.post("/api/v1/ethics/check", json={"content": "Test content"}, headers=auth_headers)
        
        assert response.status_code == 500
        data = response.json()
        assert "Ethics check failed" in data["detail"]

@pytest.mark.api
@pytest.mark.unit
class TestPerformanceEndpoints:
    """Test performance-related endpoints"""
    
    def test_get_performance_metrics_success(self, client, auth_headers, mock_performance_processor):
        """Test successful performance metrics retrieval"""
        response = client.get("/api/v1/performance/metrics", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "metrics" in data
        assert "response_time" in data["metrics"]
        assert "throughput" in data["metrics"]
        assert "error_rate" in data["metrics"]
    
    def test_optimize_system_success(self, client, auth_headers, mock_performance_processor):
        """Test successful system optimization"""
        optimization_data = {"target": "response_time", "threshold": 0.5}
        
        response = client.post("/api/v1/performance/optimize", json=optimization_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "optimizations" in data
        assert "improvement" in data
        assert "status" in data

@pytest.mark.api
@pytest.mark.unit
class TestCloudEndpoints:
    """Test cloud-related endpoints"""
    
    def test_cloud_backup_success(self, client, auth_headers, mock_aws_manager):
        """Test successful cloud backup"""
        backup_data = {"project_id": 1, "backup_type": "full"}
        
        response = client.post("/api/v1/cloud/backup", json=backup_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "backup_id" in data
        assert "status" in data
        assert "location" in data
    
    def test_cloud_restore_success(self, client, auth_headers, mock_aws_manager):
        """Test successful cloud restore"""
        restore_data = {"backup_id": "backup-123", "project_id": 1}
        
        response = client.post("/api/v1/cloud/restore", json=restore_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data

@pytest.mark.api
@pytest.mark.unit
class TestAuthenticationAndAuthorization:
    """Test authentication and authorization"""
    
    def test_protected_endpoint_without_auth(self, client):
        """Test accessing protected endpoint without authentication"""
        response = client.get("/api/v1/projects/")
        
        assert response.status_code == 401
    
    def test_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/v1/projects/", headers=headers)
        
        assert response.status_code == 401
    
    def test_protected_endpoint_with_valid_auth(self, client, auth_headers):
        """Test accessing protected endpoint with valid authentication"""
        response = client.get("/api/v1/projects/", headers=auth_headers)
        
        assert response.status_code == 200

@pytest.mark.api
@pytest.mark.unit
class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_json_request(self, client, auth_headers):
        """Test handling of invalid JSON in request body"""
        response = client.post(
            "/api/v1/projects/",
            data="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_content_type(self, client, auth_headers):
        """Test handling of missing Content-Type header"""
        response = client.post("/api/v1/projects/", data='{"name": "Test"}', headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_large_request_body(self, client, auth_headers):
        """Test handling of large request body"""
        large_data = {"name": "Test", "description": "x" * 10000}
        
        response = client.post("/api/v1/projects/", json=large_data, headers=auth_headers)
        
        # Should either succeed or fail gracefully
        assert response.status_code in [201, 413, 422]
    
    def test_sql_injection_attempt(self, client, auth_headers):
        """Test SQL injection attempt handling"""
        malicious_data = {
            "name": "'; DROP TABLE projects; --",
            "status": "active"
        }
        
        response = client.post("/api/v1/projects/", json=malicious_data, headers=auth_headers)
        
        # Should handle gracefully (either succeed with escaped data or fail safely)
        assert response.status_code in [201, 422, 400]

@pytest.mark.api
@pytest.mark.performance
class TestAPIPerformance:
    """Test API performance under various conditions"""
    
    def test_concurrent_requests(self, client, auth_headers, create_test_project, benchmark):
        """Test handling of concurrent requests"""
        project = create_test_project(name="Performance Test", status="active")
        
        def make_request():
            return client.get(f"/api/v1/projects/{project.id}", headers=auth_headers)
        
        # Test multiple concurrent requests
        results = [make_request() for _ in range(10)]
        
        # All requests should succeed
        assert all(result.status_code == 200 for result in results)
    
    def test_large_dataset_handling(self, client, auth_headers, create_test_project, benchmark):
        """Test API performance with large datasets"""
        # Create many projects
        projects = []
        for i in range(100):
            project = create_test_project(name=f"Project {i}", status="active")
            projects.append(project)
        
        def get_all_projects():
            return client.get("/api/v1/projects/", headers=auth_headers)
        
        response = benchmark(get_all_projects)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 100

@pytest.mark.api
@pytest.mark.integration
class TestAPIIntegration:
    """Test API integration scenarios"""
    
    def test_full_project_lifecycle(self, client, auth_headers):
        """Test complete project lifecycle through API"""
        # 1. Create project
        project_data = {
            "name": "Integration Test Project",
            "description": "Test project for integration testing",
            "status": "active",
            "budget": 5000.0,
            "revenue": 0.0
        }
        
        create_response = client.post("/api/v1/projects/", json=project_data, headers=auth_headers)
        assert create_response.status_code == 201
        project = create_response.json()
        project_id = project["id"]
        
        # 2. Create content for the project
        content_data = {
            "project_id": project_id,
            "title": "Integration Test Content",
            "content_type": "blog",
            "content_data": "This is test content for integration testing",
            "status": "draft"
        }
        
        content_response = client.post("/api/v1/content/", json=content_data, headers=auth_headers)
        assert content_response.status_code == 201
        content = content_response.json()
        content_id = content["id"]
        
        # 3. Add revenue to the project
        revenue_data = {
            "project_id": project_id,
            "amount": 1000.0,
            "source": "integration_test",
            "description": "Revenue from integration test"
        }
        
        revenue_response = client.post("/api/v1/revenue/", json=revenue_data, headers=auth_headers)
        assert revenue_response.status_code == 201
        
        # 4. Update project status
        update_data = {"status": "completed"}
        update_response = client.put(f"/api/v1/projects/{project_id}", json=update_data, headers=auth_headers)
        assert update_response.status_code == 200
        
        # 5. Verify final state
        final_project = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
        assert final_project.status_code == 200
        final_data = final_project.json()
        assert final_data["status"] == "completed"
        
        # 6. Clean up
        client.delete(f"/api/v1/content/{content_id}", headers=auth_headers)
        client.delete(f"/api/v1/projects/{project_id}", headers=auth_headers)
    
    def test_cross_service_integration(self, client, auth_headers, mock_ai_processor, mock_ethics_processor):
        """Test integration between different services"""
        # 1. Create project
        project_data = {"name": "Cross Service Test", "status": "active"}
        project_response = client.post("/api/v1/projects/", json=project_data, headers=auth_headers)
        assert project_response.status_code == 201
        project = project_response.json()
        
        # 2. Generate AI content
        ai_data = {"prompt": "Write a blog post about AI", "model": "gpt-4"}
        ai_response = client.post("/api/v1/ai/generate", json=ai_data, headers=auth_headers)
        assert ai_response.status_code == 200
        ai_content = ai_response.json()
        
        # 3. Check ethics of generated content
        ethics_data = {
            "content": ai_content["content"],
            "content_type": "blog",
            "project_id": project["id"]
        }
        ethics_response = client.post("/api/v1/ethics/check", json=ethics_data, headers=auth_headers)
        assert ethics_response.status_code == 200
        ethics_result = ethics_response.json()
        
        # 4. Create content if ethics check passes
        if ethics_result["is_ethical"]:
            content_data = {
                "project_id": project["id"],
                "title": "AI Generated Blog Post",
                "content_type": "blog",
                "content_data": ai_content["content"],
                "status": "draft",
                "ai_generated": True
            }
            content_response = client.post("/api/v1/content/", json=content_data, headers=auth_headers)
            assert content_response.status_code == 201 