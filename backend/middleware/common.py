"""
Common middleware for CK Empire Builder
Provides shared middleware functionality
"""

import time
import logging
import json
from typing import Callable, Dict, Any
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import StreamingResponse
import structlog

from config import settings, constants
from utils import log_operation, check_rate_limit

logger = structlog.get_logger()

class CommonMiddleware(BaseHTTPMiddleware):
    """Common middleware for request/response processing"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request and response"""
        start_time = time.time()
        
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Log request
        self.log_request(request, client_ip)
        
        # Check rate limit
        await self.check_rate_limit(request, client_ip)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Log response
            self.log_response(request, response, start_time)
            
            # Add security headers
            self.add_security_headers(response)
            
            return response
            
        except Exception as e:
            # Log error
            self.log_error(request, e, start_time)
            raise
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct IP
        return request.client.host if request.client else "unknown"
    
    def log_request(self, request: Request, client_ip: str):
        """Log incoming request"""
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "client_ip": client_ip,
            "user_agent": request.headers.get("User-Agent", ""),
            "content_length": request.headers.get("Content-Length", 0)
        }
        
        logger.info("Incoming request", **log_data)
    
    def log_response(self, request: Request, response: Response, start_time: float):
        """Log response"""
        duration = time.time() - start_time
        
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "duration": round(duration, 3),
            "content_length": response.headers.get("Content-Length", 0)
        }
        
        logger.info("Response sent", **log_data)
    
    def log_error(self, request: Request, error: Exception, start_time: float):
        """Log error"""
        duration = time.time() - start_time
        
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "error": str(error),
            "duration": round(duration, 3)
        }
        
        logger.error("Request failed", **log_data)
    
    async def check_rate_limit(self, request: Request, client_ip: str):
        """Check rate limit for client"""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return
        
        # Check rate limit
        identifier = f"ip:{client_ip}"
        allowed, info = check_rate_limit(identifier, settings.RATE_LIMIT_PER_MINUTE, 60)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=constants.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"X-RateLimit-Reset": str(info.get("reset_time", ""))}
            )
    
    def add_security_headers(self, response: Response):
        """Add security headers to response"""
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Remove server information
        if "Server" in response.headers:
            del response.headers["Server"]

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request with logging"""
        # Create structured log context
        log_context = {
            "request_id": self.generate_request_id(),
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": self.get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", ""),
            "timestamp": time.time()
        }
        
        # Log request
        logger.info("Request started", **log_context)
        
        try:
            response = await call_next(request)
            
            # Add response info to context
            log_context.update({
                "status_code": response.status_code,
                "response_size": len(response.body) if hasattr(response, 'body') else 0
            })
            
            logger.info("Request completed", **log_context)
            return response
            
        except Exception as e:
            log_context["error"] = str(e)
            logger.error("Request failed", **log_context)
            raise
    
    def generate_request_id(self) -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting metrics"""
    
    def __init__(self, app, metrics_collector=None):
        super().__init__(app)
        self.metrics_collector = metrics_collector
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request with metrics collection"""
        start_time = time.time()
        
        # Collect request metrics
        self.collect_request_metrics(request)
        
        try:
            response = await call_next(request)
            
            # Collect response metrics
            duration = time.time() - start_time
            self.collect_response_metrics(request, response, duration)
            
            return response
            
        except Exception as e:
            # Collect error metrics
            duration = time.time() - start_time
            self.collect_error_metrics(request, e, duration)
            raise
    
    def collect_request_metrics(self, request: Request):
        """Collect request metrics"""
        if self.metrics_collector:
            self.metrics_collector.increment_counter(
                "http_requests_total",
                labels={
                    "method": request.method,
                    "path": request.url.path,
                    "status": "started"
                }
            )
    
    def collect_response_metrics(self, request: Request, response: Response, duration: float):
        """Collect response metrics"""
        if self.metrics_collector:
            self.metrics_collector.increment_counter(
                "http_requests_total",
                labels={
                    "method": request.method,
                    "path": request.url.path,
                    "status": str(response.status_code)
                }
            )
            
            self.metrics_collector.observe_histogram(
                "http_request_duration_seconds",
                duration,
                labels={
                    "method": request.method,
                    "path": request.url.path
                }
            )
    
    def collect_error_metrics(self, request: Request, error: Exception, duration: float):
        """Collect error metrics"""
        if self.metrics_collector:
            self.metrics_collector.increment_counter(
                "http_requests_total",
                labels={
                    "method": request.method,
                    "path": request.url.path,
                    "status": "error"
                }
            )
            
            self.metrics_collector.observe_histogram(
                "http_request_duration_seconds",
                duration,
                labels={
                    "method": request.method,
                    "path": request.url.path
                }
            )

class CORSMiddleware(BaseHTTPMiddleware):
    """Enhanced CORS middleware"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request with CORS handling"""
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            self.add_cors_headers(response)
            return response
        
        # Process normal request
        response = await call_next(request)
        self.add_cors_headers(response)
        return response
    
    def add_cors_headers(self, response: Response):
        """Add CORS headers to response"""
        response.headers["Access-Control-Allow-Origin"] = ", ".join(settings.ALLOWED_ORIGINS)
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "3600"

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for additional protection"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request with security checks"""
        # Security checks
        self.check_security_headers(request)
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        self.add_security_headers(response)
        
        return response
    
    def check_security_headers(self, request: Request):
        """Check security headers"""
        # Check for suspicious headers
        suspicious_headers = [
            "X-Forwarded-Host",
            "X-Forwarded-Proto",
            "X-Forwarded-For"
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                # Log suspicious header
                logger.warning(f"Suspicious header detected: {header}")
    
    def add_security_headers(self, response: Response):
        """Add security headers"""
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # Remove server information
        if "Server" in response.headers:
            del response.headers["Server"] 