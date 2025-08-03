from locust import HttpUser, task, between, events
import json
import random
import time
from datetime import datetime

class CKEmpireUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Initialize user session"""
        self.client.headers = {
            "Content-Type": "application/json",
            "User-Agent": "CK-Empire-Performance-Test"
        }
        self.session_data = {
            "user_id": random.randint(1, 1000),
            "start_time": time.time()
        }
    
    @task(3)
    def get_metrics(self):
        """Test metrics endpoint"""
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get metrics: {response.status_code}")
    
    @task(2)
    def get_health(self):
        """Test health check endpoint"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get health: {response.status_code}")
    
    @task(2)
    def get_projects(self):
        """Test projects endpoint with caching"""
        with self.client.get("/projects", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get projects: {response.status_code}")
    
    @task(1)
    def create_project(self):
        """Test project creation"""
        project_data = {
            "name": f"Test Project {random.randint(1, 1000)}",
            "description": "Performance test project",
            "status": "active",
            "metadata_encrypted": "test-metadata"
        }
        with self.client.post("/projects", json=project_data, catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Failed to create project: {response.status_code}")
    
    @task(1)
    def get_revenue(self):
        """Test revenue endpoint"""
        with self.client.get("/revenue", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get revenue: {response.status_code}")
    
    @task(1)
    def create_revenue(self):
        """Test revenue creation"""
        revenue_data = {
            "amount": random.randint(100, 10000),
            "source": "performance-test",
            "date": "2024-01-01",
            "metadata_encrypted": "test-revenue"
        }
        with self.client.post("/revenue", json=revenue_data, catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Failed to create revenue: {response.status_code}")
    
    @task(1)
    def test_ethics_check(self):
        """Test ethics endpoint"""
        content_data = {
            "content": "This is a test content for ethics checking",
            "content_type": "text",
            "user_id": "test-user"
        }
        with self.client.post("/ethics/check", json=content_data, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to check ethics: {response.status_code}")
    
    @task(1)
    def test_ai_ideas(self):
        """Test AI ideas generation"""
        idea_data = {
            "topic": "technology",
            "style": "viral",
            "count": 3
        }
        with self.client.post("/ai/ideas", json=idea_data, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to generate AI ideas: {response.status_code}")
    
    @task(2)
    def test_performance_metrics(self):
        """Test performance metrics endpoint"""
        with self.client.get("/performance/metrics", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get performance metrics: {response.status_code}")
    
    @task(1)
    def test_agi_state(self):
        """Test AGI state endpoint"""
        with self.client.get("/ai/agi-state", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get AGI state: {response.status_code}")
    
    @task(1)
    def test_cached_endpoints(self):
        """Test cached endpoints for performance"""
        endpoints = [
            "/performance/cached-summary",
            "/performance/health",
            "/projects/summary"
        ]
        endpoint = random.choice(endpoints)
        with self.client.get(endpoint, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get cached endpoint {endpoint}: {response.status_code}")


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
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get metrics: {response.status_code}")
    
    @task(3)
    def rapid_health_check(self):
        """Rapid health checking"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get health: {response.status_code}")
    
    @task(2)
    def rapid_projects_check(self):
        """Rapid projects checking"""
        with self.client.get("/projects", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get projects: {response.status_code}")


class RedisClusterUser(HttpUser):
    wait_time = between(0.5, 1.5)
    weight = 2  # Medium weight for Redis cluster testing
    
    def on_start(self):
        """Initialize user session"""
        self.client.headers = {
            "Content-Type": "application/json",
            "User-Agent": "CK-Empire-Redis-Test"
        }
    
    @task(3)
    def test_redis_cache_hits(self):
        """Test Redis cache hit performance"""
        # Make multiple requests to the same endpoint to test cache hits
        for i in range(5):
            with self.client.get("/performance/cached-summary", catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed to get cached summary: {response.status_code}")
    
    @task(2)
    def test_lru_cache_performance(self):
        """Test LRU cache performance"""
        user_id = random.randint(1, 100)
        with self.client.get(f"/performance/user-profile/{user_id}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get user profile: {response.status_code}")
    
    @task(2)
    def test_cache_invalidation(self):
        """Test cache invalidation performance"""
        # First request to populate cache
        with self.client.get("/performance/cached-summary", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get cached summary: {response.status_code}")
        
        # Clear cache
        with self.client.delete("/performance/clear-cache", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to clear cache: {response.status_code}")
        
        # Second request to test cache miss
        with self.client.get("/performance/cached-summary", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get cached summary after clear: {response.status_code}")


class DatabaseLoadUser(HttpUser):
    wait_time = between(2, 5)
    weight = 1  # Lower weight for database intensive testing
    
    def on_start(self):
        """Initialize user session"""
        self.client.headers = {
            "Content-Type": "application/json",
            "User-Agent": "CK-Empire-DB-Test"
        }
    
    @task(3)
    def test_database_queries(self):
        """Test database query performance"""
        # Test complex database operations
        with self.client.get("/performance/slow-queries", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get slow queries: {response.status_code}")
    
    @task(2)
    def test_database_analytics(self):
        """Test database analytics performance"""
        with self.client.get("/analytics/summary", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get analytics: {response.status_code}")
    
    @task(1)
    def test_database_writes(self):
        """Test database write performance"""
        data = {
            "name": f"DB Test {random.randint(1, 1000)}",
            "description": "Database performance test",
            "status": "active"
        }
        with self.client.post("/projects", json=data, catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Failed to create project: {response.status_code}")


# Custom event listeners for performance monitoring
@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """Custom request handler for performance monitoring"""
    if exception:
        print(f"Request failed: {name} - {exception}")
    else:
        print(f"Request completed: {name} - {response_time}ms - {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when a test starts"""
    print(f"🚀 Performance test started at {datetime.now()}")
    print(f"Target host: {environment.host}")
    print(f"Number of users: {environment.runner.user_count}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when a test stops"""
    print(f"🏁 Performance test completed at {datetime.now()}")
    
    # Print summary statistics
    stats = environment.stats
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Failed requests: {stats.total.num_failures}")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"95th percentile: {stats.total.response_time_percentile(0.95):.2f}ms")
    print(f"99th percentile: {stats.total.response_time_percentile(0.99):.2f}ms") 