"""
Performance monitoring and caching module for CK Empire Builder
"""

import time
import json
import logging
from typing import Any, Dict, Optional, Callable
from functools import wraps, lru_cache
from datetime import datetime, timedelta
import redis
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import structlog
from sqlalchemy.orm import Session
from sqlalchemy import text
import hashlib
import pickle

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
LRU_CACHE_HITS = Counter('lru_cache_hits_total', 'Total LRU cache hits')
LRU_CACHE_MISSES = Counter('lru_cache_misses_total', 'Total LRU cache misses')

class RedisClusterCache:
    """Enhanced Redis caching wrapper with cluster support"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", cluster_mode: bool = False):
        try:
            if cluster_mode:
                # Initialize Redis cluster
                self.redis_client = redis.RedisCluster.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
            else:
                # Initialize single Redis instance
                self.redis_client = redis.from_url(
                    redis_url, 
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
            
            self.redis_client.ping()
            self.cluster_mode = cluster_mode
            logger.info(f"✅ Redis {'cluster' if cluster_mode else 'single'} connection established")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.redis_client = None
            self.cluster_mode = False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with enhanced error handling"""
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
        """Set value in cache with compression for large objects"""
        if not self.redis_client:
            return False
        
        try:
            # Compress large objects
            serialized_value = json.dumps(value)
            if len(serialized_value) > 1024:  # Compress if > 1KB
                import gzip
                compressed_value = gzip.compress(serialized_value.encode())
                self.redis_client.setex(f"{key}:compressed", expire, compressed_value)
            else:
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
            # Delete both compressed and uncompressed versions
            self.redis_client.delete(key, f"{key}:compressed")
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
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """Get Redis cluster information"""
        if not self.redis_client or not self.cluster_mode:
            return {"mode": "single", "status": "unknown"}
        
        try:
            info = self.redis_client.info()
            return {
                "mode": "cluster",
                "status": "healthy",
                "nodes": len(info.get("cluster_nodes", [])),
                "slots_assigned": info.get("cluster_slots_assigned", 0),
                "slots_ok": info.get("cluster_slots_ok", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get cluster info: {e}")
            return {"mode": "cluster", "status": "error", "error": str(e)}

class PerformanceMetrics:
    """Enhanced performance metrics tracking"""
    
    def __init__(self):
        self.query_times = []
        self.slow_queries = []
        self.cache_stats = {"hits": 0, "misses": 0}
        self.lru_cache_stats = {"hits": 0, "misses": 0}
        self.start_time = datetime.utcnow()
        self.performance_alerts = []
    
    def record_query_time(self, query: str, duration: float):
        """Record database query time with enhanced tracking"""
        query_record = {
            "query": query,
            "duration": duration,
            "timestamp": datetime.utcnow()
        }
        
        self.query_times.append(query_record)
        
        # Track slow queries (> 1 second)
        if duration > 1.0:
            self.slow_queries.append(query_record)
            logger.warning(f"Slow query detected: {query} took {duration:.2f}s")
            
            # Alert if too many slow queries
            if len(self.slow_queries) > 10:
                self.performance_alerts.append({
                    "type": "slow_queries",
                    "message": f"High number of slow queries: {len(self.slow_queries)}",
                    "timestamp": datetime.utcnow(),
                    "severity": "warning"
                })
    
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
    
    def get_lru_cache_hit_rate(self) -> float:
        """Get LRU cache hit rate"""
        total = self.lru_cache_stats["hits"] + self.lru_cache_stats["misses"]
        if total == 0:
            return 0.0
        return self.lru_cache_stats["hits"] / total * 100
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.cache_stats["hits"] += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.cache_stats["misses"] += 1
    
    def record_lru_cache_hit(self):
        """Record LRU cache hit"""
        self.lru_cache_stats["hits"] += 1
        LRU_CACHE_HITS.inc()
    
    def record_lru_cache_miss(self):
        """Record LRU cache miss"""
        self.lru_cache_stats["misses"] += 1
        LRU_CACHE_MISSES.inc()

class PerformanceAnalyzer:
    """Enhanced performance analysis and recommendations"""
    
    def __init__(self, metrics: PerformanceMetrics):
        self.metrics = metrics
    
    def analyze_performance_logs(self) -> Dict[str, Any]:
        """Analyze performance logs and provide recommendations"""
        analysis = {
            "summary": {},
            "recommendations": [],
            "slow_queries": [],
            "cache_performance": {},
            "alerts": []
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
        lru_hit_rate = self.metrics.get_lru_cache_hit_rate()
        analysis["cache_performance"]["redis_hit_rate"] = hit_rate
        analysis["cache_performance"]["lru_hit_rate"] = lru_hit_rate
        
        if hit_rate < 50:
            analysis["recommendations"].append({
                "type": "cache",
                "priority": "medium",
                "message": f"Redis cache hit rate is low ({hit_rate:.1f}%). Consider expanding cache coverage.",
                "action": "Review cache strategy and add more cacheable endpoints"
            })
        
        if lru_hit_rate < 30:
            analysis["recommendations"].append({
                "type": "cache",
                "priority": "medium",
                "message": f"LRU cache hit rate is low ({lru_hit_rate:.1f}%). Consider optimizing function caching.",
                "action": "Review @lru_cache usage and optimize function calls"
            })
        
        # Add slow queries to analysis
        analysis["slow_queries"] = slow_queries[:10]  # Top 10 slowest queries
        
        # Add performance alerts
        analysis["alerts"] = self.metrics.performance_alerts
        
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
cache = RedisClusterCache()
metrics = PerformanceMetrics()
analyzer = PerformanceAnalyzer(metrics)

def lru_cache_decorator(maxsize: int = 128, ttl: int = 3600):
    """Enhanced LRU cache decorator with TTL support"""
    def decorator(func: Callable) -> Callable:
        # Create LRU cache with custom key function
        cached_func = lru_cache(maxsize=maxsize)(func)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Try to get from Redis first
            redis_key = f"lru_cache:{cache_key}"
            cached_result = cache.get(redis_key)
            
            if cached_result is not None:
                metrics.record_lru_cache_hit()
                return cached_result
            
            # Execute function and cache result
            start_time = time.time()
            result = cached_func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Record metrics
            metrics.record_query_time(f"{func.__name__}", duration)
            metrics.record_lru_cache_miss()
            
            # Cache the result in Redis
            cache.set(redis_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def cache_decorator(expire: int = 3600, key_prefix: str = ""):
    """Enhanced decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
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
    """Enhanced decorator for monitoring function performance"""
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
    """Get enhanced performance summary"""
    return {
        "uptime": (datetime.utcnow() - metrics.start_time).total_seconds(),
        "total_queries": len(metrics.query_times),
        "average_query_time": metrics.get_average_query_time(),
        "slow_queries_count": len(metrics.slow_queries),
        "redis_cache_hit_rate": metrics.get_cache_hit_rate(),
        "lru_cache_hit_rate": metrics.get_lru_cache_hit_rate(),
        "cache_stats": metrics.cache_stats,
        "lru_cache_stats": metrics.lru_cache_stats,
        "performance_alerts": len(metrics.performance_alerts),
        "redis_cluster_info": cache.get_cluster_info()
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

# Example cached functions for common operations
@lru_cache_decorator(maxsize=256, ttl=1800)
def get_user_profile(user_id: int) -> Dict[str, Any]:
    """Get user profile with LRU caching"""
    # Simulate database query
    time.sleep(0.1)
    return {
        "user_id": user_id,
        "username": f"user_{user_id}",
        "email": f"user_{user_id}@example.com",
        "created_at": datetime.utcnow().isoformat()
    }

@cache_decorator(expire=3600, key_prefix="projects")
def get_project_summary(project_id: int) -> Dict[str, Any]:
    """Get project summary with Redis caching"""
    # Simulate database query
    time.sleep(0.2)
    return {
        "project_id": project_id,
        "name": f"Project {project_id}",
        "status": "active",
        "revenue": 1000 * project_id,
        "last_updated": datetime.utcnow().isoformat()
    }

@lru_cache_decorator(maxsize=128, ttl=900)
def calculate_revenue_metrics(period: str = "monthly") -> Dict[str, Any]:
    """Calculate revenue metrics with LRU caching"""
    # Simulate complex calculation
    time.sleep(0.3)
    return {
        "period": period,
        "total_revenue": 50000,
        "growth_rate": 15.5,
        "top_sources": ["subscriptions", "ads", "consulting"],
        "calculated_at": datetime.utcnow().isoformat()
    } 