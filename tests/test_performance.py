"""
Performance monitoring tests for CK Empire Builder
"""

import pytest
import time
import json
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from backend.performance import (
    RedisCache, PerformanceMetrics, PerformanceAnalyzer,
    cache_decorator, performance_monitor, get_metrics,
    get_performance_summary, analyze_performance
)
from backend.database import get_db, SessionLocal


class TestRedisCache:
    """Test Redis caching functionality"""
    
    def test_cache_initialization(self):
        """Test Redis cache initialization"""
        with patch('redis.from_url') as mock_redis:
            mock_client = Mock()
            mock_redis.return_value = mock_client
            mock_client.ping.return_value = True
            
            cache = RedisCache("redis://localhost:6379")
            assert cache.redis_client is not None
    
    def test_cache_get_set(self):
        """Test cache get and set operations"""
        with patch('redis.from_url') as mock_redis:
            mock_client = Mock()
            mock_redis.return_value = mock_client
            mock_client.ping.return_value = True
            
            cache = RedisCache()
            
            # Test set
            test_data = {"test": "data"}
            mock_client.setex.return_value = True
            result = cache.set("test_key", test_data)
            assert result is True
            
            # Test get
            mock_client.get.return_value = json.dumps(test_data)
            cached_data = cache.get("test_key")
            assert cached_data == test_data
    
    def test_cache_miss(self):
        """Test cache miss scenario"""
        with patch('redis.from_url') as mock_redis:
            mock_client = Mock()
            mock_redis.return_value = mock_client
            mock_client.ping.return_value = True
            mock_client.get.return_value = None
            
            cache = RedisCache()
            result = cache.get("nonexistent_key")
            assert result is None


class TestPerformanceMetrics:
    """Test performance metrics tracking"""
    
    def test_metrics_initialization(self):
        """Test metrics initialization"""
        metrics = PerformanceMetrics()
        assert len(metrics.query_times) == 0
        assert len(metrics.slow_queries) == 0
        assert metrics.cache_stats["hits"] == 0
        assert metrics.cache_stats["misses"] == 0
    
    def test_record_query_time(self):
        """Test recording query times"""
        metrics = PerformanceMetrics()
        
        # Record a fast query
        metrics.record_query_time("SELECT * FROM projects", 0.1)
        assert len(metrics.query_times) == 1
        assert len(metrics.slow_queries) == 0
        
        # Record a slow query
        metrics.record_query_time("SELECT * FROM projects", 1.5)
        assert len(metrics.query_times) == 2
        assert len(metrics.slow_queries) == 1
    
    def test_average_query_time(self):
        """Test average query time calculation"""
        metrics = PerformanceMetrics()
        
        # Add some query times
        metrics.record_query_time("query1", 0.5)
        metrics.record_query_time("query2", 1.0)
        metrics.record_query_time("query3", 1.5)
        
        avg_time = metrics.get_average_query_time()
        assert avg_time == 1.0
    
    def test_cache_hit_rate(self):
        """Test cache hit rate calculation"""
        metrics = PerformanceMetrics()
        
        # No requests yet
        assert metrics.get_cache_hit_rate() == 0.0
        
        # Add some hits and misses
        metrics.record_cache_hit()
        metrics.record_cache_hit()
        metrics.record_cache_miss()
        
        hit_rate = metrics.get_cache_hit_rate()
        assert hit_rate == 66.66666666666666  # 2/3 * 100


class TestPerformanceAnalyzer:
    """Test performance analysis functionality"""
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        metrics = PerformanceMetrics()
        analyzer = PerformanceAnalyzer(metrics)
        assert analyzer.metrics == metrics
    
    def test_analyze_performance_logs(self):
        """Test performance analysis"""
        metrics = PerformanceMetrics()
        
        # Add some test data
        metrics.record_query_time("slow_query", 2.0)
        metrics.record_query_time("fast_query", 0.1)
        metrics.record_cache_hit()
        metrics.record_cache_miss()
        
        analyzer = PerformanceAnalyzer(metrics)
        analysis = analyzer.analyze_performance_logs()
        
        assert "summary" in analysis
        assert "recommendations" in analysis
        assert "slow_queries" in analysis
        assert "cache_performance" in analysis
        
        assert analysis["summary"]["total_queries"] == 2
        assert analysis["summary"]["slow_queries_count"] == 1
    
    def test_index_recommendations(self):
        """Test index recommendations generation"""
        metrics = PerformanceMetrics()
        analyzer = PerformanceAnalyzer(metrics)
        
        # Mock database session
        mock_db = Mock()
        mock_db.execute.return_value.scalar.return_value = 1
        
        recommendations = analyzer.generate_index_recommendations(mock_db)
        assert isinstance(recommendations, list)


class TestCacheDecorator:
    """Test cache decorator functionality"""
    
    def test_cache_decorator(self):
        """Test cache decorator with simple function"""
        call_count = 0
        
        @cache_decorator(expire=60, key_prefix="test")
        def test_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call should execute function
        result1 = test_function(1, 2)
        assert result1 == 3
        assert call_count == 1
        
        # Second call should use cache
        result2 = test_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # Should not increment


class TestPerformanceMonitor:
    """Test performance monitoring decorator"""
    
    def test_performance_monitor(self):
        """Test performance monitoring decorator"""
        call_count = 0
        
        @performance_monitor
        def test_function():
            nonlocal call_count
            call_count += 1
            time.sleep(0.1)  # Simulate some work
            return "success"
        
        result = test_function()
        assert result == "success"
        assert call_count == 1


class TestPerformanceEndpoints:
    """Test performance-related API endpoints"""
    
    def test_get_metrics(self):
        """Test Prometheus metrics endpoint"""
        metrics_data = get_metrics()
        assert isinstance(metrics_data, str)
        assert "http_requests_total" in metrics_data
    
    def test_get_performance_summary(self):
        """Test performance summary"""
        summary = get_performance_summary()
        assert "uptime" in summary
        assert "total_queries" in summary
        assert "average_query_time" in summary
        assert "cache_hit_rate" in summary
    
    def test_analyze_performance(self):
        """Test performance analysis"""
        analysis = analyze_performance()
        assert "summary" in analysis
        assert "recommendations" in analysis
        assert "slow_queries" in analysis
        assert "cache_performance" in analysis


class TestIntegration:
    """Integration tests for performance features"""
    
    def test_cache_and_metrics_integration(self):
        """Test integration between cache and metrics"""
        metrics = PerformanceMetrics()
        
        # Simulate cache operations
        metrics.record_cache_hit()
        metrics.record_cache_hit()
        metrics.record_cache_miss()
        
        # Check metrics
        hit_rate = metrics.get_cache_hit_rate()
        assert hit_rate == 66.66666666666666
        
        # Check cache stats
        assert metrics.cache_stats["hits"] == 2
        assert metrics.cache_stats["misses"] == 1
    
    def test_performance_analysis_with_data(self):
        """Test performance analysis with realistic data"""
        metrics = PerformanceMetrics()
        
        # Simulate realistic usage
        for i in range(10):
            metrics.record_query_time(f"query_{i}", 0.1 + (i * 0.1))
            if i % 2 == 0:
                metrics.record_cache_hit()
            else:
                metrics.record_cache_miss()
        
        analyzer = PerformanceAnalyzer(metrics)
        analysis = analyzer.analyze_performance_logs()
        
        assert analysis["summary"]["total_queries"] == 10
        assert analysis["summary"]["slow_queries_count"] > 0
        assert analysis["cache_performance"]["hit_rate"] == 50.0


@pytest.fixture
def test_db():
    """Test database fixture"""
    # Create a test database session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestDatabasePerformance:
    """Test database performance features"""
    
    def test_database_query_monitoring(self, test_db):
        """Test database query monitoring"""
        metrics = PerformanceMetrics()
        
        # Simulate database queries
        start_time = time.time()
        # Simulate a query
        time.sleep(0.1)
        duration = time.time() - start_time
        
        metrics.record_query_time("SELECT * FROM projects", duration)
        
        assert len(metrics.query_times) == 1
        assert metrics.query_times[0]["query"] == "SELECT * FROM projects"
        assert metrics.query_times[0]["duration"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 