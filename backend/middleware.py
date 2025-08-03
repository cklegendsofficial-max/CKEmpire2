"""
Middleware for automatic monitoring and metrics collection.
"""

import time
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from monitoring import get_monitoring

logger = structlog.get_logger()

class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic request monitoring"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.monitoring = get_monitoring()
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract request information
        method = request.method
        endpoint = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request start
        logger.info("Request started", 
                   method=method, 
                   endpoint=endpoint, 
                   client_ip=client_ip)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            self.monitoring.record_http_request(
                method=method,
                endpoint=endpoint,
                status=response.status_code,
                duration=duration
            )
            
            # Log successful request
            logger.info("Request completed", 
                       method=method, 
                       endpoint=endpoint, 
                       status=response.status_code, 
                       duration=duration)
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Record error
            self.monitoring.record_error(
                error_type=type(e).__name__,
                endpoint=endpoint,
                error_message=str(e)
            )
            
            # Log error
            logger.error("Request failed", 
                        method=method, 
                        endpoint=endpoint, 
                        error=str(e), 
                        duration=duration)
            
            raise

class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Middleware for health check endpoint"""
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            # Return health check response
            monitoring = get_monitoring()
            health_status = monitoring.health_check()
            
            return Response(
                content=str(health_status),
                media_type="application/json",
                status_code=200
            )
        
        return await call_next(request)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for metrics endpoint"""
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/metrics":
            # Return Prometheus metrics
            monitoring = get_monitoring()
            metrics = monitoring.get_metrics()
            
            return Response(
                content=metrics,
                media_type="text/plain",
                status_code=200
            )
        
        return await call_next(request) 