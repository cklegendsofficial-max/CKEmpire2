from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    """Project status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"

class RiskLevel(str, Enum):
    """Risk level enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Base Models
class ProjectBase(BaseModel):
    """Base project model"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    status: ProjectStatus = Field(ProjectStatus.ACTIVE, description="Project status")
    budget: float = Field(0.0, ge=0, description="Project budget")
    revenue: float = Field(0.0, ge=0, description="Project revenue")

class RevenueBase(BaseModel):
    """Base revenue model"""
    project_id: int = Field(..., gt=0, description="Project ID")
    amount: float = Field(..., gt=0, description="Revenue amount")
    source: str = Field(..., min_length=1, max_length=100, description="Revenue source")
    description: Optional[str] = Field(None, max_length=500, description="Revenue description")

# Create Models
class ProjectCreate(ProjectBase):
    """Create project model"""
    pass

class RevenueCreate(RevenueBase):
    """Create revenue model"""
    pass

# Update Models
class ProjectUpdate(BaseModel):
    """Update project model"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[ProjectStatus] = None
    budget: Optional[float] = Field(None, ge=0)
    revenue: Optional[float] = Field(None, ge=0)

class RevenueUpdate(BaseModel):
    """Update revenue model"""
    amount: Optional[float] = Field(None, gt=0)
    source: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

# Response Models
class ProjectModel(ProjectBase):
    """Project response model"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class RevenueModel(RevenueBase):
    """Revenue response model"""
    id: int
    date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# List Response Models
class ProjectList(BaseModel):
    """Project list response"""
    projects: List[ProjectModel]
    total: int
    page: int
    limit: int

class RevenueList(BaseModel):
    """Revenue list response"""
    revenues: List[RevenueModel]
    total: int
    page: int
    limit: int

# AI Models
class AIRequest(BaseModel):
    """AI request model"""
    prompt: str = Field(..., min_length=1, max_length=2000, description="AI prompt")
    model: Optional[str] = Field("gpt-4", description="AI model to use")
    max_tokens: Optional[int] = Field(2000, gt=0, le=4000, description="Maximum tokens")
    temperature: Optional[float] = Field(0.7, ge=0, le=2, description="AI temperature")

class AIResponse(BaseModel):
    """AI response model"""
    response: str
    model: str
    tokens_used: int
    cost: Optional[float] = None
    timestamp: datetime

# Ethics Models
class EthicsRequest(BaseModel):
    """Ethics check request"""
    content: str = Field(..., min_length=1, description="Content to check")
    action: str = Field(..., description="Action being performed")
    user_id: Optional[int] = None

class EthicsResponse(BaseModel):
    """Ethics check response"""
    bias_score: float = Field(..., ge=0, le=1, description="Bias detection score")
    risk_level: RiskLevel
    recommendations: List[str]
    is_approved: bool
    timestamp: datetime

# Error Models
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SuccessResponse(BaseModel):
    """Success response model"""
    message: str
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Validation
@validator('name')
def validate_project_name(cls, v):
    """Validate project name"""
    if not v.strip():
        raise ValueError('Project name cannot be empty')
    return v.strip()

@validator('amount')
def validate_amount(cls, v):
    """Validate amount"""
    if v <= 0:
        raise ValueError('Amount must be greater than 0')
    return round(v, 2)

# Config
class Config:
    """Pydantic config"""
    json_encoders = {
        datetime: lambda v: v.isoformat()
    }
    schema_extra = {
        "example": {
            "name": "CK Empire Builder",
            "description": "Advanced digital empire management platform",
            "status": "active",
            "budget": 10000.0,
            "revenue": 5000.0
        }
    } 