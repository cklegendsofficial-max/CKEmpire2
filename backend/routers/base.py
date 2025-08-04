"""
Base router with common functionality for all API routers
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from config import settings, constants
from utils import (
    validate_required_fields, 
    validate_field_types, 
    sanitize_dict,
    log_operation,
    check_rate_limit,
    verify_jwt_token
)
from database import get_db, Session

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

class BaseRouter:
    """Base router class with common functionality"""
    
    def __init__(self, prefix: str = "", tags: List[str] = None):
        self.router = APIRouter(prefix=prefix, tags=tags or [])
        self.setup_routes()
    
    def setup_routes(self):
        """Setup router routes - to be implemented by subclasses"""
        pass
    
    async def get_current_user(self, token: str = Depends(security)) -> Optional[Dict[str, Any]]:
        """Get current user from JWT token"""
        try:
            payload = verify_jwt_token(token.credentials)
            if payload is None:
                raise HTTPException(
                    status_code=constants.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return payload
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            raise HTTPException(
                status_code=constants.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def validate_request_data(self, data: Dict[str, Any], required_fields: List[str], field_types: Dict[str, type] = None) -> Dict[str, Any]:
        """Validate request data"""
        # Check required fields
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            raise HTTPException(
                status_code=constants.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Check field types if provided
        if field_types:
            type_errors = validate_field_types(data, field_types)
            if type_errors:
                raise HTTPException(
                    status_code=constants.HTTP_400_BAD_REQUEST,
                    detail=f"Field type errors: {', '.join(type_errors)}"
                )
        
        # Sanitize data
        return sanitize_dict(data)
    
    def check_rate_limit_for_user(self, user_id: int, limit: int = 100, window: int = 60) -> bool:
        """Check rate limit for a specific user"""
        identifier = f"user:{user_id}"
        allowed, info = check_rate_limit(identifier, limit, window)
        
        if not allowed:
            raise HTTPException(
                status_code=constants.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"X-RateLimit-Reset": str(info.get("reset_time", ""))}
            )
        
        return True
    
    def log_api_operation(self, operation: str, user_id: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        """Log API operation"""
        log_operation(
            operation=operation,
            user_id=user_id,
            details=details,
            level="info"
        )
    
    def create_success_response(self, data: Any, message: str = "Success") -> Dict[str, Any]:
        """Create standardized success response"""
        return {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def create_error_response(self, message: str, error_code: str = None, details: Any = None) -> Dict[str, Any]:
        """Create standardized error response"""
        response = {
            "success": False,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if error_code:
            response["error_code"] = error_code
        
        if details:
            response["details"] = details
        
        return response
    
    def paginate_response(self, items: List[Any], total: int, page: int, page_size: int) -> Dict[str, Any]:
        """Create paginated response"""
        return {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size,
                "has_next": page * page_size < total,
                "has_prev": page > 1
            }
        }
    
    def handle_database_error(self, error: Exception, operation: str):
        """Handle database errors"""
        logger.error(f"Database error in {operation}: {error}")
        raise HTTPException(
            status_code=constants.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database operation failed: {operation}"
        )
    
    def handle_validation_error(self, error: Exception, field: str = None):
        """Handle validation errors"""
        logger.error(f"Validation error: {error}")
        detail = f"Validation failed: {error}"
        if field:
            detail = f"Validation failed for field '{field}': {error}"
        
        raise HTTPException(
            status_code=constants.HTTP_400_BAD_REQUEST,
            detail=detail
        )
    
    def get_user_from_token(self, request: Request) -> Optional[Dict[str, Any]]:
        """Get user from request token"""
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            return verify_jwt_token(token)
        except Exception as e:
            logger.warning(f"Failed to get user from token: {e}")
            return None
    
    def require_authentication(self, request: Request):
        """Require authentication for endpoint"""
        user = self.get_user_from_token(request)
        if not user:
            raise HTTPException(
                status_code=constants.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    
    def require_admin(self, request: Request):
        """Require admin privileges"""
        user = self.require_authentication(request)
        # Add admin check logic here
        # For now, just check if user exists
        return user
    
    def get_db_session(self) -> Session:
        """Get database session"""
        return next(get_db())
    
    def validate_file_upload(self, file_size: int, filename: str) -> bool:
        """Validate file upload"""
        # Check file size
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=constants.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Check file type
        if not validate_file_type(filename, settings.ALLOWED_FILE_TYPES):
            raise HTTPException(
                status_code=constants.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
            )
        
        return True

# Common response models
class SuccessResponse:
    """Standard success response model"""
    success: bool = True
    message: str
    data: Any
    timestamp: str

class ErrorResponse:
    """Standard error response model"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None
    timestamp: str

class PaginatedResponse:
    """Standard paginated response model"""
    items: List[Any]
    pagination: Dict[str, Any] 