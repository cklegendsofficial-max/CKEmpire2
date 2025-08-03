from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    """Project status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"

class ContentType(str, Enum):
    """Content type enum"""
    BLOG = "blog"
    VIDEO = "video"
    SOCIAL = "social"
    EMAIL = "email"
    ARTICLE = "article"
    PODCAST = "podcast"

class ContentStatus(str, Enum):
    """Content status enum"""
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"

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

class ContentBase(BaseModel):
    """Base content model"""
    project_id: int = Field(..., gt=0, description="Project ID")
    title: str = Field(..., min_length=1, max_length=255, description="Content title")
    content_type: ContentType = Field(..., description="Content type")
    content_data: str = Field(..., min_length=1, description="Content data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    status: ContentStatus = Field(ContentStatus.DRAFT, description="Content status")
    ai_generated: bool = Field(False, description="Whether content was AI generated")

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

class ContentCreate(ContentBase):
    """Create content model"""
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

class ContentUpdate(BaseModel):
    """Update content model"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content_type: Optional[ContentType] = None
    content_data: Optional[str] = Field(None, min_length=1)
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[ContentStatus] = None
    ai_generated: Optional[bool] = None

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

class ContentResponse(ContentBase):
    """Content response model"""
    id: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
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

class ContentList(BaseModel):
    """Content list response"""
    content: List[ContentResponse]
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
    content_id: Optional[int] = Field(None, description="Content ID for tracking")
    user_id: Optional[int] = Field(None, description="User ID")

class EthicsResponse(BaseModel):
    """Ethics check response"""
    bias_score: float = Field(..., ge=0, le=1, description="Bias detection score")
    fairness_score: float = Field(..., ge=0, le=1, description="Fairness score")
    bias_detected: bool = Field(..., description="Whether bias was detected")
    bias_types: List[str] = Field(..., description="Types of bias detected")
    content_status: str = Field(..., description="Content status after analysis")
    recommendations: List[str] = Field(..., description="Recommendations for improvement")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in analysis")
    flagged_keywords: List[str] = Field(..., description="Flagged sensitive keywords")
    sensitive_topics: List[str] = Field(..., description="Sensitive topics identified")
    analysis_timestamp: datetime = Field(..., description="Analysis timestamp")
    is_approved: bool = Field(..., description="Whether content is approved")

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

@validator('title')
def validate_content_title(cls, v):
    """Validate content title"""
    if not v.strip():
        raise ValueError('Content title cannot be empty')
    return v.strip()

@validator('content_data')
def validate_content_data(cls, v):
    """Validate content data"""
    if not v.strip():
        raise ValueError('Content data cannot be empty')
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

# AI Models
class ContentIdeaRequest(BaseModel):
    """Content idea generation request"""
    topic: str = Field(..., min_length=1, description="Topic for content generation")
    count: int = Field(5, ge=1, le=20, description="Number of ideas to generate")
    content_type: Optional[str] = Field(None, description="Specific content type")

class ContentIdeaResponse(BaseModel):
    """Content idea response"""
    title: str = Field(..., description="Content title")
    description: str = Field(..., description="Content description")
    content_type: str = Field(..., description="Content type")
    target_audience: str = Field(..., description="Target audience")
    viral_potential: float = Field(..., ge=0, le=1, description="Viral potential score")
    estimated_revenue: float = Field(..., ge=0, description="Estimated revenue potential")
    keywords: List[str] = Field(..., description="SEO keywords")
    hashtags: List[str] = Field(..., description="Trending hashtags")
    ai_generated: bool = Field(True, description="Whether AI generated")
    created_at: datetime = Field(..., description="Creation timestamp")

class VideoRequest(BaseModel):
    """Video generation request"""
    script: str = Field(..., min_length=10, description="Video script/content")
    style: str = Field("zack_snyder", description="Video style")
    duration: int = Field(60, ge=10, le=3600, description="Video duration in seconds")

class VideoResponse(BaseModel):
    """Video generation response"""
    title: str = Field(..., description="Video title")
    script: str = Field(..., description="Video script")
    style: str = Field(..., description="Applied video style")
    duration: int = Field(..., description="Video duration")
    resolution: str = Field(..., description="Video resolution")
    output_path: str = Field(..., description="Output file path")
    status: str = Field(..., description="Generation status")
    created_at: datetime = Field(..., description="Creation timestamp")

class NFTRequest(BaseModel):
    """NFT creation request"""
    name: str = Field(..., min_length=1, description="NFT name")
    description: str = Field(..., min_length=1, description="NFT description")
    image_path: str = Field(..., description="Path to NFT image")
    price_eth: float = Field(..., ge=0.001, description="Price in ETH")
    collection: str = Field("CK Empire", description="NFT collection")

class NFTResponse(BaseModel):
    """NFT creation response"""
    name: str = Field(..., description="NFT name")
    description: str = Field(..., description="NFT description")
    image_path: str = Field(..., description="Image path")
    price_eth: float = Field(..., description="Price in ETH")
    price_usd: float = Field(..., description="Price in USD")
    collection: str = Field(..., description="NFT collection")
    status: str = Field(..., description="NFT status")
    token_id: Optional[str] = Field(None, description="Blockchain token ID")
    transaction_hash: Optional[str] = Field(None, description="Transaction hash")
    metadata: Dict[str, Any] = Field(..., description="NFT metadata")
    created_at: datetime = Field(..., description="Creation timestamp")

class AGIStateResponse(BaseModel):
    """AGI consciousness state response"""
    consciousness_score: float = Field(..., ge=0, le=1, description="Consciousness level")
    decision_capability: float = Field(..., ge=0, le=1, description="Decision making capability")
    learning_rate: float = Field(..., ge=0, le=1, description="Learning rate")
    creativity_level: float = Field(..., ge=0, le=1, description="Creativity level")
    ethical_awareness: float = Field(..., ge=0, le=1, description="Ethical awareness")
    last_evolution: datetime = Field(..., description="Last evolution timestamp")
    evolution_count: int = Field(..., ge=0, description="Total evolution count")

class DecisionRequest(BaseModel):
    """AGI decision request"""
    context: Dict[str, Any] = Field(..., description="Context for decision making")

class DecisionResponse(BaseModel):
    """AGI decision response"""
    decisions: Dict[str, Any] = Field(..., description="Made decisions")
    agi_state: AGIStateResponse = Field(..., description="Current AGI state")
    timestamp: datetime = Field(..., description="Decision timestamp") 