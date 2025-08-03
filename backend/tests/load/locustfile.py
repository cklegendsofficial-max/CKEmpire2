import time
import random
import json
from locust import HttpUser, task, between, events
from locust.exception import StopUser

class CKEmpireUser(HttpUser):
    """Load testing user for CK Empire API"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Setup user session"""
        self.auth_headers = {"Authorization": "Bearer test-token"}
        self.project_ids = []
        self.content_ids = []
        self.revenue_ids = []
    
    @task(3)
    def health_check(self):
        """Test health endpoint"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure("Health check returned unhealthy status")
            else:
                response.failure(f"Health check failed with status {response.status_code}")
    
    @task(2)
    def get_metrics(self):
        """Test metrics endpoint"""
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                required_fields = ["consciousness_score", "total_revenue", "active_agents", "total_projects"]
                if all(field in data for field in required_fields):
                    response.success()
                else:
                    response.failure("Metrics missing required fields")
            else:
                response.failure(f"Metrics endpoint failed with status {response.status_code}")
    
    @task(2)
    def get_projects(self):
        """Test getting all projects"""
        with self.client.get("/api/v1/projects/", headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("Projects endpoint did not return a list")
            else:
                response.failure(f"Projects endpoint failed with status {response.status_code}")
    
    @task(1)
    def create_project(self):
        """Test project creation"""
        project_data = {
            "name": f"Load Test Project {random.randint(1000, 9999)}",
            "description": "Project created during load testing",
            "status": random.choice(["active", "inactive", "completed"]),
            "budget": random.uniform(1000, 10000),
            "revenue": random.uniform(0, 5000)
        }
        
        with self.client.post("/api/v1/projects/", json=project_data, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 201:
                data = response.json()
                if "id" in data:
                    self.project_ids.append(data["id"])
                    response.success()
                else:
                    response.failure("Project creation response missing ID")
            else:
                response.failure(f"Project creation failed with status {response.status_code}")
    
    @task(1)
    def get_project(self):
        """Test getting specific project"""
        if not self.project_ids:
            return
        
        project_id = random.choice(self.project_ids)
        with self.client.get(f"/api/v1/projects/{project_id}", headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == project_id:
                    response.success()
                else:
                    response.failure("Project ID mismatch")
            else:
                response.failure(f"Get project failed with status {response.status_code}")
    
    @task(1)
    def update_project(self):
        """Test project update"""
        if not self.project_ids:
            return
        
        project_id = random.choice(self.project_ids)
        update_data = {
            "name": f"Updated Project {random.randint(1000, 9999)}",
            "status": random.choice(["active", "completed"])
        }
        
        with self.client.put(f"/api/v1/projects/{project_id}", json=update_data, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == project_id:
                    response.success()
                else:
                    response.failure("Updated project ID mismatch")
            else:
                response.failure(f"Project update failed with status {response.status_code}")
    
    @task(1)
    def create_content(self):
        """Test content creation"""
        if not self.project_ids:
            return
        
        project_id = random.choice(self.project_ids)
        content_data = {
            "project_id": project_id,
            "title": f"Load Test Content {random.randint(1000, 9999)}",
            "content_type": random.choice(["blog", "article", "video", "image"]),
            "content_data": f"Content data for load testing {random.randint(1000, 9999)}",
            "status": random.choice(["draft", "published", "archived"]),
            "ai_generated": random.choice([True, False])
        }
        
        with self.client.post("/api/v1/content/", json=content_data, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 201:
                data = response.json()
                if "id" in data:
                    self.content_ids.append(data["id"])
                    response.success()
                else:
                    response.failure("Content creation response missing ID")
            else:
                response.failure(f"Content creation failed with status {response.status_code}")
    
    @task(1)
    def get_content(self):
        """Test getting specific content"""
        if not self.content_ids:
            return
        
        content_id = random.choice(self.content_ids)
        with self.client.get(f"/api/v1/content/{content_id}", headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == content_id:
                    response.success()
                else:
                    response.failure("Content ID mismatch")
            else:
                response.failure(f"Get content failed with status {response.status_code}")
    
    @task(1)
    def create_revenue(self):
        """Test revenue creation"""
        if not self.project_ids:
            return
        
        project_id = random.choice(self.project_ids)
        revenue_data = {
            "project_id": project_id,
            "amount": random.uniform(100, 5000),
            "source": f"load_test_source_{random.randint(1, 10)}",
            "description": f"Revenue from load testing {random.randint(1000, 9999)}"
        }
        
        with self.client.post("/api/v1/revenue/", json=revenue_data, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 201:
                data = response.json()
                if "id" in data:
                    self.revenue_ids.append(data["id"])
                    response.success()
                else:
                    response.failure("Revenue creation response missing ID")
            else:
                response.failure(f"Revenue creation failed with status {response.status_code}")
    
    @task(1)
    def ai_generate_content(self):
        """Test AI content generation"""
        ai_data = {
            "prompt": f"Write a blog post about load testing and performance optimization {random.randint(1000, 9999)}",
            "model": random.choice(["gpt-4", "gpt-3.5-turbo"]),
            "max_tokens": random.randint(100, 1000),
            "temperature": random.uniform(0.1, 1.0)
        }
        
        with self.client.post("/api/v1/ai/generate", json=ai_data, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "content" in data and "tokens_used" in data:
                    response.success()
                else:
                    response.failure("AI generation response missing required fields")
            else:
                response.failure(f"AI generation failed with status {response.status_code}")
    
    @task(1)
    def ai_sentiment_analysis(self):
        """Test AI sentiment analysis"""
        sentiment_data = {
            "text": f"This is a test text for sentiment analysis during load testing {random.randint(1000, 9999)}. "
                   f"It contains both positive and negative elements to test the analysis capabilities."
        }
        
        with self.client.post("/api/v1/ai/sentiment", json=sentiment_data, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "sentiment" in data and "confidence" in data:
                    response.success()
                else:
                    response.failure("Sentiment analysis response missing required fields")
            else:
                response.failure(f"Sentiment analysis failed with status {response.status_code}")
    
    @task(1)
    def ethics_check(self):
        """Test ethics check"""
        ethics_data = {
            "content": f"This is test content for ethics checking during load testing {random.randint(1000, 9999)}. "
                      f"It should be evaluated for ethical considerations and potential issues.",
            "content_type": random.choice(["blog", "article", "video"]),
            "project_id": random.choice(self.project_ids) if self.project_ids else 1
        }
        
        with self.client.post("/api/v1/ethics/check", json=ethics_data, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "is_ethical" in data and "confidence" in data:
                    response.success()
                else:
                    response.failure("Ethics check response missing required fields")
            else:
                response.failure(f"Ethics check failed with status {response.status_code}")
    
    @task(1)
    def get_performance_metrics(self):
        """Test performance metrics endpoint"""
        with self.client.get("/api/v1/performance/metrics", headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "score" in data and "metrics" in data:
                    response.success()
                else:
                    response.failure("Performance metrics response missing required fields")
            else:
                response.failure(f"Performance metrics failed with status {response.status_code}")
    
    @task(1)
    def cloud_backup(self):
        """Test cloud backup functionality"""
        backup_data = {
            "project_id": random.choice(self.project_ids) if self.project_ids else 1,
            "backup_type": random.choice(["full", "incremental"])
        }
        
        with self.client.post("/api/v1/cloud/backup", json=backup_data, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "backup_id" in data and "status" in data:
                    response.success()
                else:
                    response.failure("Cloud backup response missing required fields")
            else:
                response.failure(f"Cloud backup failed with status {response.status_code}")
    
    @task(1)
    def test_monitoring_endpoints(self):
        """Test monitoring test endpoints"""
        test_endpoints = [
            ("/api/v1/test/error", {"error_type": "test_error"}),
            ("/api/v1/test/metrics", {}),
            ("/api/v1/test/performance", {"duration": random.uniform(0.1, 2.0)}),
            ("/api/v1/test/health", {}),
            ("/api/v1/test/logs", {})
        ]
        
        endpoint, data = random.choice(test_endpoints)
        
        if data:
            with self.client.post(endpoint, json=data, headers=self.auth_headers, catch_response=True) as response:
                if response.status_code in [200, 201]:
                    response.success()
                else:
                    response.failure(f"Test endpoint {endpoint} failed with status {response.status_code}")
        else:
            with self.client.get(endpoint, headers=self.auth_headers, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Test endpoint {endpoint} failed with status {response.status_code}")

class AdminUser(CKEmpireUser):
    """Admin user with additional privileges"""
    
    wait_time = between(2, 5)  # Slower pace for admin operations
    
    @task(1)
    def delete_project(self):
        """Test project deletion (admin only)"""
        if not self.project_ids:
            return
        
        project_id = self.project_ids.pop()  # Remove from list
        with self.client.delete(f"/api/v1/projects/{project_id}", headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 204:
                response.success()
            else:
                response.failure(f"Project deletion failed with status {response.status_code}")
    
    @task(1)
    def delete_content(self):
        """Test content deletion (admin only)"""
        if not self.content_ids:
            return
        
        content_id = self.content_ids.pop()  # Remove from list
        with self.client.delete(f"/api/v1/content/{content_id}", headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 204:
                response.success()
            else:
                response.failure(f"Content deletion failed with status {response.status_code}")
    
    @task(1)
    def system_optimization(self):
        """Test system optimization (admin only)"""
        optimization_data = {
            "target": random.choice(["response_time", "throughput", "memory_usage"]),
            "threshold": random.uniform(0.1, 1.0)
        }
        
        with self.client.post("/api/v1/performance/optimize", json=optimization_data, headers=self.auth_headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "optimizations" in data and "improvement" in data:
                    response.success()
                else:
                    response.failure("System optimization response missing required fields")
            else:
                response.failure(f"System optimization failed with status {response.status_code}")

class ReadOnlyUser(CKEmpireUser):
    """Read-only user for testing read operations under load"""
    
    wait_time = between(0.5, 2)  # Faster pace for read operations
    
    @task(5)
    def read_only_health_check(self):
        """Frequent health checks"""
        self.health_check()
    
    @task(3)
    def read_only_metrics(self):
        """Frequent metrics checks"""
        self.get_metrics()
    
    @task(2)
    def read_only_projects(self):
        """Frequent project reads"""
        self.get_projects()
    
    @task(1)
    def read_only_performance(self):
        """Frequent performance checks"""
        self.get_performance_metrics()

# Custom event handlers for monitoring
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when a test is starting"""
    print("🚀 Load test starting...")
    print(f"Target host: {environment.host}")
    print(f"Number of users: {environment.runner.user_count if environment.runner else 'Unknown'}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when a test is ending"""
    print("🏁 Load test completed!")
    
    # Print summary statistics
    if hasattr(environment, 'stats'):
        stats = environment.stats
        print("\n📊 Test Summary:")
        print(f"Total requests: {stats.total.num_requests}")
        print(f"Failed requests: {stats.total.num_failures}")
        print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
        print(f"Max response time: {stats.total.max_response_time:.2f}ms")
        print(f"Min response time: {stats.total.min_response_time:.2f}ms")
        print(f"Requests per second: {stats.total.current_rps:.2f}")

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """Called for every request"""
    if exception:
        print(f"❌ Request failed: {name} - {exception}")
    elif response.status_code >= 400:
        print(f"⚠️  Request error: {name} - Status {response.status_code}")

# Custom metrics collection
class CustomMetrics:
    """Custom metrics collection for load testing"""
    
    def __init__(self):
        self.response_times = []
        self.error_counts = {}
        self.success_counts = {}
    
    def record_request(self, name, response_time, success, status_code):
        """Record request metrics"""
        self.response_times.append(response_time)
        
        if success:
            self.success_counts[name] = self.success_counts.get(name, 0) + 1
        else:
            self.error_counts[name] = self.error_counts.get(name, 0) + 1
    
    def get_summary(self):
        """Get metrics summary"""
        if not self.response_times:
            return {}
        
        return {
            "avg_response_time": sum(self.response_times) / len(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "total_requests": len(self.response_times),
            "success_counts": self.success_counts,
            "error_counts": self.error_counts
        }

# Global metrics instance
custom_metrics = CustomMetrics()

# Add metrics collection to request events
@events.request.add_listener
def collect_metrics(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """Collect custom metrics"""
    success = exception is None and response.status_code < 400
    custom_metrics.record_request(name, response_time, success, response.status_code if response else 0)

@events.test_stop.add_listener
def print_custom_metrics(environment, **kwargs):
    """Print custom metrics at test end"""
    summary = custom_metrics.get_summary()
    if summary:
        print("\n📈 Custom Metrics Summary:")
        print(f"Average response time: {summary['avg_response_time']:.2f}ms")
        print(f"Min response time: {summary['min_response_time']:.2f}ms")
        print(f"Max response time: {summary['max_response_time']:.2f}ms")
        print(f"Total requests: {summary['total_requests']}")
        print(f"Success counts: {summary['success_counts']}")
        print(f"Error counts: {summary['error_counts']}") 