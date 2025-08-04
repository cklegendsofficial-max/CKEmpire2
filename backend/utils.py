"""
Common utilities for CK Empire Builder
Provides shared functions for database operations, validation, encryption, etc.
"""

import os
import hashlib
import secrets
import string
import re
import json
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from functools import wraps
import asyncio
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from config import settings, constants

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom validation error"""
    pass

class EncryptionError(Exception):
    """Custom encryption error"""
    pass

class DatabaseError(Exception):
    """Custom database error"""
    pass

# Encryption utilities
def generate_encryption_key() -> str:
    """Generate a new encryption key"""
    try:
        return Fernet.generate_key().decode()
    except Exception as e:
        logger.error(f"Failed to generate encryption key: {e}")
        raise EncryptionError("Failed to generate encryption key")

def get_encryption_cipher(key: Optional[str] = None) -> Optional[Fernet]:
    """Get encryption cipher"""
    try:
        encryption_key = key or settings.ENCRYPTION_KEY
        if not encryption_key:
            logger.warning("No encryption key provided")
            return None
        
        # Ensure key is bytes
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
        
        return Fernet(encryption_key)
    except Exception as e:
        logger.error(f"Failed to create encryption cipher: {e}")
        return None

def encrypt_data(data: str, key: Optional[str] = None) -> str:
    """Encrypt string data"""
    try:
        cipher = get_encryption_cipher(key)
        if not cipher:
            return data
        
        if not data:
            return data
        
        encrypted_data = cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise EncryptionError(f"Encryption failed: {e}")

def decrypt_data(encrypted_data: str, key: Optional[str] = None) -> str:
    """Decrypt string data"""
    try:
        cipher = get_encryption_cipher(key)
        if not cipher:
            return encrypted_data
        
        if not encrypted_data:
            return encrypted_data
        
        # Decode from base64
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = cipher.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise EncryptionError(f"Decryption failed: {e}")

# Password utilities
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    try:
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except ImportError:
        # Fallback to hashlib if bcrypt not available
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode('utf-8'))
        return f"{salt}${hash_obj.hexdigest()}"
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        raise ValidationError("Password hashing failed")

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ImportError:
        # Fallback to hashlib if bcrypt not available
        try:
            salt, hash_value = hashed_password.split('$')
            hash_obj = hashlib.sha256()
            hash_obj.update((password + salt).encode('utf-8'))
            return hash_obj.hexdigest() == hash_value
        except Exception:
            return False
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False

def generate_secure_password(length: int = 12) -> str:
    """Generate a secure random password"""
    if length < 8:
        length = 8
    
    # Ensure at least one of each character type
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Generate password with at least one of each type
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(symbols)
    ]
    
    # Fill the rest with random characters
    all_chars = lowercase + uppercase + digits + symbols
    password.extend(secrets.choice(all_chars) for _ in range(length - 4))
    
    # Shuffle the password
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)
    return ''.join(password_list)

def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    errors = []
    warnings = []
    
    if len(password) < constants.PASSWORD_MIN_LENGTH:
        errors.append(f"Password must be at least {constants.PASSWORD_MIN_LENGTH} characters long")
    
    if len(password) > constants.PASSWORD_MAX_LENGTH:
        errors.append(f"Password must be no more than {constants.PASSWORD_MAX_LENGTH} characters long")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        warnings.append("Password should contain at least one special character")
    
    if re.search(r'(.)\1{2,}', password):
        warnings.append("Password should not contain repeated characters")
    
    # Check for common patterns
    common_patterns = [
        'password', '123456', 'qwerty', 'admin', 'user',
        'letmein', 'welcome', 'monkey', 'dragon', 'master'
    ]
    
    if password.lower() in common_patterns:
        errors.append("Password should not be a common password")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "score": max(0, 10 - len(errors) - len(warnings))
    }

# Validation utilities
def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_username(username: str) -> bool:
    """Validate username format"""
    # Username should be 3-30 characters, alphanumeric and underscores only
    pattern = r'^[a-zA-Z0-9_]{3,30}$'
    return bool(re.match(pattern, username))

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()

def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """Validate file type"""
    if not filename:
        return False
    
    file_extension = filename.lower().split('.')[-1]
    return file_extension in allowed_types

def validate_file_upload(file_size: int, filename: str, max_size: int = None, allowed_types: List[str] = None) -> bool:
    """Validate file upload"""
    if max_size is None:
        max_size = settings.MAX_FILE_SIZE
    
    if allowed_types is None:
        allowed_types = settings.ALLOWED_FILE_TYPES
    
    # Check file size
    if file_size > max_size:
        return False
    
    # Check file type
    return validate_file_type(filename, allowed_types)

def validate_file_size(file_size: int, max_size: int) -> bool:
    """Validate file size"""
    return file_size <= max_size

# Database utilities
def create_audit_log(
    db_session,
    table_name: str,
    record_id: int,
    operation: str,
    old_values: Optional[Dict] = None,
    new_values: Optional[Dict] = None,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None
) -> None:
    """Create an audit log entry"""
    try:
        from database import AuditLog
        
        audit_entry = AuditLog(
            table_name=table_name,
            record_id=record_id,
            operation=operation,
            old_values=old_values,
            new_values=new_values,
            user_id=user_id,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        
        db_session.add(audit_entry)
        db_session.commit()
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
        db_session.rollback()

def paginate_results(
    query,
    page: int = 1,
    page_size: int = constants.DEFAULT_PAGE_SIZE
) -> Dict[str, Any]:
    """Paginate database query results"""
    if page < 1:
        page = 1
    
    if page_size > constants.MAX_PAGE_SIZE:
        page_size = constants.MAX_PAGE_SIZE
    
    total = query.count()
    offset = (page - 1) * page_size
    
    results = query.offset(offset).limit(page_size).all()
    
    return {
        "items": results,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "has_next": page * page_size < total,
        "has_prev": page > 1
    }

# Cache utilities
def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a cache key"""
    key_parts = [prefix]
    
    # Add args
    for arg in args:
        key_parts.append(str(arg))
    
    # Add kwargs
    for key, value in sorted(kwargs.items()):
        key_parts.append(f"{key}:{value}")
    
    return f"{constants.CACHE_KEY_PREFIX}{':'.join(key_parts)}"

def cache_result(ttl: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = get_cache_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            try:
                from database import get_redis_client
                redis_client = get_redis_client()
                if redis_client:
                    cached_result = redis_client.get(cache_key)
                    if cached_result:
                        return json.loads(cached_result)
            except Exception as e:
                logger.warning(f"Cache retrieval failed: {e}")
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            try:
                if redis_client:
                    redis_client.setex(cache_key, ttl, json.dumps(result))
            except Exception as e:
                logger.warning(f"Cache storage failed: {e}")
            
            return result
        return wrapper
    return decorator

# Rate limiting utilities
def check_rate_limit(
    identifier: str,
    limit: int,
    window: int = 60
) -> Tuple[bool, Dict[str, Any]]:
    """Check rate limit for an identifier"""
    try:
        from database import get_redis_client
        redis_client = get_redis_client()
        
        if not redis_client:
            return True, {"remaining": limit, "reset_time": None}
        
        key = f"rate_limit:{identifier}"
        current = redis_client.get(key)
        
        if current is None:
            redis_client.setex(key, window, 1)
            return True, {"remaining": limit - 1, "reset_time": datetime.utcnow() + timedelta(seconds=window)}
        
        current_count = int(current)
        if current_count >= limit:
            return False, {"remaining": 0, "reset_time": None}
        
        redis_client.incr(key)
        return True, {"remaining": limit - current_count - 1, "reset_time": None}
    
    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        return True, {"remaining": limit, "reset_time": None}

# Error handling utilities
def handle_database_error(func):
    """Decorator to handle database errors"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
    return wrapper

def handle_validation_error(func):
    """Decorator to handle validation errors"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise ValidationError(f"Validation failed: {e}")
    return wrapper

# Security utilities
def generate_jwt_token(
    user_id: int,
    username: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generate JWT token"""
    try:
        import jwt
        from datetime import datetime, timedelta
        
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": str(user_id),
            "username": username,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"JWT token generation failed: {e}")
        raise ValidationError("Token generation failed")

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token"""
    try:
        import jwt
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.JWTError as e:
        logger.warning(f"JWT token verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"JWT token verification error: {e}")
        return None

def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

# File utilities
def ensure_directory_exists(directory: str) -> None:
    """Ensure directory exists, create if it doesn't"""
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        raise ValidationError(f"Failed to create directory: {e}")

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return filename.lower().split('.')[-1] if '.' in filename else ''

def generate_unique_filename(original_filename: str, directory: str = "") -> str:
    """Generate a unique filename"""
    import uuid
    
    name, ext = os.path.splitext(original_filename)
    unique_id = str(uuid.uuid4())[:8]
    new_filename = f"{name}_{unique_id}{ext}"
    
    if directory:
        return os.path.join(directory, new_filename)
    return new_filename

# Date/Time utilities
def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    return dt.strftime(format_str)

def parse_datetime(date_string: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse datetime from string"""
    try:
        return datetime.strptime(date_string, format_str)
    except ValueError:
        return None

def get_time_difference(start_time: datetime, end_time: datetime = None) -> timedelta:
    """Get time difference between two datetimes"""
    if end_time is None:
        end_time = datetime.utcnow()
    return end_time - start_time

# Logging utilities
def log_operation(
    operation: str,
    user_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    level: str = "info"
) -> None:
    """Log an operation"""
    log_data = {
        "operation": operation,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details or {}
    }
    
    if level.lower() == "error":
        logger.error(json.dumps(log_data))
    elif level.lower() == "warning":
        logger.warning(json.dumps(log_data))
    else:
        logger.info(json.dumps(log_data))

# Performance utilities
def measure_execution_time(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        try:
            result = await func(*args, **kwargs)
            execution_time = get_time_difference(start_time)
            logger.info(f"Function {func.__name__} executed in {execution_time.total_seconds():.3f} seconds")
            return result
        except Exception as e:
            execution_time = get_time_difference(start_time)
            logger.error(f"Function {func.__name__} failed after {execution_time.total_seconds():.3f} seconds: {e}")
            raise
    return wrapper

# Async utilities
def run_async_safely(coro):
    """Run coroutine safely with error handling"""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)
    except RuntimeError:
        # Create new event loop if none exists
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

# Data validation utilities
def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate that required fields are present"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    return missing_fields

def validate_field_types(data: Dict[str, Any], field_types: Dict[str, type]) -> List[str]:
    """Validate field types"""
    type_errors = []
    for field, expected_type in field_types.items():
        if field in data and not isinstance(data[field], expected_type):
            type_errors.append(f"Field '{field}' must be of type {expected_type.__name__}")
    return type_errors

def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize dictionary values"""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_input(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_input(str(item)) if isinstance(item, str) else item for item in value]
        else:
            sanitized[key] = value
    return sanitized 