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

class StrategyType(str, Enum):
    """Empire strategy type enum"""
    LEAN_STARTUP = "lean_startup"
    SCALE_UP = "scale_up"
    DIVERSIFICATION = "diversification"
    ACQUISITION = "acquisition"
    INNOVATION = "innovation"
    COST_OPTIMIZATION = "cost_optimization"

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

# Response Models
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

# Validators
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
    if v < 0:
        raise ValueError('Amount cannot be negative')
    return v

class Config:
    """Pydantic config"""
    json_encoders = {
        datetime: lambda v: v.isoformat()
    }
    schema_extra = {
        "example": {
            "name": "Sample Project",
            "description": "A sample project description",
            "status": "active",
            "budget": 10000.0,
            "revenue": 5000.0
        }
    }

# AI Content Generation Models
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

# Empire Strategy Models
class EmpireStrategyRequest(BaseModel):
    """Empire strategy generation request"""
    user_input: str = Field(..., min_length=1, description="User's strategy requirements")
    include_financial_metrics: bool = Field(True, description="Whether to include DCF calculations")

class FinancialMetricsResponse(BaseModel):
    """Financial metrics response"""
    npv: float = Field(..., description="Net Present Value")
    irr: float = Field(..., description="Internal Rate of Return")
    payback_period: float = Field(..., description="Payback period in months")
    roi_percentage: float = Field(..., description="ROI percentage")
    monthly_cash_flow: float = Field(..., description="Monthly cash flow")
    break_even_month: int = Field(..., description="Break-even month")
    total_investment: float = Field(..., description="Total investment required")
    projected_revenue: float = Field(..., description="Projected total revenue")

class EmpireStrategyResponse(BaseModel):
    """Empire strategy response"""
    strategy_type: str = Field(..., description="Strategy type")
    title: str = Field(..., description="Strategy title")
    description: str = Field(..., description="Strategy description")
    key_actions: List[str] = Field(..., description="Key actions to take")
    timeline_months: int = Field(..., description="Timeline in months")
    estimated_investment: float = Field(..., description="Estimated investment required")
    projected_roi: float = Field(..., description="Projected ROI")
    risk_level: str = Field(..., description="Risk level")
    success_metrics: List[str] = Field(..., description="Success metrics")
    created_at: datetime = Field(..., description="Creation timestamp")
    financial_metrics: Optional[FinancialMetricsResponse] = Field(None, description="Financial analysis")

# Fine-tuning Models
class FineTuningRequest(BaseModel):
    """Fine-tuning request"""
    model_name: str = Field("gpt-4", description="Base model to fine-tune")
    epochs: int = Field(3, ge=1, le=10, description="Number of training epochs")

class FineTuningResponse(BaseModel):
    """Fine-tuning response"""
    training_examples: int = Field(..., description="Number of training examples")
    validation_examples: int = Field(..., description="Number of validation examples")
    model_name: str = Field(..., description="Model name")
    training_status: str = Field(..., description="Training status")
    created_at: datetime = Field(..., description="Creation timestamp")

class FineTuningStatusResponse(BaseModel):
    """Fine-tuning status response"""
    job_id: str = Field(..., description="Fine-tuning job ID")
    status: str = Field(..., description="Job status")
    model_name: str = Field(..., description="Model name")
    epochs: int = Field(..., description="Number of epochs")
    created_at: datetime = Field(..., description="Creation timestamp")
    finished_at: Optional[datetime] = Field(None, description="Completion timestamp")
    trained_tokens: int = Field(0, description="Number of tokens trained")

# Subscription Models
class SubscriptionTier(str, Enum):
    """Subscription tier enum"""
    FREEMIUM = "freemium"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class BillingCycle(str, Enum):
    """Billing cycle enum"""
    MONTHLY = "monthly"
    YEARLY = "yearly"

class SubscriptionStatus(str, Enum):
    """Subscription status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"

class SubscriptionRequest(BaseModel):
    """Subscription creation request"""
    tier: SubscriptionTier = Field(..., description="Subscription tier")
    billing_cycle: BillingCycle = Field(..., description="Billing cycle")
    payment_method_id: str = Field(..., description="Stripe payment method ID")

class SubscriptionResponse(BaseModel):
    """Subscription response"""
    subscription_id: str = Field(..., description="Stripe subscription ID")
    tier: str = Field(..., description="Subscription tier")
    status: str = Field(..., description="Subscription status")
    billing_cycle: str = Field(..., description="Billing cycle")
    price: float = Field(..., description="Subscription price")
    features: List[str] = Field(..., description="Available features")
    limits: Dict[str, int] = Field(..., description="Usage limits")
    current_period_start: Optional[str] = Field(None, description="Current period start")
    current_period_end: Optional[str] = Field(None, description="Current period end")
    cancel_at_period_end: bool = Field(False, description="Whether subscription will cancel at period end")

class SubscriptionCancelResponse(BaseModel):
    """Subscription cancellation response"""
    subscription_id: str = Field(..., description="Stripe subscription ID")
    status: str = Field(..., description="Subscription status")
    cancel_at_period_end: bool = Field(..., description="Whether subscription will cancel at period end")
    current_period_end: str = Field(..., description="Current period end date")

class PricingPlanResponse(BaseModel):
    """Pricing plan response"""
    tier: str = Field(..., description="Plan tier")
    name: str = Field(..., description="Plan name")
    price_monthly: float = Field(..., description="Monthly price")
    price_yearly: float = Field(..., description="Yearly price")
    features: List[str] = Field(..., description="Plan features")
    limits: Dict[str, int] = Field(..., description="Usage limits")
    stripe_price_id_monthly: str = Field(..., description="Stripe monthly price ID")
    stripe_price_id_yearly: str = Field(..., description="Stripe yearly price ID")

class FinancialMetricsResponse(BaseModel):
    """Financial metrics response"""
    monthly_recurring_revenue: float = Field(..., description="Monthly Recurring Revenue")
    annual_recurring_revenue: float = Field(..., description="Annual Recurring Revenue")
    customer_acquisition_cost: float = Field(..., description="Customer Acquisition Cost")
    lifetime_value: float = Field(..., description="Customer Lifetime Value")
    churn_rate: float = Field(..., description="Churn rate percentage")
    revenue_growth_rate: float = Field(..., description="Revenue growth rate percentage")
    roi_percentage: float = Field(..., description="Return on Investment percentage")
    break_even_months: int = Field(..., description="Break-even months")
    total_customers: int = Field(..., description="Total active customers")
    total_revenue: float = Field(..., description="Total revenue")
    average_revenue_per_user: float = Field(..., description="Average Revenue Per User")
    calculated_at: datetime = Field(..., description="Calculation timestamp")

class UserLimitsResponse(BaseModel):
    """User limits response"""
    user_id: int = Field(..., description="User ID")
    tier: str = Field(..., description="Current subscription tier")
    features: List[str] = Field(..., description="Available features")
    limits: Dict[str, int] = Field(..., description="Usage limits")
    usage: Dict[str, int] = Field(..., description="Current usage")
    has_access: bool = Field(..., description="Whether user has access to features")

# Ethics Models
class BiasType(str, Enum):
    """Bias types enum"""
    GENDER = "gender"
    RACE = "race"
    AGE = "age"
    INCOME = "income"
    EDUCATION = "education"
    LOCATION = "location"

class CorrectionMethod(str, Enum):
    """Bias correction methods"""
    REWEIGHING = "reweighing"
    ADVERSARIAL_DEBIASING = "adversarial_debiasing"
    PREJUDICE_REMOVER = "prejudice_remover"

class BiasMetricsResponse(BaseModel):
    """Bias metrics response"""
    statistical_parity_difference: float = Field(..., description="Statistical parity difference")
    equal_opportunity_difference: float = Field(..., description="Equal opportunity difference")
    average_odds_difference: float = Field(..., description="Average odds difference")
    theil_index: float = Field(..., description="Theil index")
    overall_bias_score: float = Field(..., description="Overall bias score")
    bias_type: str = Field(..., description="Type of bias detected")
    protected_attribute: str = Field(..., description="Protected attribute")
    privileged_group: str = Field(..., description="Privileged group value")
    unprivileged_group: str = Field(..., description="Unprivileged group value")

class BiasDetectionRequest(BaseModel):
    """Bias detection request"""
    data: List[Dict[str, Any]] = Field(..., description="Dataset to analyze")
    protected_attributes: List[str] = Field(..., description="Protected attribute columns")
    target_column: str = Field(..., description="Target variable column")
    privileged_groups: List[Dict[str, Any]] = Field(..., description="Privileged group definitions")

class BiasDetectionResponse(BaseModel):
    """Bias detection response"""
    bias_detected: bool = Field(..., description="Whether bias was detected")
    bias_metrics: List[BiasMetricsResponse] = Field(..., description="Bias metrics for each protected attribute")
    total_metrics: int = Field(..., description="Total number of metrics calculated")
    detection_timestamp: Optional[datetime] = Field(None, description="Detection timestamp")

class BiasCorrectionRequest(BaseModel):
    """Bias correction request"""
    data: List[Dict[str, Any]] = Field(..., description="Dataset to correct")
    protected_attributes: List[str] = Field(..., description="Protected attribute columns")
    target_column: str = Field(..., description="Target variable column")
    privileged_groups: List[Dict[str, Any]] = Field(..., description="Privileged group definitions")
    correction_method: CorrectionMethod = Field(..., description="Correction method to use")

class BiasCorrectionResponse(BaseModel):
    """Bias correction response"""
    correction_successful: bool = Field(..., description="Whether correction was successful")
    method: str = Field(..., description="Correction method used")
    original_bias: float = Field(..., description="Original bias score")
    corrected_bias: float = Field(..., description="Corrected bias score")
    bias_reduction: float = Field(..., description="Bias reduction percentage")
    protected_attribute: str = Field(..., description="Protected attribute corrected")
    weights_applied: bool = Field(..., description="Whether weights were applied")
    corrected_data: List[Dict[str, Any]] = Field(..., description="Corrected dataset")
    correction_info: Dict[str, Any] = Field(..., description="Additional correction information")

class EthicalReportResponse(BaseModel):
    """Ethical report response"""
    bias_metrics: List[BiasMetricsResponse] = Field(..., description="Bias metrics")
    overall_ethical_score: float = Field(..., description="Overall ethical score (0-1)")
    bias_detected: bool = Field(..., description="Whether bias was detected")
    correction_applied: bool = Field(..., description="Whether correction was applied")
    correction_method: Optional[str] = Field(None, description="Correction method used")
    recommendations: List[str] = Field(..., description="Ethical recommendations")
    compliance_status: str = Field(..., description="Compliance status")
    risk_level: str = Field(..., description="Risk level")
    generated_at: datetime = Field(..., description="Report generation timestamp")
    should_stop_evolution: bool = Field(..., description="Whether AI evolution should be stopped")

class EthicsDashboardResponse(BaseModel):
    """Ethics dashboard response"""
    overall_ethical_score: float = Field(..., description="Overall ethical score")
    bias_detection_rate: float = Field(..., description="Bias detection rate")
    correction_success_rate: float = Field(..., description="Correction success rate")
    avg_bias_reduction: float = Field(..., description="Average bias reduction")
    compliance_rate: float = Field(..., description="Compliance rate")
    risk_level_distribution: Dict[str, int] = Field(..., description="Risk level distribution")
    bias_types_detected: Dict[str, int] = Field(..., description="Bias types detected")
    correction_methods_used: Dict[str, int] = Field(..., description="Correction methods used")
    total_corrections: int = Field(..., description="Total corrections applied")
    total_reports: int = Field(..., description="Total reports generated")
    last_updated: datetime = Field(..., description="Last update timestamp")

# Video/NFT Models
class VideoProductionRequest(BaseModel):
    """Video production request"""
    theme: str = Field(..., min_length=1, description="Video theme/concept")
    duration: int = Field(60, ge=10, le=3600, description="Video duration in seconds")
    style: str = Field("zack_snyder", description="Video style (zack_snyder, action, dramatic)")

class VideoProductionResponse(BaseModel):
    """Video production response"""
    production_id: str = Field(..., description="Production ID")
    video_prompt: str = Field(..., description="Generated video prompt")
    video_metadata: Dict[str, Any] = Field(..., description="Video metadata")
    nft_metadata: Dict[str, Any] = Field(..., description="NFT metadata")
    pricing_prediction: Dict[str, Any] = Field(..., description="Pricing prediction")
    stripe_product: Dict[str, Any] = Field(..., description="Stripe product info")
    status: str = Field(..., description="Production status")
    created_at: str = Field(..., description="Creation timestamp")

class NFTGenerationRequest(BaseModel):
    """NFT generation request"""
    video_metadata: Dict[str, Any] = Field(..., description="Video metadata")
    collection_name: str = Field("CKEmpire Videos", description="NFT collection name")

class NFTGenerationResponse(BaseModel):
    """NFT generation response"""
    nft_metadata: Dict[str, Any] = Field(..., description="NFT metadata")
    pricing_prediction: Dict[str, Any] = Field(..., description="Pricing prediction")
    stripe_product: Dict[str, Any] = Field(..., description="Stripe product info")
    status: str = Field(..., description="Generation status")
    created_at: str = Field(..., description="Creation timestamp")

class PricingPredictionRequest(BaseModel):
    """Pricing prediction request"""
    nft_metadata: Dict[str, Any] = Field(..., description="NFT metadata")
    market_data: Optional[Dict[str, Any]] = Field(None, description="Market data")

class PricingPredictionResponse(BaseModel):
    """Pricing prediction response"""
    predicted_price: float = Field(..., description="Predicted price in ETH")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")
    factors: List[str] = Field(..., description="Pricing factors")
    market_analysis: Dict[str, Any] = Field(..., description="Market analysis")
    recommendation: str = Field(..., description="Pricing recommendation")
    status: str = Field(..., description="Prediction status")

class VideoStyleResponse(BaseModel):
    """Video styles response"""
    styles: Dict[str, Dict[str, Any]] = Field(..., description="Available video styles")
    total_styles: int = Field(..., description="Total number of styles")

class NFTMetadataResponse(BaseModel):
    """NFT metadata response"""
    production_id: str = Field(..., description="Production ID")
    metadata: Dict[str, Any] = Field(..., description="NFT metadata")
    status: str = Field(..., description="Metadata status")

# Finance Models
class ROICalculationRequest(BaseModel):
    """ROI calculation request"""
    target_amount: float = Field(..., gt=0, description="Target amount to achieve")
    initial_investment: Optional[float] = Field(None, gt=0, description="Initial investment amount")
    time_period: float = Field(1.0, gt=0, description="Time period in years")

class ROICalculationResponse(BaseModel):
    """ROI calculation response"""
    roi_percentage: float = Field(..., description="ROI percentage")
    annualized_roi: float = Field(..., description="Annualized ROI percentage")
    payback_period: float = Field(..., description="Payback period in years")
    initial_investment: float = Field(..., description="Initial investment amount")
    total_return: float = Field(..., description="Total return amount")
    time_period: float = Field(..., description="Time period in years")
    target_amount: float = Field(..., description="Target amount")
    status: str = Field(..., description="Calculation status")

class DCFModelRequest(BaseModel):
    """DCF model request"""
    initial_investment: float = Field(..., gt=0, description="Initial investment amount")
    target_revenue: float = Field(..., gt=0, description="Target revenue amount")
    growth_rate: Optional[float] = Field(None, ge=0, le=1, description="Annual growth rate")
    discount_rate: Optional[float] = Field(None, ge=0, le=1, description="Discount rate")
    time_period: Optional[int] = Field(None, gt=0, description="Time period in years")

class DCFModelResponse(BaseModel):
    """DCF model response"""
    npv: float = Field(..., description="Net Present Value")
    irr: float = Field(..., description="Internal Rate of Return")
    present_value: float = Field(..., description="Present Value of cash flows")
    projected_revenue: List[float] = Field(..., description="Projected revenue by year")
    initial_investment: float = Field(..., description="Initial investment amount")
    growth_rate: float = Field(..., description="Growth rate used")
    discount_rate: float = Field(..., description="Discount rate used")
    time_period: int = Field(..., description="Time period in years")
    status: str = Field(..., description="Model status")

class ABTestRequest(BaseModel):
    """A/B test request"""
    variant_a_data: Dict[str, Any] = Field(..., description="Variant A test data")
    variant_b_data: Dict[str, Any] = Field(..., description="Variant B test data")
    metric: str = Field("conversion_rate", description="Metric to test")

class ABTestResponse(BaseModel):
    """A/B test response"""
    variant_a: Dict[str, Any] = Field(..., description="Variant A results")
    variant_b: Dict[str, Any] = Field(..., description="Variant B results")
    confidence_level: float = Field(..., description="Statistical confidence level")
    winner: str = Field(..., description="Winning variant")
    p_value: float = Field(..., description="P-value")
    sample_size: int = Field(..., description="Total sample size")
    metric: str = Field(..., description="Tested metric")
    status: str = Field(..., description="Test status")

class FinancialReportRequest(BaseModel):
    """Financial report request"""
    target_amount: float = Field(20000, gt=0, description="Target amount")
    initial_investment: Optional[float] = Field(None, gt=0, description="Initial investment")

class FinancialReportResponse(BaseModel):
    """Financial report response"""
    target_amount: float = Field(..., description="Target amount")
    roi_analysis: Dict[str, Any] = Field(..., description="ROI analysis")
    dcf_analysis: Dict[str, Any] = Field(..., description="DCF analysis")
    break_even_analysis: Dict[str, Any] = Field(..., description="Break-even analysis")
    cash_flow_forecast: List[Dict[str, Any]] = Field(..., description="Cash flow forecast")
    financial_ratios: Dict[str, float] = Field(..., description="Financial ratios")
    recommendations: List[str] = Field(..., description="Financial recommendations")
    timestamp: str = Field(..., description="Report timestamp")
    status: str = Field(..., description="Report status")

class BreakEvenRequest(BaseModel):
    """Break-even calculation request"""
    fixed_costs: float = Field(..., gt=0, description="Fixed costs")
    variable_cost_per_unit: float = Field(..., ge=0, description="Variable cost per unit")
    price_per_unit: float = Field(..., gt=0, description="Price per unit")

class BreakEvenResponse(BaseModel):
    """Break-even calculation response"""
    break_even_units: float = Field(..., description="Break-even units")
    break_even_revenue: float = Field(..., description="Break-even revenue")
    contribution_margin: float = Field(..., description="Contribution margin")
    is_profitable: bool = Field(..., description="Whether business is profitable")
    fixed_costs: float = Field(..., description="Fixed costs")
    variable_cost_per_unit: float = Field(..., description="Variable cost per unit")
    price_per_unit: float = Field(..., description="Price per unit")
    status: str = Field(..., description="Calculation status")

class CashFlowRequest(BaseModel):
    """Cash flow forecast request"""
    initial_cash: float = Field(..., ge=0, description="Initial cash amount")
    monthly_revenue: float = Field(..., ge=0, description="Monthly revenue")
    monthly_expenses: float = Field(..., ge=0, description="Monthly expenses")
    months: int = Field(12, gt=0, le=60, description="Number of months to forecast")

class CashFlowResponse(BaseModel):
    """Cash flow forecast response"""
    forecast: List[Dict[str, Any]] = Field(..., description="Cash flow forecast")
    initial_cash: float = Field(..., description="Initial cash amount")
    monthly_revenue: float = Field(..., description="Monthly revenue")
    monthly_expenses: float = Field(..., description="Monthly expenses")
    months: int = Field(..., description="Number of months forecasted")
    status: str = Field(..., description="Calculation status")

class FinancialRatiosRequest(BaseModel):
    """Financial ratios calculation request"""
    revenue: float = Field(..., ge=0, description="Total revenue")
    expenses: float = Field(..., ge=0, description="Total expenses")
    assets: float = Field(..., ge=0, description="Total assets")
    liabilities: float = Field(..., ge=0, description="Total liabilities")
    equity: float = Field(..., ge=0, description="Total equity")

class FinancialRatiosResponse(BaseModel):
    """Financial ratios response"""
    profit_margin: float = Field(..., description="Profit margin percentage")
    return_on_assets: float = Field(..., description="Return on assets percentage")
    return_on_equity: float = Field(..., description="Return on equity percentage")
    debt_to_equity: float = Field(..., description="Debt to equity ratio")
    current_ratio: float = Field(..., description="Current ratio")
    quick_ratio: float = Field(..., description="Quick ratio")
    revenue: float = Field(..., description="Total revenue")
    expenses: float = Field(..., description="Total expenses")
    assets: float = Field(..., description="Total assets")
    liabilities: float = Field(..., description="Total liabilities")
    equity: float = Field(..., description="Total equity")
    status: str = Field(..., description="Calculation status")

# Analytics Models
class UserMetricsRequest(BaseModel):
    """User metrics tracking request"""
    user_id: str = Field(..., description="User ID")
    session_duration: float = Field(..., ge=0, description="Session duration in seconds")
    page_views: int = Field(..., ge=0, description="Number of page views")
    conversion_rate: float = Field(..., ge=0, le=1, description="Conversion rate (0-1)")
    revenue: float = Field(..., ge=0, description="Revenue generated")

class UserMetricsResponse(BaseModel):
    """User metrics response"""
    user_id: str = Field(..., description="User ID")
    session_duration: float = Field(..., description="Session duration in seconds")
    page_views: int = Field(..., description="Number of page views")
    conversion_rate: float = Field(..., description="Conversion rate")
    revenue: float = Field(..., description="Revenue generated")
    timestamp: str = Field(..., description="Metrics timestamp")
    status: str = Field(..., description="Tracking status")

class AnalyticsReportResponse(BaseModel):
    """Analytics report response"""
    total_users: int = Field(..., description="Total number of users")
    total_revenue: float = Field(..., description="Total revenue")
    average_session_duration: float = Field(..., description="Average session duration")
    conversion_rate: float = Field(..., description="Overall conversion rate")
    top_performing_pages: List[str] = Field(..., description="Top performing pages")
    user_retention_rate: float = Field(..., description="User retention rate")
    revenue_per_user: float = Field(..., description="Revenue per user")
    timestamp: str = Field(..., description="Report timestamp")
    status: str = Field(..., description="Report status")

class GADataRequest(BaseModel):
    """Google Analytics data integration request"""
    ga_data: Dict[str, Any] = Field(..., description="Google Analytics data")

class GADataResponse(BaseModel):
    """Google Analytics data response"""
    page_views: int = Field(..., description="Total page views")
    unique_visitors: int = Field(..., description="Unique visitors")
    bounce_rate: float = Field(..., description="Bounce rate")
    avg_session_duration: float = Field(..., description="Average session duration")
    conversion_rate: float = Field(..., description="Conversion rate")
    revenue: float = Field(..., description="Revenue")
    top_pages: List[str] = Field(..., description="Top pages")
    traffic_sources: Dict[str, Any] = Field(..., description="Traffic sources")
    device_categories: Dict[str, Any] = Field(..., description="Device categories")
    timestamp: str = Field(..., description="Integration timestamp")
    status: str = Field(..., description="Integration status")

class DecisionRequest(BaseModel):
    """Data-driven decision request"""
    decision_type: str = Field(..., description="Type of decision (pricing, marketing, product, user_experience)")
    data: Dict[str, Any] = Field(..., description="Data for decision making")

class DecisionResponse(BaseModel):
    """Data-driven decision response"""
    decision_type: str = Field(..., description="Type of decision made")
    recommendations: List[str] = Field(..., description="Decision recommendations")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level")
    expected_impact: str = Field(..., description="Expected impact")
    timestamp: str = Field(..., description="Decision timestamp")
    status: str = Field(..., description="Decision status")

class AnalyticsDashboardResponse(BaseModel):
    """Analytics dashboard response"""
    summary: Dict[str, Any] = Field(..., description="Analytics summary")
    recent_ab_tests: int = Field(..., description="Number of recent A/B tests")
    total_ab_tests: int = Field(..., description="Total number of A/B tests")
    ga_integrated: bool = Field(..., description="Whether GA is integrated")
    user_metrics_count: int = Field(..., description="Number of user metrics")
    reports_count: int = Field(..., description="Number of reports")
    timestamp: str = Field(..., description="Dashboard timestamp")
    status: str = Field(..., description="Dashboard status")