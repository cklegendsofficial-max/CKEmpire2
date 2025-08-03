"""
Performance monitoring and metrics router
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import time

from database import get_db
from performance import (
    get_metrics, get_performance_summary, analyze_performance,
    get_index_recommendations, clear_cache_pattern, cache, metrics,
    performance_monitor, cache_decorator
)
from models import SuccessResponse

router = APIRouter()

@router.get("/metrics")
async def prometheus_metrics():
    """Get Prometheus metrics"""
    try:
        metrics_data = get_metrics()
        return Response(content=metrics_data, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/performance/summary")
@performance_monitor
async def get_performance_summary_endpoint():
    """Get performance summary"""
    try:
        summary = get_performance_summary()
        return {
            "status": "success",
            "data": summary,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance summary: {str(e)}")

@router.get("/performance/analysis")
@performance_monitor
async def get_performance_analysis():
    """Get detailed performance analysis and recommendations"""
    try:
        analysis = analyze_performance()
        return {
            "status": "success",
            "data": analysis,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze performance: {str(e)}")

@router.get("/performance/recommendations")
@performance_monitor
async def get_database_recommendations(db: Session = Depends(get_db)):
    """Get database optimization recommendations"""
    try:
        recommendations = get_index_recommendations(db)
        return {
            "status": "success",
            "data": {
                "recommendations": recommendations,
                "total_count": len(recommendations)
            },
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.post("/cache/clear")
async def clear_cache(pattern: str = "*"):
    """Clear cache entries matching pattern"""
    try:
        success = clear_cache_pattern(pattern)
        if success:
            return SuccessResponse(message=f"Cache cleared for pattern: {pattern}")
        else:
            raise HTTPException(status_code=500, detail="Failed to clear cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    try:
        stats = {
            "hit_rate": metrics.get_cache_hit_rate(),
            "hits": metrics.cache_stats["hits"],
            "misses": metrics.cache_stats["misses"],
            "total_requests": metrics.cache_stats["hits"] + metrics.cache_stats["misses"]
        }
        return {
            "status": "success",
            "data": stats,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache stats: {str(e)}")

@router.get("/performance/slow-queries")
@performance_monitor
async def get_slow_queries(threshold: float = 1.0):
    """Get slow queries above threshold"""
    try:
        slow_queries = metrics.get_slow_queries(threshold)
        return {
            "status": "success",
            "data": {
                "slow_queries": slow_queries,
                "threshold": threshold,
                "count": len(slow_queries)
            },
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get slow queries: {str(e)}")

@router.get("/performance/health")
async def performance_health_check():
    """Health check for performance monitoring"""
    try:
        # Check if Redis is available
        redis_healthy = cache.redis_client is not None
        if redis_healthy:
            try:
                cache.redis_client.ping()
                redis_status = "connected"
            except:
                redis_status = "disconnected"
        else:
            redis_status = "unavailable"
        
        health_data = {
            "redis": redis_status,
            "metrics_collection": "active",
            "uptime_seconds": (metrics.start_time - metrics.start_time).total_seconds(),
            "total_queries": len(metrics.query_times),
            "cache_hit_rate": metrics.get_cache_hit_rate()
        }
        
        return {
            "status": "healthy" if redis_status == "connected" else "degraded",
            "data": health_data,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# Cached endpoints for demonstration
@cache_decorator(expire=300, key_prefix="api")  # Cache for 5 minutes
@router.get("/performance/cached-summary")
async def get_cached_performance_summary():
    """Get cached performance summary (demonstrates caching)"""
    try:
        summary = get_performance_summary()
        return {
            "status": "success",
            "data": summary,
            "cached": True,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cached summary: {str(e)}")

@router.post("/performance/reset-metrics")
async def reset_performance_metrics():
    """Reset performance metrics (for testing)"""
    try:
        # Reset metrics
        metrics.query_times.clear()
        metrics.slow_queries.clear()
        metrics.cache_stats = {"hits": 0, "misses": 0}
        metrics.start_time = time.time()
        
        return SuccessResponse(message="Performance metrics reset successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset metrics: {str(e)}") 