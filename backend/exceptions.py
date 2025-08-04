"""
Exception handling for CK Empire Builder
Provides custom exceptions and exception handlers
"""

import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from config import settings, constants
from utils import log_operation

logger = logging.getLogger(__name__)

class CKEmpireException(Exception):
    """Base exception for CK Empire Builder"""
    
    def __init__(self, message: str, error_code: str = None, status_code: int = 500, details: Any = None):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

class ValidationException(CKEmpireException):
    """Validation exception"""
    
    def __init__(self, message: str, field: str = None, details: Any = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=constants.HTTP_400_BAD_REQUEST,
            details=details
        )
        self.field = field

class AuthenticationException(CKEmpireException):
    """Authentication exception"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=constants.HTTP_401_UNAUTHORIZED
        )

class AuthorizationException(CKEmpireException):
    """Authorization exception"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=constants.HTTP_403_FORBIDDEN
        )

class NotFoundException(CKEmpireException):
    """Not found exception"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=constants.HTTP_404_NOT_FOUND
        )

class RateLimitException(CKEmpireException):
    """Rate limit exception"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=constants.HTTP_429_TOO_MANY_REQUESTS
        )

class DatabaseException(CKEmpireException):
    """Database exception"""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=constants.HTTP_500_INTERNAL_SERVER_ERROR
        )

class ExternalServiceException(CKEmpireException):
    """External service exception"""
    
    def __init__(self, message: str = "External service error", service: str = None):
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=constants.HTTP_503_SERVICE_UNAVAILABLE
        )
        self.service = service

class ConfigurationException(CKEmpireException):
    """Configuration exception"""
    
    def __init__(self, message: str = "Configuration error"):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=constants.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Exception handlers
async def ckempire_exception_handler(request: Request, exc: CKEmpireException) -> JSONResponse:
    """Handle CK Empire Builder exceptions"""
    # Log the exception
    log_operation(
        operation="exception_handled",
        details={
            "exception_type": exc.__class__.__name__,
            "message": exc.message,
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "path": str(request.url),
            "method": request.method
        },
        level="error"
    )
    
    # Create error response
    error_response = {
        "success": False,
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "type": exc.__class__.__name__
        },
        "timestamp": "2024-01-01T00:00:00Z"  # Will be replaced with actual timestamp
    }
    
    if exc.details:
        error_response["error"]["details"] = exc.details
    
    if hasattr(exc, 'field') and exc.field:
        error_response["error"]["field"] = exc.field
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    # Log the exception
    log_operation(
        operation="http_exception_handled",
        details={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": str(request.url),
            "method": request.method
        },
        level="warning"
    )
    
    # Create error response
    error_response = {
        "success": False,
        "error": {
            "code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "type": "HTTPException"
        },
        "timestamp": "2024-01-01T00:00:00Z"  # Will be replaced with actual timestamp
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions"""
    # Log the exception
    log_operation(
        operation="validation_exception_handled",
        details={
            "errors": exc.errors(),
            "path": str(request.url),
            "method": request.method
        },
        level="warning"
    )
    
    # Create error response
    error_response = {
        "success": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "type": "ValidationError",
            "details": exc.errors()
        },
        "timestamp": "2024-01-01T00:00:00Z"  # Will be replaced with actual timestamp
    }
    
    return JSONResponse(
        status_code=constants.HTTP_400_BAD_REQUEST,
        content=error_response
    )

async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation exceptions"""
    # Log the exception
    log_operation(
        operation="pydantic_validation_exception_handled",
        details={
            "errors": exc.errors(),
            "path": str(request.url),
            "method": request.method
        },
        level="warning"
    )
    
    # Create error response
    error_response = {
        "success": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Data validation failed",
            "type": "ValidationError",
            "details": exc.errors()
        },
        "timestamp": "2024-01-01T00:00:00Z"  # Will be replaced with actual timestamp
    }
    
    return JSONResponse(
        status_code=constants.HTTP_400_BAD_REQUEST,
        content=error_response
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions"""
    # Log the exception
    log_operation(
        operation="general_exception_handled",
        details={
            "exception_type": exc.__class__.__name__,
            "message": str(exc),
            "path": str(request.url),
            "method": request.method
        },
        level="error"
    )
    
    # Create error response
    error_response = {
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "type": "Exception"
        },
        "timestamp": "2024-01-01T00:00:00Z"  # Will be replaced with actual timestamp
    }
    
    # Add details in development mode
    if settings.DEBUG:
        error_response["error"]["details"] = {
            "exception_type": exc.__class__.__name__,
            "message": str(exc)
        }
    
    return JSONResponse(
        status_code=constants.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )

# Exception registry
EXCEPTION_HANDLERS = {
    CKEmpireException: ckempire_exception_handler,
    HTTPException: http_exception_handler,
    RequestValidationError: validation_exception_handler,
    ValidationError: pydantic_validation_exception_handler,
    Exception: general_exception_handler
}

def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app"""
    for exception_type, handler in EXCEPTION_HANDLERS.items():
        app.add_exception_handler(exception_type, handler)
    
    logger.info("Exception handlers registered successfully")

# Utility functions for raising exceptions
def raise_validation_error(message: str, field: str = None, details: Any = None):
    """Raise a validation error"""
    raise ValidationException(message, field, details)

def raise_authentication_error(message: str = "Authentication failed"):
    """Raise an authentication error"""
    raise AuthenticationException(message)

def raise_authorization_error(message: str = "Access denied"):
    """Raise an authorization error"""
    raise AuthorizationException(message)

def raise_not_found_error(message: str = "Resource not found"):
    """Raise a not found error"""
    raise NotFoundException(message)

def raise_rate_limit_error(message: str = "Rate limit exceeded"):
    """Raise a rate limit error"""
    raise RateLimitException(message)

def raise_database_error(message: str = "Database operation failed"):
    """Raise a database error"""
    raise DatabaseException(message)

def raise_external_service_error(message: str = "External service error", service: str = None):
    """Raise an external service error"""
    raise ExternalServiceException(message, service)

def raise_configuration_error(message: str = "Configuration error"):
    """Raise a configuration error"""
    raise ConfigurationException(message) 