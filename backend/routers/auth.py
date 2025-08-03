"""
Authentication router with JWT + OAuth2 implementation
OWASP compliant security features
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import httpx
import structlog
import re
import hashlib
import time
from rate_limiter import get_enhanced_rate_limiter

from database import get_db
from models import UserCreate, UserResponse, TokenResponse, OAuth2TokenResponse
from database import User
from settings import settings

logger = structlog.get_logger()

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password hashing with enhanced security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# JWT settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Security settings
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 15  # minutes
PASSWORD_MIN_LENGTH = 12
PASSWORD_REQUIREMENTS = {
    'uppercase': True,
    'lowercase': True,
    'digits': True,
    'special': True
}

class LoginRequest(BaseModel):
    """Login request model with enhanced validation"""
    username: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v

class RegisterRequest(BaseModel):
    """Register request model with enhanced validation"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < PASSWORD_MIN_LENGTH:
            raise ValueError(f'Password must be at least {PASSWORD_MIN_LENGTH} characters')
        
        if PASSWORD_REQUIREMENTS['uppercase'] and not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if PASSWORD_REQUIREMENTS['lowercase'] and not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if PASSWORD_REQUIREMENTS['digits'] and not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if PASSWORD_REQUIREMENTS['special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        # Check for common weak passwords
        weak_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common')
        
        return v

class OAuth2Request(BaseModel):
    """OAuth2 authorization request"""
    provider: str  # "google", "github", "microsoft"
    code: str
    redirect_uri: str

class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr

class PasswordChangeRequest(BaseModel):
    """Password change request with validation"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < PASSWORD_MIN_LENGTH:
            raise ValueError(f'Password must be at least {PASSWORD_MIN_LENGTH} characters')
        
        if PASSWORD_REQUIREMENTS['uppercase'] and not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if PASSWORD_REQUIREMENTS['lowercase'] and not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if PASSWORD_REQUIREMENTS['digits'] and not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if PASSWORD_REQUIREMENTS['special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token with enhanced security"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add additional security claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "ckempire",
        "aud": "ckempire-users",
        "jti": hashlib.sha256(f"{data.get('sub')}{time.time()}".encode()).hexdigest()
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token with enhanced security"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # 7 days
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "iss": "ckempire",
        "aud": "ckempire-users",
        "jti": hashlib.sha256(f"refresh_{data.get('sub')}{time.time()}".encode()).hexdigest()
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password with enhanced security"""
    return pwd_context.hash(password)

def check_account_lockout(db: Session, username: str) -> bool:
    """Check if account is locked due to failed login attempts"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    
    if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
        if user.last_failed_login:
            lockout_until = user.last_failed_login + timedelta(minutes=LOCKOUT_DURATION)
            if datetime.utcnow() < lockout_until:
                return True
    
    return False

def reset_failed_attempts(db: Session, username: str):
    """Reset failed login attempts"""
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.failed_login_attempts = 0
        user.last_failed_login = None
        db.commit()

def increment_failed_attempts(db: Session, username: str):
    """Increment failed login attempts"""
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.failed_login_attempts += 1
        user.last_failed_login = datetime.utcnow()
        db.commit()

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user with enhanced security"""
    # Check for account lockout
    if check_account_lockout(db, username):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked due to multiple failed login attempts. Try again in {LOCKOUT_DURATION} minutes."
        )
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        increment_failed_attempts(db, username)
        return None
    
    # Reset failed attempts on successful login
    reset_failed_attempts(db, username)
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from JWT token with enhanced validation"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Validate token issuer and audience
        if payload.get("iss") != "ckempire" or payload.get("aud") != "ckempire-users":
            raise credentials_exception
        
        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise credentials_exception
            
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register new user with enhanced security"""
    try:
        # Rate limiting for registration
        rate_limiter = get_enhanced_rate_limiter()
        rate_check = rate_limiter.check_rate_limit(Request, "auth")
        if not rate_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many registration attempts"
            )
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == request.username) | (User.email == request.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Create new user with enhanced security
        hashed_password = get_password_hash(request.password)
        user = User(
            username=request.username,
            email=request.email,
            hashed_password=hashed_password,
            full_name=request.full_name,
            is_active=True,
            failed_login_attempts=0,
            created_at=datetime.utcnow()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info("User registered successfully", username=user.username, email=user.email)
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT tokens with enhanced security"""
    try:
        # Rate limiting for login attempts
        rate_limiter = get_enhanced_rate_limiter()
        rate_check = rate_limiter.check_rate_limit(Request, "auth")
        if not rate_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts"
            )
        
        user = authenticate_user(db, request.username, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Create tokens with enhanced security
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": user.username})
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        logger.info("User logged in successfully", username=user.username)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = db.query(User).filter(User.username == username).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user"
            )
        
        # Create new tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(data={"sub": user.username})
        
        logger.info("Token refreshed successfully", username=user.username)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/oauth2/{provider}", response_model=OAuth2TokenResponse)
async def oauth2_login(provider: str, request: OAuth2Request, db: Session = Depends(get_db)):
    """OAuth2 login with external provider"""
    try:
        # OAuth2 provider configurations
        oauth_configs = {
            "google": {
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
            },
            "github": {
                "token_url": "https://github.com/login/oauth/access_token",
                "userinfo_url": "https://api.github.com/user",
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
            },
            "microsoft": {
                "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                "userinfo_url": "https://graph.microsoft.com/v1.0/me",
                "client_id": settings.MICROSOFT_CLIENT_ID,
                "client_secret": settings.MICROSOFT_CLIENT_SECRET,
            }
        }
        
        if provider not in oauth_configs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth2 provider: {provider}"
            )
        
        config = oauth_configs[provider]
        
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                config["token_url"],
                data={
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                    "code": request.code,
                    "redirect_uri": request.redirect_uri,
                    "grant_type": "authorization_code"
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange OAuth2 code"
                )
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No access token received"
                )
            
            # Get user info
            headers = {"Authorization": f"Bearer {access_token}"}
            userinfo_response = await client.get(
                config["userinfo_url"],
                headers=headers
            )
            
            if userinfo_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info"
                )
            
            userinfo = userinfo_response.json()
            
            # Extract user info based on provider
            if provider == "google":
                email = userinfo.get("email")
                username = userinfo.get("email", "").split("@")[0]
                full_name = userinfo.get("name")
            elif provider == "github":
                email = userinfo.get("email")
                username = userinfo.get("login")
                full_name = userinfo.get("name")
            elif provider == "microsoft":
                email = userinfo.get("mail") or userinfo.get("userPrincipalName")
                username = userinfo.get("userPrincipalName", "").split("@")[0]
                full_name = userinfo.get("displayName")
            
            # Check if user exists
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                # Create new user
                user = User(
                    username=username,
                    email=email,
                    full_name=full_name,
                    is_active=True,
                    oauth_provider=provider,
                    oauth_id=userinfo.get("id")
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                logger.info("OAuth2 user created", provider=provider, email=email)
            else:
                # Update OAuth info
                user.oauth_provider = provider
                user.oauth_id = userinfo.get("id")
                user.last_login = datetime.utcnow()
                db.commit()
                logger.info("OAuth2 user logged in", provider=provider, email=email)
            
            # Create JWT tokens
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            jwt_access_token = create_access_token(
                data={"sub": user.username}, expires_delta=access_token_expires
            )
            refresh_token = create_refresh_token(data={"sub": user.username})
            
            return OAuth2TokenResponse(
                access_token=jwt_access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                provider=provider,
                user=UserResponse(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    is_active=user.is_active,
                    created_at=user.created_at
                )
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("OAuth2 login failed", provider=provider, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth2 login failed"
        )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout user (client should discard tokens)"""
    logger.info("User logged out", username=current_user.username)
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

@router.post("/password-reset")
async def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset (send email)"""
    try:
        user = db.query(User).filter(User.email == request.email).first()
        if user:
            # In production, send email with reset link
            # For now, just log the request
            logger.info("Password reset requested", email=request.email)
        
        # Always return success to prevent email enumeration
        return {"message": "If the email exists, a password reset link has been sent"}
        
    except Exception as e:
        logger.error("Password reset request failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )

@router.post("/password-change")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        # Verify current password
        if not verify_password(request.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        
        # Update password
        current_user.hashed_password = get_password_hash(request.new_password)
        db.commit()
        
        logger.info("Password changed successfully", username=current_user.username)
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Password change failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.get("/providers")
async def get_oauth_providers():
    """Get available OAuth2 providers"""
    providers = []
    
    if hasattr(settings, 'GOOGLE_CLIENT_ID') and settings.GOOGLE_CLIENT_ID:
        providers.append({
            "name": "google",
            "display_name": "Google",
            "auth_url": "https://accounts.google.com/oauth2/authorize",
            "client_id": settings.GOOGLE_CLIENT_ID
        })
    
    if hasattr(settings, 'GITHUB_CLIENT_ID') and settings.GITHUB_CLIENT_ID:
        providers.append({
            "name": "github",
            "display_name": "GitHub",
            "auth_url": "https://github.com/login/oauth/authorize",
            "client_id": settings.GITHUB_CLIENT_ID
        })
    
    if hasattr(settings, 'MICROSOFT_CLIENT_ID') and settings.MICROSOFT_CLIENT_ID:
        providers.append({
            "name": "microsoft",
            "display_name": "Microsoft",
            "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "client_id": settings.MICROSOFT_CLIENT_ID
        })
    
    return {"providers": providers} 