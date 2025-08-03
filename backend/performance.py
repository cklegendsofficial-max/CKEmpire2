"""
Performance monitoring and caching module for CK Empire Builder
"""

import time
import json
import logging
from typing import Any, Dict, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import redis
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import structlog
from sqlalchemy.orm import Session
from sqlalchemy import text

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
CACHE_HIT_COUNT = Counter('cache_hits_total', 'Total cache hits')
CACHE_MISS_COUNT = Counter('cache_misses_total', 'Total cache misses')
DB_QUERY_DURATION = Histogram('db_query_duration_seconds', 'Database query duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')

class RedisCache:
    """Redis caching wrapper"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                CACHE_HIT_COUNT.inc()
                logger.debug(f"Cache hit for key: {key}")
                return json.loads(value)
            else:
                CACHE_MISS_COUNT.inc()
                logger.debug(f"Cache miss for key: {key}")
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache"""
        if not self.redis_client:
            return False
        
        try:
            serialized_value = json.dumps(value)
            self.redis_client.setex(key, expire, serialized_value)
            logger.debug(f"Cache set for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            logger.debug(f"Cache delete for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> bool:
        """Clear cache entries matching pattern"""
        if not self.redis_client:
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cache entries matching pattern: {pattern}")
            return True
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return False

class PerformanceMetrics:
    """Performance metrics tracking"""
    
    def __init__(self):
        self.query_times = []
        self.slow_queries = []
        self.cache_stats = {"hits": 0, "misses": 0}
        self.start_time = datetime.utcnow()
    
    def record_query_time(self, query: str, duration: float):
        """Record database query time"""
        self.query_times.append({
            "query": query,
            "duration": duration,
            "timestamp": datetime.utcnow()
        })
        
        # Track slow queries (> 1 second)
        if duration > 1.0:
            self.slow_queries.append({
                "query": query,
                "duration": duration,
                "timestamp": datetime.utcnow()
            })
            logger.warning(f"Slow query detected: {query} took {duration:.2f}s")
    
    def get_average_query_time(self) -> float:
        """Get average query time"""
        if not self.query_times:
            return 0.0
        return sum(q["duration"] for q in self.query_times) / len(self.query_times)
    
    def get_slow_queries(self, threshold: float = 1.0) -> list:
        """Get queries slower than threshold"""
        return [q for q in self.query_times if q["duration"] > threshold]
    
    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate"""
        total = self.cache_stats["hits"] + self.cache_stats["misses"]
        if total == 0:
            return 0.0
        return self.cache_stats["hits"] / total * 100
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.cache_stats["hits"] += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.cache_stats["misses"] += 1

class PerformanceAnalyzer:
    """Performance analysis and recommendations"""
    
    def __init__(self, metrics: PerformanceMetrics):
        self.metrics = metrics
    
    def analyze_performance_logs(self) -> Dict[str, Any]:
        """Analyze performance logs and provide recommendations"""
        analysis = {
            "summary": {},
            "recommendations": [],
            "slow_queries": [],
            "cache_performance": {}
        }
        
        # Analyze query performance
        avg_query_time = self.metrics.get_average_query_time()
        slow_queries = self.metrics.get_slow_queries()
        
        analysis["summary"]["average_query_time"] = avg_query_time
        analysis["summary"]["total_queries"] = len(self.metrics.query_times)
        analysis["summary"]["slow_queries_count"] = len(slow_queries)
        
        # Generate recommendations
        if avg_query_time > 0.5:
            analysis["recommendations"].append({
                "type": "database",
                "priority": "high",
                "message": "Average query time is high. Consider adding database indexes.",
                "action": "Review and optimize database queries"
            })
        
        if len(slow_queries) > 5:
            analysis["recommendations"].append({
                "type": "database",
                "priority": "critical",
                "message": f"Found {len(slow_queries)} slow queries. Immediate optimization needed.",
                "action": "Analyze and optimize slow queries"
            })
        
        # Cache performance analysis
        hit_rate = self.metrics.get_cache_hit_rate()
        analysis["cache_performance"]["hit_rate"] = hit_rate
        
        if hit_rate < 50:
            analysis["recommendations"].append({
                "type": "cache",
                "priority": "medium",
                "message": f"Cache hit rate is low ({hit_rate:.1f}%). Consider expanding cache coverage.",
                "action": "Review cache strategy and add more cacheable endpoints"
            })
        
        # Add slow queries to analysis
        analysis["slow_queries"] = slow_queries[:10]  # Top 10 slowest queries
        
        return analysis
    
    def generate_index_recommendations(self, db: Session) -> list:
        """Generate database index recommendations"""
        recommendations = []
        
        try:
            # Analyze table sizes and query patterns
            tables = ["projects", "content", "revenues", "audit_logs"]
            
            for table in tables:
                # Check if table has indexes
                result = db.execute(text(f"""
                    SELECT COUNT(*) as index_count 
                    FROM sqlite_master 
                    WHERE type='index' AND tbl_name='{table}'
                """))
                index_count = result.scalar()
                
                if index_count < 2:  # Assuming we need at least 2 indexes per table
                    recommendations.append({
                        "table": table,
                        "recommendation": f"Add indexes to {table} table",
                        "priority": "medium",
                        "reason": f"Table {table} has only {index_count} indexes"
                    })
        
        except Exception as e:
            logger.error(f"Error generating index recommendations: {e}")
        
        return recommendations

# Global instances
cache = RedisCache()
metrics = PerformanceMetrics()
analyzer = PerformanceAnalyzer(metrics)

def cache_decorator(expire: int = 3600, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                metrics.record_cache_hit()
                return cached_result
            
            # Execute function and cache result
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Record metrics
            metrics.record_query_time(f"{func.__name__}", duration)
            metrics.record_cache_miss()
            
            # Cache the result
            cache.set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator

def performance_monitor(func: Callable) -> Callable:
    """Decorator for monitoring function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Record metrics
            metrics.record_query_time(f"{func.__name__}", duration)
            
            # Log performance
            logger.info(
                "Function performance",
                function=func.__name__,
                duration=duration,
                success=True
            )
            
            return result
        
        except Exception as e:
            duration = time.time() - start_time
            
            # Record error
            logger.error(
                "Function error",
                function=func.__name__,
                duration=duration,
                error=str(e),
                success=False
            )
            raise
    
    return wrapper

def get_metrics() -> str:
    """Get Prometheus metrics"""
    return generate_latest()

def get_performance_summary() -> Dict[str, Any]:
    """Get performance summary"""
    return {
        "uptime": (datetime.utcnow() - metrics.start_time).total_seconds(),
        "total_queries": len(metrics.query_times),
        "average_query_time": metrics.get_average_query_time(),
        "slow_queries_count": len(metrics.slow_queries),
        "cache_hit_rate": metrics.get_cache_hit_rate(),
        "cache_stats": metrics.cache_stats
    }

def clear_cache_pattern(pattern: str) -> bool:
    """Clear cache entries matching pattern"""
    return cache.clear_pattern(pattern)

def analyze_performance() -> Dict[str, Any]:
    """Analyze current performance and return recommendations"""
    return analyzer.analyze_performance_logs()

def get_index_recommendations(db: Session) -> list:
    """Get database index recommendations"""
    return analyzer.generate_index_recommendations(db) 