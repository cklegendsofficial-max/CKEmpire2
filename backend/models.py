from pydantic import BaseModel, Field, validator, EmailStr
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

# Authentication Models
class UserBase(BaseModel):
    """Base user model"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="User email")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    is_active: bool = Field(True, description="Whether user is active")

class UserCreate(UserBase):
    """Create user model"""
    password: str = Field(..., min_length=8, description="User password")

class UserResponse(UserBase):
    """User response model"""
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")

class OAuth2TokenResponse(TokenResponse):
    """OAuth2 token response"""
    provider: str = Field(..., description="OAuth2 provider")
    user: UserResponse = Field(..., description="User information")

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
    """Ethical report response with auto-fix and revert"""
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
    auto_fix_applied: bool = Field(False, description="Whether auto-fix was applied")
    revert_triggered: bool = Field(False, description="Whether revert was triggered")

class EthicsDashboardResponse(BaseModel):
    """Ethics dashboard response with auto-fix statistics"""
    overall_ethical_score: float = Field(..., description="Overall ethical score")
    bias_detection_rate: float = Field(..., description="Bias detection rate")
    correction_success_rate: float = Field(..., description="Correction success rate")
    auto_fix_success_rate: float = Field(..., description="Auto-fix success rate")
    avg_bias_reduction: float = Field(..., description="Average bias reduction")
    compliance_rate: float = Field(..., description="Compliance rate")
    risk_level_distribution: Dict[str, int] = Field(..., description="Risk level distribution")
    bias_types_detected: Dict[str, int] = Field(..., description="Bias types detected")
    correction_methods_used: Dict[str, int] = Field(..., description="Correction methods used")
    total_corrections: int = Field(..., description="Total corrections applied")
    total_auto_fixes: int = Field(..., description="Total auto-fixes applied")
    total_reverts: int = Field(..., description="Total reverts triggered")
    total_reports: int = Field(..., description="Total reports generated")
    aif360_integration: bool = Field(True, description="Whether AIF360 is integrated")
    last_updated: datetime = Field(..., description="Last update timestamp")

class AutoFixStatusResponse(BaseModel):
    """Auto-fix status response"""
    auto_fix_enabled: bool = Field(..., description="Whether auto-fix is enabled")
    auto_fix_threshold: float = Field(..., description="Auto-fix threshold")
    revert_threshold: float = Field(..., description="Revert threshold")
    recent_auto_fixes: int = Field(..., description="Number of recent auto-fixes")
    recent_reverts: int = Field(..., description="Number of recent reverts")
    total_auto_fixes: int = Field(..., description="Total auto-fixes")
    total_reverts: int = Field(..., description="Total reverts")
    aif360_integration: bool = Field(True, description="Whether AIF360 is integrated")
    last_auto_fix: Optional[Dict[str, Any]] = Field(None, description="Last auto-fix details")
    last_revert: Optional[Dict[str, Any]] = Field(None, description="Last revert details")

# Video/NFT Models
class VideoProductionRequest(BaseModel):
    """Enhanced video production request with AI minting"""
    theme: str = Field(..., min_length=1, description="Video theme/concept")
    duration: int = Field(60, ge=10, le=3600, description="Video duration in seconds")
    style: str = Field("zack_snyder", description="Video style (zack_snyder, action, dramatic, sci_fi)")
    ai_enhanced: bool = Field(True, description="Enable AI enhancement")
    blockchain_ready: bool = Field(True, description="Prepare for blockchain minting")

class VideoProductionResponse(BaseModel):
    """Enhanced video production response with AI minting data"""
    production_id: str = Field(..., description="Production ID")
    video_prompt: str = Field(..., description="Generated AI video prompt")
    video_metadata: Dict[str, Any] = Field(..., description="Enhanced video metadata")
    nft_metadata: Dict[str, Any] = Field(..., description="AI-optimized NFT metadata")
    pricing_prediction: Dict[str, Any] = Field(..., description="ML-powered pricing prediction")
    stripe_product: Dict[str, Any] = Field(..., description="Enhanced Stripe product info")
    ai_minting_config: Dict[str, Any] = Field(..., description="AI minting configuration")
    minting_history_count: int = Field(..., description="Total minting history count")
    status: str = Field(..., description="Production status")
    created_at: str = Field(..., description="Creation timestamp")

class NFTGenerationRequest(BaseModel):
    """Enhanced NFT generation request with AI optimization"""
    video_metadata: Dict[str, Any] = Field(..., description="Video metadata")
    collection_name: str = Field("CKEmpire AI Videos", description="NFT collection name")
    ai_enhanced: bool = Field(True, description="Enable AI enhancement")
    blockchain_metadata: Optional[Dict[str, Any]] = Field(None, description="Blockchain metadata")

class NFTGenerationResponse(BaseModel):
    """Enhanced NFT generation response with AI optimization"""
    nft_metadata: Dict[str, Any] = Field(..., description="AI-optimized NFT metadata")
    pricing_prediction: Dict[str, Any] = Field(..., description="ML-powered pricing prediction")
    stripe_product: Dict[str, Any] = Field(..., description="Enhanced Stripe product info")
    rarity_score: float = Field(..., description="Calculated rarity score")
    ai_enhanced: bool = Field(..., description="Whether AI enhancement was applied")
    blockchain_ready: bool = Field(..., description="Whether ready for blockchain minting")
    status: str = Field(..., description="Generation status")
    created_at: str = Field(..., description="Creation timestamp")

class PricingPredictionRequest(BaseModel):
    """Enhanced pricing prediction request with ML model"""
    nft_metadata: Dict[str, Any] = Field(..., description="NFT metadata")
    market_data: Optional[Dict[str, Any]] = Field(None, description="Market data")
    ml_model_version: str = Field("v2.1", description="ML model version")
    include_competitor_analysis: bool = Field(True, description="Include competitor analysis")

class PricingPredictionResponse(BaseModel):
    """Enhanced pricing prediction response with ML insights"""
    predicted_price: float = Field(..., description="Predicted price in ETH")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")
    factors: List[str] = Field(..., description="Pricing factors")
    market_analysis: Dict[str, Any] = Field(..., description="Enhanced market analysis")
    recommendation: str = Field(..., description="Pricing recommendation")
    ml_model_version: str = Field(..., description="ML model version used")
    training_data_points: int = Field(..., description="Training data points")
    market_volatility: float = Field(..., description="Market volatility score")
    competitor_analysis: Dict[str, Any] = Field(..., description="Competitor analysis")
    status: str = Field(..., description="Prediction status")

class VideoStyleResponse(BaseModel):
    """Enhanced video styles response with AI minting info"""
    styles: Dict[str, Dict[str, Any]] = Field(..., description="Available video styles")
    total_styles: int = Field(..., description="Total number of styles")
    ai_enhanced_styles: int = Field(..., description="Number of AI-enhanced styles")
    blockchain_ready_styles: int = Field(..., description="Number of blockchain-ready styles")

class NFTMetadataResponse(BaseModel):
    """Enhanced NFT metadata response with AI optimization"""
    production_id: str = Field(..., description="Production ID")
    metadata: Dict[str, Any] = Field(..., description="AI-optimized NFT metadata")
    rarity_score: float = Field(..., description="Calculated rarity score")
    ai_enhanced: bool = Field(..., description="Whether AI enhancement was applied")
    blockchain_metadata: Dict[str, Any] = Field(..., description="Blockchain metadata")
    market_analysis: Dict[str, Any] = Field(..., description="Market analysis")
    status: str = Field(..., description="Metadata status")

class AIMintingConfigResponse(BaseModel):
    """AI minting configuration response"""
    model_version: str = Field(..., description="AI model version")
    prompt_optimization: bool = Field(..., description="Enable prompt optimization")
    metadata_enhancement: bool = Field(..., description="Enable metadata enhancement")
    rarity_calculation: bool = Field(..., description="Enable rarity calculation")
    market_analysis: bool = Field(..., description="Enable market analysis")
    blockchain_integration: bool = Field(..., description="Enable blockchain integration")
    minting_history_count: int = Field(..., description="Total minting history count")

class NFTMintingRequest(BaseModel):
    """NFT minting request with AI optimization"""
    production_id: str = Field(..., description="Production ID")
    blockchain: str = Field("Ethereum", description="Target blockchain")
    gas_limit: Optional[int] = Field(None, description="Gas limit for minting")
    auto_price: bool = Field(True, description="Use AI-predicted price")

class NFTMintingResponse(BaseModel):
    """NFT minting response with blockchain data"""
    production_id: str = Field(..., description="Production ID")
    transaction_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    token_id: Optional[str] = Field(None, description="Minted token ID")
    contract_address: Optional[str] = Field(None, description="Smart contract address")
    gas_used: Optional[int] = Field(None, description="Gas used for minting")
    minting_cost: Optional[float] = Field(None, description="Minting cost in ETH")
    status: str = Field(..., description="Minting status")
    blockchain_metadata: Dict[str, Any] = Field(..., description="Blockchain metadata")
    created_at: str = Field(..., description="Minting timestamp")

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

# Enhanced Finance Models for CAC/LTV
class CACLTVRequest(BaseModel):
    """CAC/LTV calculation request"""
    customer_acquisition_cost: float = Field(..., gt=0, description="Customer acquisition cost")
    customer_lifetime_value: float = Field(..., gt=0, description="Customer lifetime value")
    average_order_value: Optional[float] = Field(None, gt=0, description="Average order value")
    purchase_frequency: Optional[float] = Field(None, gt=0, description="Purchase frequency per year")
    customer_lifespan: Optional[float] = Field(None, gt=0, description="Customer lifespan in years")
    marketing_spend: Optional[float] = Field(None, gt=0, description="Total marketing spend")
    new_customers: Optional[int] = Field(None, gt=0, description="Number of new customers")

class CACLTVResponse(BaseModel):
    """CAC/LTV calculation response"""
    cac: float = Field(..., description="Customer Acquisition Cost")
    ltv: float = Field(..., description="Customer Lifetime Value")
    ltv_cac_ratio: float = Field(..., description="LTV/CAC ratio")
    payback_period: float = Field(..., description="CAC payback period in months")
    profitability_score: str = Field(..., description="Profitability assessment")
    recommendations: List[str] = Field(..., description="Strategic recommendations")
    calculated_ltv: float = Field(..., description="Calculated LTV from inputs")
    calculated_cac: float = Field(..., description="Calculated CAC from inputs")
    status: str = Field(..., description="Calculation status")

class EnhancedROIRequest(BaseModel):
    """Enhanced ROI calculation request with CAC/LTV"""
    target_amount: float = Field(..., gt=0, description="Target amount to achieve")
    initial_investment: Optional[float] = Field(None, gt=0, description="Initial investment amount")
    time_period: float = Field(1.0, gt=0, description="Time period in years")
    customer_acquisition_cost: Optional[float] = Field(None, gt=0, description="Customer acquisition cost")
    customer_lifetime_value: Optional[float] = Field(None, gt=0, description="Customer lifetime value")
    marketing_spend: Optional[float] = Field(None, gt=0, description="Marketing spend")
    new_customers: Optional[int] = Field(None, gt=0, description="Number of new customers")

class EnhancedROIResponse(BaseModel):
    """Enhanced ROI calculation response with CAC/LTV analysis"""
    roi_percentage: float = Field(..., description="ROI percentage")
    annualized_roi: float = Field(..., description="Annualized ROI percentage")
    payback_period: float = Field(..., description="Payback period in years")
    initial_investment: float = Field(..., description="Initial investment amount")
    total_return: float = Field(..., description="Total return amount")
    time_period: float = Field(..., description="Time period in years")
    target_amount: float = Field(..., description="Target amount")
    cac_ltv_analysis: Optional[CACLTVResponse] = Field(None, description="CAC/LTV analysis")
    strategy_recommendations: List[str] = Field(..., description="Strategy recommendations")
    risk_assessment: str = Field(..., description="Risk assessment")
    status: str = Field(..., description="Calculation status")

class FinancialStrategyRequest(BaseModel):
    """Financial strategy request"""
    current_revenue: float = Field(..., gt=0, description="Current revenue")
    target_revenue: float = Field(..., gt=0, description="Target revenue")
    current_cac: float = Field(..., gt=0, description="Current customer acquisition cost")
    current_ltv: float = Field(..., gt=0, description="Current customer lifetime value")
    available_budget: float = Field(..., gt=0, description="Available budget for growth")
    growth_timeline: int = Field(12, gt=0, description="Growth timeline in months")

class FinancialStrategyResponse(BaseModel):
    """Financial strategy response"""
    recommended_investment: float = Field(..., description="Recommended investment amount")
    expected_new_customers: int = Field(..., description="Expected new customers")
    projected_revenue: float = Field(..., description="Projected revenue")
    expected_roi: float = Field(..., description="Expected ROI percentage")
    risk_level: str = Field(..., description="Risk level assessment")
    growth_strategy: str = Field(..., description="Recommended growth strategy")
    timeline_breakdown: List[Dict[str, Any]] = Field(..., description="Timeline breakdown")
    key_metrics: Dict[str, float] = Field(..., description="Key performance metrics")
    status: str = Field(..., description="Strategy status")

class DashboardGraphRequest(BaseModel):
    """Dashboard graph data request"""
    graph_type: str = Field(..., description="Type of graph (roi_trend, cac_ltv, revenue_forecast)")
    time_period: str = Field("12m", description="Time period (3m, 6m, 12m, 24m)")
    include_projections: bool = Field(True, description="Include future projections")

class DashboardGraphResponse(BaseModel):
    """Dashboard graph data response"""
    graph_type: str = Field(..., description="Type of graph")
    data_points: List[Dict[str, Any]] = Field(..., description="Graph data points")
    summary_metrics: Dict[str, float] = Field(..., description="Summary metrics")
    trend_analysis: str = Field(..., description="Trend analysis")
    recommendations: List[str] = Field(..., description="Graph-based recommendations")
    status: str = Field(..., description="Graph status")

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
    property_id: str = Field(..., description="Google Analytics property ID")
    start_date: str = Field(..., description="Start date for data range")
    end_date: str = Field(..., description="End date for data range")
    metrics: List[str] = Field(..., description="Metrics to retrieve")

class GADataResponse(BaseModel):
    """Google Analytics data response"""
    property_id: str = Field(..., description="Google Analytics property ID")
    start_date: str = Field(..., description="Start date for data range")
    end_date: str = Field(..., description="End date for data range")
    metrics: Dict[str, Any] = Field(..., description="Google Analytics metrics data")
    status: str = Field(..., description="Integration status")

class DecisionRequest(BaseModel):
    """Data-driven decision request"""
    category: str = Field(..., description="Category of decision (pricing, marketing, product, user_experience)")
    data: Dict[str, Any] = Field(..., description="Data for decision making")
    confidence_threshold: float = Field(0.95, ge=0, le=1, description="Confidence threshold for decision")

class DecisionResponse(BaseModel):
    """Data-driven decision response"""
    category: str = Field(..., description="Category of decision made")
    decision: str = Field(..., description="Decision made")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level")
    reasoning: List[str] = Field(..., description="Decision reasoning")
    data_points: int = Field(..., description="Number of data points used")
    status: str = Field(..., description="Decision status")

class AnalyticsDashboardResponse(BaseModel):
    """Analytics dashboard response"""
    summary: Dict[str, Any] = Field(..., description="Analytics summary")
    user_metrics: List[Dict[str, Any]] = Field(..., description="User metrics data")
    ab_test_results: List[Dict[str, Any]] = Field(..., description="A/B test results")
    top_pages: List[str] = Field(..., description="Top performing pages")
    revenue_trends: List[float] = Field(..., description="Revenue trends data")
    conversion_funnel: List[int] = Field(..., description="Conversion funnel data")
    status: str = Field(..., description="Dashboard status")

class SuccessResponse(BaseModel):
    """Success response model"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str
    error_code: Optional[str] = None

class ContentIdeaRequest(BaseModel):
    """Content idea generation request"""
    topic: str = Field(..., description="Content topic")
    content_type: str = Field(..., description="Type of content")
    target_audience: str = Field(..., description="Target audience")
    tone: str = Field(..., description="Content tone")
    length: str = Field(..., description="Content length")

class ContentIdeaResponse(BaseModel):
    """Content idea generation response"""
    ideas: List[str] = Field(..., description="Generated content ideas")
    ai_model: str = Field(..., description="AI model used")
    timestamp: str = Field(..., description="Generation timestamp")
    status: str = Field(..., description="Generation status")

class VideoRequest(BaseModel):
    """Video production request"""
    script: str = Field(..., description="Video script/content")
    style: str = Field(..., description="Video style (zack_snyder, cinematic, documentary, viral, corporate)")
    duration: int = Field(..., description="Video duration in seconds")

class VideoResponse(BaseModel):
    """Video production response"""
    title: str = Field(..., description="Video title")
    script: str = Field(..., description="Video script/content")
    style: str = Field(..., description="Video style")
    duration: int = Field(..., description="Video duration in seconds")
    resolution: Optional[str] = Field(None, description="Video resolution")
    output_path: Optional[str] = Field(None, description="Output file path")
    status: str = Field(..., description="Video generation status")
    created_at: Optional[str] = Field(None, description="Creation timestamp")

class NFTRequest(BaseModel):
    """NFT minting request"""
    name: str = Field(..., description="NFT name")
    description: str = Field(..., description="NFT description")
    image_path: str = Field(..., description="Path to NFT image")
    price_eth: float = Field(..., description="Price in ETH")
    collection: str = Field(..., description="NFT collection name")

class NFTResponse(BaseModel):
    """NFT minting response"""
    name: str = Field(..., description="NFT name")
    description: str = Field(..., description="NFT description")
    image_path: str = Field(..., description="NFT image path")
    price_eth: float = Field(..., description="Price in ETH")
    price_usd: Optional[float] = Field(None, description="Price in USD")
    collection: str = Field(..., description="NFT collection name")
    status: str = Field(..., description="Minting status")
    token_id: Optional[str] = Field(None, description="Token ID")
    transaction_hash: Optional[str] = Field(None, description="Transaction hash")
    metadata: Optional[dict] = Field(None, description="NFT metadata")
    created_at: Optional[str] = Field(None, description="Creation timestamp")

class AGIStateResponse(BaseModel):
    """AGI state response"""
    consciousness_score: float = Field(..., description="Consciousness score")
    decision_capability: float = Field(..., description="Decision capability")
    learning_rate: float = Field(..., description="Learning rate")
    creativity_level: float = Field(..., description="Creativity level")
    ethical_awareness: float = Field(..., description="Ethical awareness")
    last_evolution: Optional[str] = Field(None, description="Last evolution timestamp")
    evolution_count: int = Field(..., description="Number of evolutions")

class EmpireStrategyRequest(BaseModel):
    """Empire strategy request"""
    user_input: str = Field(..., description="User's strategy requirements")
    include_financial_metrics: Optional[bool] = Field(False, description="Include enhanced DCF calculations")

class EmpireStrategyResponse(BaseModel):
    """Empire strategy response"""
    strategy_type: str = Field(..., description="Type of strategy")
    title: str = Field(..., description="Strategy title")
    description: str = Field(..., description="Strategy description")
    key_actions: list = Field(..., description="Key actions for the strategy")
    timeline_months: int = Field(..., description="Timeline in months")
    estimated_investment: float = Field(..., description="Estimated investment")
    projected_roi: float = Field(..., description="Projected ROI")
    risk_level: str = Field(..., description="Risk level")
    success_metrics: list = Field(..., description="Success metrics")
    created_at: str = Field(..., description="Creation timestamp")
    financial_metrics: Optional[dict] = Field(None, description="Financial metrics (optional)")

class FinancialMetricsResponse(BaseModel):
    """Financial metrics response"""
    npv: Optional[float] = Field(None, description="Net Present Value")
    irr: Optional[float] = Field(None, description="Internal Rate of Return")
    roi: Optional[float] = Field(None, description="Return on Investment")
    payback_period: Optional[float] = Field(None, description="Payback period")
    break_even_point: Optional[float] = Field(None, description="Break-even point")
    ltv_cac_ratio: Optional[float] = Field(None, description="LTV/CAC ratio")
    risk_level: Optional[str] = Field(None, description="Risk level")
    summary: Optional[str] = Field(None, description="Summary of financial metrics")

class FineTuningRequest(BaseModel):
    """Fine-tuning request"""
    dataset_id: str = Field(..., description="Dataset ID for fine-tuning")
    epochs: int = Field(5, description="Number of epochs")
    learning_rate: float = Field(0.001, description="Learning rate")

class FineTuningResponse(BaseModel):
    """Fine-tuning response"""
    job_id: str = Field(..., description="Fine-tuning job ID")
    status: str = Field(..., description="Job status")
    started_at: Optional[str] = Field(None, description="Start time")
    finished_at: Optional[str] = Field(None, description="Finish time")

class FineTuningStatusResponse(BaseModel):
    """Fine-tuning status response"""
    job_id: str = Field(..., description="Fine-tuning job ID")
    status: str = Field(..., description="Job status")
    progress: Optional[float] = Field(None, description="Progress (0-1)")
    started_at: Optional[str] = Field(None, description="Start time")
    finished_at: Optional[str] = Field(None, description="Finish time")
    metrics: Optional[dict] = Field(None, description="Training metrics")