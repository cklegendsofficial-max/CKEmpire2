"""
Performance monitoring and analytics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import time
from datetime import datetime, timedelta

from database import get_db
from performance import (
    get_performance_summary, 
    analyze_performance, 
    get_index_recommendations,
    cache,
    metrics,
    clear_cache_pattern,
    get_user_profile,
    get_project_summary,
    calculate_revenue_metrics
)

router = APIRouter(prefix="/performance", tags=["performance"])

@router.get("/metrics")
async def get_performance_metrics():
    """Get current performance metrics"""
    try:
        summary = get_performance_summary()
        return {
            "status": "success",
            "data": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}"
        )

@router.get("/analysis")
async def get_performance_analysis():
    """Get performance analysis and recommendations"""
    try:
        analysis = analyze_performance()
        return {
            "status": "success",
            "data": analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance analysis: {str(e)}"
        )

@router.get("/slow-queries")
async def get_slow_queries(threshold: float = 1.0):
    """Get slow queries above threshold"""
    try:
        slow_queries = metrics.get_slow_queries(threshold)
        return {
            "status": "success",
            "data": {
                "slow_queries": slow_queries,
                "count": len(slow_queries),
                "threshold": threshold
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get slow queries: {str(e)}"
        )

@router.get("/health")
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
            "uptime_seconds": (datetime.utcnow() - metrics.start_time).total_seconds(),
            "total_queries": len(metrics.query_times),
            "cache_hit_rate": metrics.get_cache_hit_rate(),
            "lru_cache_hit_rate": metrics.get_lru_cache_hit_rate()
        }
        
        return {
            "status": "healthy" if redis_status == "connected" else "degraded",
            "data": health_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )

# Cached endpoints for demonstration
@router.get("/cached-summary")
async def get_cached_summary():
    """Get cached performance summary"""
    try:
        summary = get_performance_summary()
        return {
            "status": "success",
            "data": summary,
            "cached": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cached summary: {str(e)}"
        )

@router.get("/user-profile/{user_id}")
async def get_user_profile_endpoint(user_id: int):
    """Get user profile with LRU caching"""
    try:
        profile = get_user_profile(user_id)
        return {
            "status": "success",
            "data": profile,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )

@router.get("/project-summary/{project_id}")
async def get_project_summary_endpoint(project_id: int):
    """Get project summary with Redis caching"""
    try:
        summary = get_project_summary(project_id)
        return {
            "status": "success",
            "data": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project summary: {str(e)}"
        )

@router.get("/revenue-metrics")
async def get_revenue_metrics(period: str = "monthly"):
    """Get revenue metrics with LRU caching"""
    try:
        metrics_data = calculate_revenue_metrics(period)
        return {
            "status": "success",
            "data": metrics_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get revenue metrics: {str(e)}"
        )

@router.delete("/clear-cache")
async def clear_cache():
    """Clear all performance caches"""
    try:
        # Clear Redis cache patterns
        patterns = ["lru_cache:*", "api:*", "projects:*"]
        cleared_count = 0
        
        for pattern in patterns:
            if clear_cache_pattern(pattern):
                cleared_count += 1
        
        return {
            "status": "success",
            "message": f"Cleared {cleared_count} cache patterns",
            "patterns_cleared": patterns,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )

@router.get("/cache-stats")
async def get_cache_stats():
    """Get detailed cache statistics"""
    try:
        redis_info = cache.get_cluster_info()
        
        stats = {
            "redis": {
                "mode": redis_info.get("mode", "unknown"),
                "status": redis_info.get("status", "unknown"),
                "cluster_info": redis_info
            },
            "cache_stats": {
                "hits": metrics.cache_stats["hits"],
                "misses": metrics.cache_stats["misses"],
                "hit_rate": metrics.get_cache_hit_rate()
            },
            "lru_cache_stats": {
                "hits": metrics.lru_cache_stats["hits"],
                "misses": metrics.lru_cache_stats["misses"],
                "hit_rate": metrics.get_lru_cache_hit_rate()
            }
        }
        
        return {
            "status": "success",
            "data": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache stats: {str(e)}"
        )

@router.get("/database-recommendations")
async def get_database_recommendations(db: Session = Depends(get_db)):
    """Get database index recommendations"""
    try:
        recommendations = get_index_recommendations(db)
        return {
            "status": "success",
            "data": {
                "recommendations": recommendations,
                "count": len(recommendations)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database recommendations: {str(e)}"
        )

@router.get("/alerts")
async def get_performance_alerts():
    """Get current performance alerts"""
    try:
        alerts = metrics.performance_alerts
        return {
            "status": "success",
            "data": {
                "alerts": alerts,
                "count": len(alerts),
                "severity_counts": {
                    "critical": len([a for a in alerts if a.get("severity") == "critical"]),
                    "warning": len([a for a in alerts if a.get("severity") == "warning"]),
                    "info": len([a for a in alerts if a.get("severity") == "info"])
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance alerts: {str(e)}"
        ) 