from locust import HttpUser, task, between
import json
import random


class CKEmpireUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Initialize user session"""
        self.client.headers = {
            "Content-Type": "application/json",
            "User-Agent": "CK-Empire-Performance-Test"
        }
    
    @task(3)
    def get_metrics(self):
        """Test metrics endpoint"""
        self.client.get("/metrics")
    
    @task(2)
    def get_health(self):
        """Test health check endpoint"""
        self.client.get("/health")
    
    @task(2)
    def get_projects(self):
        """Test projects endpoint"""
        self.client.get("/projects")
    
    @task(1)
    def create_project(self):
        """Test project creation"""
        project_data = {
            "name": f"Test Project {random.randint(1, 1000)}",
            "description": "Performance test project",
            "status": "active",
            "metadata_encrypted": "test-metadata"
        }
        self.client.post("/projects", json=project_data)
    
    @task(1)
    def get_revenue(self):
        """Test revenue endpoint"""
        self.client.get("/revenue")
    
    @task(1)
    def create_revenue(self):
        """Test revenue creation"""
        revenue_data = {
            "amount": random.randint(100, 10000),
            "source": "performance-test",
            "date": "2024-01-01",
            "metadata_encrypted": "test-revenue"
        }
        self.client.post("/revenue", json=revenue_data)
    
    @task(1)
    def test_ethics_check(self):
        """Test ethics endpoint"""
        content_data = {
            "content": "This is a test content for ethics checking",
            "content_type": "text",
            "user_id": "test-user"
        }
        self.client.post("/ethics/check", json=content_data)
    
    @task(1)
    def test_ai_ideas(self):
        """Test AI ideas generation"""
        idea_data = {
            "topic": "technology",
            "style": "viral",
            "count": 3
        }
        self.client.post("/ai/ideas", json=idea_data)
    
    @task(1)
    def test_performance_metrics(self):
        """Test performance metrics endpoint"""
        self.client.get("/performance/metrics")
    
    @task(1)
    def test_agi_state(self):
        """Test AGI state endpoint"""
        self.client.get("/ai/agi-state")


class HighLoadUser(HttpUser):
    wait_time = between(0.1, 0.5)
    weight = 1  # Lower weight for high load users
    
    def on_start(self):
        """Initialize user session"""
        self.client.headers = {
            "Content-Type": "application/json",
            "User-Agent": "CK-Empire-HighLoad-Test"
        }
    
    @task(5)
    def rapid_metrics_check(self):
        """Rapid metrics checking"""
        self.client.get("/metrics")
    
    @task(3)
    def rapid_health_check(self):
        """Rapid health checking"""
        self.client.get("/health")
    
    @task(2)
    def rapid_projects_check(self):
        """Rapid projects checking"""
        self.client.get("/projects") 