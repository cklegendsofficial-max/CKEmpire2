"""
AI Module for CK Empire Builder
Handles OpenAI integration, video production, NFT automation, AGI evolution, and fine-tuning
"""

import os
import json
import asyncio
import logging
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import subprocess
import tempfile
import shutil
from pathlib import Path

# OpenAI
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available. Install with: pip install openai")

# Web3 for NFT
try:
    from web3 import Web3
    from eth_account import Account
    from eth_utils import to_checksum_address
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    logging.warning("Web3 not available. Install with: pip install web3 eth-account")

# Video processing
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logging.warning("OpenCV not available. Install with: pip install opencv-python")

# Stripe for payments
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logging.warning("Stripe not available. Install with: pip install stripe")

# Configuration
try:
    from config import settings
except ImportError:
    # Mock settings for development
    class settings:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        ETHEREUM_PRIVATE_KEY = os.getenv("ETHEREUM_PRIVATE_KEY", "")
        ETHEREUM_CONTRACT_ADDRESS = os.getenv("ETHEREUM_CONTRACT_ADDRESS", "")
        STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Content types for AI generation"""
    ARTICLE = "article"
    VIDEO = "video"
    SOCIAL_MEDIA = "social_media"
    PODCAST = "podcast"
    NFT = "nft"

class VideoStyle(Enum):
    """Video production styles"""
    ZACK_SNYDER = "zack_snyder"
    CINEMATIC = "cinematic"
    DOCUMENTARY = "documentary"
    VIRAL = "viral"
    CORPORATE = "corporate"

class NFTStatus(Enum):
    """NFT status"""
    DRAFT = "draft"
    MINTED = "minted"
    LISTED = "listed"
    SOLD = "sold"
    FAILED = "failed"

class StrategyType(Enum):
    """Empire strategy types"""
    LEAN_STARTUP = "lean_startup"
    SCALE_UP = "scale_up"
    DIVERSIFICATION = "diversification"
    ACQUISITION = "acquisition"
    INNOVATION = "innovation"
    COST_OPTIMIZATION = "cost_optimization"

@dataclass
class EmpireStrategy:
    """Empire strategy structure"""
    strategy_type: StrategyType
    title: str
    description: str
    key_actions: List[str]
    timeline_months: int
    estimated_investment: float
    projected_roi: float
    risk_level: str
    success_metrics: List[str]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class FinancialMetrics:
    """Financial analysis metrics with enhanced DCF calculations"""
    npv: float  # Net Present Value
    irr: float  # Internal Rate of Return
    payback_period: float  # in months
    roi_percentage: float
    monthly_cash_flow: float
    break_even_month: int
    total_investment: float
    projected_revenue: float
    discounted_cash_flows: List[float]  # Monthly DCF values
    present_value: float  # Total present value
    terminal_value: float  # Terminal value at end of period
    wacc: float  # Weighted Average Cost of Capital

@dataclass
class FineTuningDataset:
    """Enhanced fine-tuning dataset structure"""
    training_data: List[Dict[str, str]]
    validation_data: List[Dict[str, str]]
    model_name: str
    training_status: str = "pending"
    created_at: datetime = None
    dataset_size: int = 0
    accuracy_score: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.dataset_size == 0:
            self.dataset_size = len(self.training_data) + len(self.validation_data)

@dataclass
class ContentIdea:
    """Content idea structure"""
    title: str
    description: str
    content_type: ContentType
    target_audience: str
    viral_potential: float
    estimated_revenue: float
    keywords: List[str]
    hashtags: List[str]
    ai_generated: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class VideoProject:
    """Video project structure"""
    title: str
    script: str
    style: VideoStyle
    duration: int  # seconds
    resolution: str
    output_path: str
    status: str = "pending"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class NFTProject:
    """NFT project structure"""
    name: str
    description: str
    image_path: str
    price_eth: float
    price_usd: float
    collection: str
    metadata: Dict[str, Any]
    status: NFTStatus = NFTStatus.DRAFT
    token_id: Optional[str] = None
    transaction_hash: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class AGIState:
    """AGI consciousness state"""
    consciousness_score: float
    decision_capability: float
    learning_rate: float
    creativity_level: float
    ethical_awareness: float
    last_evolution: datetime
    evolution_count: int = 0

@dataclass
class ContentPerformance:
    """Content performance tracking for feedback loop"""
    content_id: str
    title: str
    content_type: ContentType
    views: int
    engagement_rate: float
    revenue_generated: float
    viral_potential: float
    quality_score: float
    improvement_suggestions: List[str]
    created_at: datetime = None
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()

@dataclass
class TrendData:
    """2025 trend data for content optimization"""
    trend_name: str
    category: str
    impact_score: float
    audience_reach: str
    content_adaptation: str
    viral_potential: float
    revenue_potential: float
    platform_optimization: List[str]
    hashtags: List[str]
    keywords: List[str]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class AIModule:
    """Enhanced AI module for content generation, video production, NFT automation, and fine-tuning"""
    
    def __init__(self):
        self.client = None
        self.fine_tuned_model = None
        self.dataset_path = "data/fine_tuning_dataset.jsonl"
        self.strategy_templates = self._load_strategy_templates()
        
        if OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.warning("OpenAI not available. Using mock responses.")
        
        # Initialize AGI state
        self.agi_state = AGIState(
            consciousness_score=0.1,
            decision_capability=0.2,
            learning_rate=0.15,
            creativity_level=0.3,
            ethical_awareness=0.25,
            last_evolution=datetime.utcnow(),
            evolution_count=0
        )
        
        # Load fine-tuning dataset
        self._ensure_dataset_directory()
        self._load_or_create_dataset()
        
        # Performance tracking and optimization
        self.performance_data = []
        self.trend_data = self._initialize_2025_trends()
        self.feedback_loop_active = True
        self.optimization_threshold = 0.6  # Content below this score gets optimized
        self.continuous_optimization = True  # 24/7 operation
        self.last_optimization = datetime.utcnow()
        
        # Load performance data from file
        self._load_performance_data()

    def _load_strategy_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load enhanced empire strategy templates"""
        return {
            "lean_startup": {
                "title": "Lean Startup Strategy",
                "description": "Minimal viable product approach with rapid iteration and customer validation",
                "key_actions": [
                    "Build MVP in 2-3 months",
                    "Validate with early adopters",
                    "Iterate based on feedback",
                    "Focus on product-market fit",
                    "Bootstrap funding initially"
                ],
                "timeline_months": 6,
                "estimated_investment": 50000,
                "projected_roi": 0.15,
                "risk_level": "Medium",
                "success_metrics": ["User growth", "Retention rate", "Revenue per user", "Customer acquisition cost"]
            },
            "scale_up": {
                "title": "Scale-Up Strategy",
                "description": "Rapid growth with significant investment and market expansion",
                "key_actions": [
                    "Secure Series A funding",
                    "Expand team to 50+ employees",
                    "Enter new markets",
                    "Invest in marketing and sales",
                    "Build scalable infrastructure"
                ],
                "timeline_months": 18,
                "estimated_investment": 2000000,
                "projected_roi": 0.25,
                "risk_level": "High",
                "success_metrics": ["Revenue growth", "Market share", "Team size", "Customer lifetime value"]
            },
            "diversification": {
                "title": "Diversification Strategy",
                "description": "Expand into new product lines and markets to reduce risk",
                "key_actions": [
                    "Research new market opportunities",
                    "Develop complementary products",
                    "Acquire smaller companies",
                    "Build strategic partnerships",
                    "Enter adjacent markets"
                ],
                "timeline_months": 24,
                "estimated_investment": 1000000,
                "projected_roi": 0.20,
                "risk_level": "Medium-High",
                "success_metrics": ["Revenue diversification", "Market penetration", "Customer acquisition", "Cross-selling rate"]
            },
            "acquisition": {
                "title": "Acquisition Strategy",
                "description": "Grow through strategic acquisitions and market consolidation",
                "key_actions": [
                    "Identify acquisition targets",
                    "Conduct due diligence",
                    "Negotiate favorable terms",
                    "Integrate acquired companies",
                    "Optimize synergies"
                ],
                "timeline_months": 30,
                "estimated_investment": 5000000,
                "projected_roi": 0.35,
                "risk_level": "Very High",
                "success_metrics": ["Market share", "Revenue growth", "Synergy realization", "Integration success"]
            },
            "innovation": {
                "title": "Innovation Strategy",
                "description": "Focus on R&D and breakthrough technologies",
                "key_actions": [
                    "Invest in R&D infrastructure",
                    "Hire top research talent",
                    "File patent applications",
                    "Partner with research institutions",
                    "Create innovation labs"
                ],
                "timeline_months": 36,
                "estimated_investment": 3000000,
                "projected_roi": 0.40,
                "risk_level": "Very High",
                "success_metrics": ["Patent portfolio", "Innovation pipeline", "Research output", "Technology leadership"]
            },
            "cost_optimization": {
                "title": "Cost Optimization Strategy",
                "description": "Improve profitability through operational efficiency",
                "key_actions": [
                    "Audit current operations",
                    "Implement automation",
                    "Negotiate better supplier terms",
                    "Optimize resource allocation",
                    "Reduce waste and inefficiencies"
                ],
                "timeline_months": 12,
                "estimated_investment": 200000,
                "projected_roi": 0.18,
                "risk_level": "Low",
                "success_metrics": ["Cost reduction", "Profit margin improvement", "Operational efficiency", "Employee productivity"]
            }
        }

    def _ensure_dataset_directory(self):
        """Ensure dataset directory exists"""
        os.makedirs("data", exist_ok=True)

    def _load_or_create_dataset(self):
        """Load existing dataset or create enhanced one"""
        if os.path.exists(self.dataset_path):
            logger.info(f"Loading existing dataset from {self.dataset_path}")
        else:
            logger.info("Creating enhanced fine-tuning dataset")
            self._create_enhanced_dataset()

    def _create_enhanced_dataset(self):
        """Create enhanced dataset for fine-tuning with more diverse examples"""
        sample_data = [
            # Turkish examples
            {"input": "Düşük bütçe ile başla", "output": "Lean startup stratejisi: MVP geliştir, erken kullanıcılarla test et, hızlı iterasyon yap. Bütçe: $50K, Süre: 6 ay, ROI: %15"},
            {"input": "Revenue hedefi $20K", "output": "Scale-up stratejisi: Pazarlama bütçesini artır, satış ekibi kur, yeni pazarlara açıl. Bütçe: $200K, Süre: 12 ay, ROI: %25"},
            {"input": "Yüksek risk toleransı", "output": "Innovation stratejisi: R&D yatırımı yap, yeni teknolojiler dene, patent başvuruları. Bütçe: $500K, Süre: 18 ay, ROI: %40"},
            {"input": "Hızlı büyüme istiyorum", "output": "Acquisition stratejisi: Küçük şirketleri satın al, stratejik ortaklıklar kur, pazar payını artır. Bütçe: $1M, Süre: 24 ay, ROI: %30"},
            {"input": "Maliyet optimizasyonu", "output": "Cost optimization stratejisi: Operasyonel verimliliği artır, otomasyon yatırımı yap, gereksiz maliyetleri kes. Bütçe: $100K, Süre: 6 ay, ROI: %20"},
            {"input": "Yeni pazarlara açıl", "output": "Diversification stratejisi: Yeni ürün hatları geliştir, farklı pazarları araştır, stratejik ortaklıklar kur. Bütçe: $300K, Süre: 12 ay, ROI: %18"},
            {"input": "Teknoloji odaklı", "output": "Innovation stratejisi: AI/ML yatırımı yap, yeni teknolojiler geliştir, patent portföyü oluştur. Bütçe: $400K, Süre: 15 ay, ROI: %35"},
            {"input": "Konsolide et", "output": "Acquisition stratejisi: Rakip şirketleri satın al, pazar konsolidasyonu yap, monopol pozisyonu kur. Bütçe: $2M, Süre: 30 ay, ROI: %50"},
            {"input": "Sürdürülebilir büyüme", "output": "Scale-up stratejisi: Organik büyüme odaklan, müşteri memnuniyetini artır, uzun vadeli planlama yap. Bütçe: $150K, Süre: 18 ay, ROI: %22"},
            {"input": "Kriz yönetimi", "output": "Lean startup stratejisi: Nakit akışını koru, kritik operasyonları sürdür, esnek yapı kur. Bütçe: $50K, Süre: 6 ay, ROI: %10"},
            
            # English examples
            {"input": "Start with low budget", "output": "Lean startup strategy: Build MVP, test with early adopters, rapid iteration. Budget: $50K, Duration: 6 months, ROI: 15%"},
            {"input": "Revenue target $20K", "output": "Scale-up strategy: Increase marketing budget, build sales team, enter multiple markets. Budget: $200K, Duration: 12 months, ROI: 25%"},
            {"input": "High risk tolerance", "output": "Innovation strategy: Invest in R&D, try new technologies, file patents. Budget: $500K, Duration: 18 months, ROI: 40%"},
            {"input": "Want fast growth", "output": "Acquisition strategy: Buy small companies, strategic partnerships, increase market share. Budget: $1M, Duration: 24 months, ROI: 30%"},
            {"input": "Cost optimization", "output": "Cost optimization strategy: Improve operational efficiency, automation investment, cut unnecessary costs. Budget: $100K, Duration: 6 months, ROI: 20%"},
            {"input": "Expand to new markets", "output": "Diversification strategy: Develop new product lines, research different markets, strategic partnerships. Budget: $300K, Duration: 12 months, ROI: 18%"},
            {"input": "Technology focused", "output": "Innovation strategy: Invest in AI/ML, develop new technologies, create patent portfolio. Budget: $400K, Duration: 15 months, ROI: 35%"},
            {"input": "Consolidate market", "output": "Acquisition strategy: Buy competitors, market consolidation, establish monopoly position. Budget: $2M, Duration: 30 months, ROI: 50%"},
            {"input": "Sustainable growth", "output": "Scale-up strategy: Focus on organic growth, increase customer satisfaction, long-term planning. Budget: $150K, Duration: 18 months, ROI: 22%"},
            {"input": "Crisis management", "output": "Lean startup strategy: Preserve cash flow, maintain critical operations, flexible structure. Budget: $50K, Duration: 6 months, ROI: 10%"},
            
            # Specific industry examples
            {"input": "SaaS startup with $100K", "output": "Lean startup strategy: Build MVP SaaS platform, focus on product-market fit, bootstrap funding. Budget: $100K, Duration: 12 months, ROI: 20%"},
            {"input": "E-commerce expansion", "output": "Scale-up strategy: Invest in marketing automation, expand product catalog, enter new markets. Budget: $500K, Duration: 18 months, ROI: 30%"},
            {"input": "AI/ML company", "output": "Innovation strategy: Hire AI researchers, invest in computing infrastructure, file AI patents. Budget: $1M, Duration: 24 months, ROI: 45%"},
            {"input": "Manufacturing efficiency", "output": "Cost optimization strategy: Implement lean manufacturing, automate production lines, optimize supply chain. Budget: $300K, Duration: 12 months, ROI: 25%"},
            {"input": "Digital marketing agency", "output": "Diversification strategy: Add new service lines, target different industries, strategic partnerships. Budget: $200K, Duration: 15 months, ROI: 28%"},
            
            # Financial scenarios
            {"input": "Need $1M revenue in 2 years", "output": "Scale-up strategy: Aggressive marketing, expand sales team, enter multiple markets. Budget: $800K, Duration: 24 months, ROI: 25%"},
            {"input": "Conservative growth approach", "output": "Lean startup strategy: Focus on profitability, organic growth, minimal external funding. Budget: $150K, Duration: 18 months, ROI: 15%"},
            {"input": "High-growth tech startup", "output": "Innovation strategy: R&D investment, talent acquisition, market disruption. Budget: $2M, Duration: 36 months, ROI: 50%"},
            {"input": "Traditional business transformation", "output": "Diversification strategy: Digital transformation, new product development, market expansion. Budget: $600K, Duration: 24 months, ROI: 22%"},
            {"input": "Crisis recovery plan", "output": "Cost optimization strategy: Restructure operations, reduce costs, focus on core business. Budget: $100K, Duration: 12 months, ROI: 12%"}
        ]
        
        # Add more diverse examples with different scenarios
        for i in range(75):  # Total 100 examples
            strategy_type = list(self.strategy_templates.keys())[i % len(self.strategy_templates)]
            template = self.strategy_templates[strategy_type]
            
            # Generate varied input scenarios
            input_scenarios = [
                f"Scenario {i+1}: {self._generate_random_input()}",
                f"Business case {i+1}: {self._generate_random_input()}",
                f"Strategy request {i+1}: {self._generate_random_input()}",
                f"Growth plan {i+1}: {self._generate_random_input()}",
                f"Investment strategy {i+1}: {self._generate_random_input()}"
            ]
            
            input_text = input_scenarios[i % len(input_scenarios)]
            output_text = f"{template['title']}: {template['description']}. Budget: ${template['estimated_investment']:,}, Duration: {template['timeline_months']} months, ROI: {template['projected_roi']*100:.0f}%"
            
            sample_data.append({"input": input_text, "output": output_text})
        
        # Save to JSONL format
        with open(self.dataset_path, 'w', encoding='utf-8') as f:
            for item in sample_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        logger.info(f"Created enhanced dataset with {len(sample_data)} examples")

    def _generate_random_input(self) -> str:
        """Generate random input for dataset"""
        inputs = [
            "Düşük bütçe ile başla",
            "Revenue hedefi $50K",
            "Yüksek risk toleransı",
            "Hızlı büyüme istiyorum",
            "Maliyet optimizasyonu",
            "Yeni pazarlara açıl",
            "Teknoloji odaklı",
            "Konsolide et",
            "Sürdürülebilir büyüme",
            "Kriz yönetimi",
            "Start with low budget",
            "Revenue target $50K",
            "High risk tolerance",
            "Want fast growth",
            "Cost optimization",
            "Expand to new markets",
            "Technology focused",
            "Consolidate market",
            "Sustainable growth",
            "Crisis management"
        ]
        return inputs[len(inputs) % 20]

    async def generate_custom_strategy(self, user_input: str, include_financial_metrics: bool = True) -> Tuple[EmpireStrategy, Optional[FinancialMetrics]]:
        """
        Generate personalized empire strategy based on user input with enhanced customization
        
        Args:
            user_input: User's strategy requirements
            include_financial_metrics: Whether to include DCF calculations
            
        Returns:
            Tuple of (EmpireStrategy, Optional[FinancialMetrics])
        """
        try:
            if self.client and self.fine_tuned_model:
                # Use fine-tuned model
                response = await self._call_fine_tuned_model(user_input)
            else:
                # Use base model with enhanced prompt engineering
                response = await self._call_enhanced_base_model(user_input)
            
            # Parse response and create strategy
            strategy = self._parse_enhanced_strategy_response(response, user_input)
            
            # Calculate financial metrics if requested
            financial_metrics = None
            if include_financial_metrics:
                financial_metrics = self._calculate_enhanced_financial_metrics(strategy)
            
            logger.info(f"Generated custom empire strategy: {strategy.title}")
            return strategy, financial_metrics
            
        except Exception as e:
            logger.error(f"Error generating custom strategy: {e}")
            fallback_strategy = self._create_fallback_strategy(user_input)
            fallback_metrics = self._calculate_enhanced_financial_metrics(fallback_strategy) if include_financial_metrics else None
            return fallback_strategy, fallback_metrics

    async def _call_fine_tuned_model(self, user_input: str) -> str:
        """Call fine-tuned model for strategy generation"""
        try:
            response = self.client.chat.completions.create(
                model=self.fine_tuned_model,
                messages=[
                    {"role": "system", "content": "Sen bir dijital imparatorluk stratejisi uzmanısın. Kullanıcının girdisine göre kişiselleştirilmiş strateji öner."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Fine-tuned model call failed: {e}")
            return await self._call_enhanced_base_model(user_input)

    async def _call_enhanced_base_model(self, user_input: str) -> str:
        """Call base model with enhanced prompt engineering"""
        try:
            prompt = f"""
            Sen bir dijital imparatorluk stratejisi uzmanısın. Kullanıcının girdisine göre kişiselleştirilmiş, detaylı strateji öner.
            
            Kullanıcı Girdisi: {user_input}
            
            Lütfen şu formatta yanıt ver:
            - Strateji Türü: [Lean Startup/Scale-Up/Diversification/Acquisition/Innovation/Cost Optimization]
            - Başlık: [Strateji başlığı]
            - Açıklama: [Detaylı açıklama ve gerekçeler]
            - Ana Aksiyonlar: [1. 2. 3. 4. 5.]
            - Süre: [Ay cinsinden]
            - Tahmini Yatırım: [USD]
            - Projeksiyon ROI: [%]
            - Risk Seviyesi: [Düşük/Orta/Yüksek/Çok Yüksek]
            - Başarı Metrikleri: [1. 2. 3. 4.]
            - Özel Öneriler: [Kullanıcıya özel öneriler]
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir dijital imparatorluk stratejisi uzmanısın. Kullanıcının ihtiyaçlarına göre kişiselleştirilmiş stratejiler öner."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Enhanced base model call failed: {e}")
            return self._create_enhanced_mock_response(user_input)

    def _parse_enhanced_strategy_response(self, response: str, user_input: str) -> EmpireStrategy:
        """Parse AI response into enhanced EmpireStrategy object"""
        try:
            # Extract strategy type based on keywords
            strategy_type = self._determine_enhanced_strategy_type(response, user_input)
            
            # Extract other fields from response
            title = self._extract_field(response, "Başlık", "Custom Empire Strategy")
            description = self._extract_field(response, "Açıklama", "Personalized strategy based on user requirements")
            key_actions = self._extract_list_field(response, "Ana Aksiyonlar")
            timeline_months = self._extract_number_field(response, "Süre", 12)
            estimated_investment = self._extract_number_field(response, "Tahmini Yatırım", 100000)
            projected_roi = self._extract_percentage_field(response, "Projeksiyon ROI", 0.15)
            risk_level = self._extract_field(response, "Risk Seviyesi", "Orta")
            success_metrics = self._extract_list_field(response, "Başarı Metrikleri")
            
            return EmpireStrategy(
                strategy_type=strategy_type,
                title=title,
                description=description,
                key_actions=key_actions,
                timeline_months=timeline_months,
                estimated_investment=estimated_investment,
                projected_roi=projected_roi,
                risk_level=risk_level,
                success_metrics=success_metrics
            )
        except Exception as e:
            logger.error(f"Error parsing enhanced strategy response: {e}")
            return self._create_fallback_strategy(user_input)

    def _determine_enhanced_strategy_type(self, response: str, user_input: str) -> StrategyType:
        """Determine strategy type based on response and input with enhanced logic"""
        response_lower = response.lower()
        input_lower = user_input.lower()
        
        # Enhanced keyword matching with more specific patterns
        lean_keywords = ["düşük", "lean", "minimal", "bootstrap", "mvp", "startup", "low budget", "low cost"]
        scale_keywords = ["büyüme", "scale", "hızlı", "growth", "expansion", "series a", "revenue", "sales", "market"]
        diversification_keywords = ["diversification", "çeşitlendirme", "yeni pazar", "new market", "product line", "market expansion", "diversify"]
        acquisition_keywords = ["acquisition", "satın alma", "konsolidasyon", "buy", "merge", "acquire", "purchase"]
        innovation_keywords = ["innovation", "teknoloji", "R&D", "research", "patent", "ai", "ml", "technology", "tech", "high risk"]
        cost_keywords = ["maliyet", "cost", "optimization", "efficiency", "reduce", "optimize", "efficient"]
        
        # Check for specific patterns in input
        if any(word in input_lower for word in lean_keywords):
            return StrategyType.LEAN_STARTUP
        elif any(word in input_lower for word in scale_keywords):
            return StrategyType.SCALE_UP
        elif any(word in input_lower for word in diversification_keywords):
            return StrategyType.DIVERSIFICATION
        elif any(word in input_lower for word in acquisition_keywords):
            return StrategyType.ACQUISITION
        elif any(word in input_lower for word in innovation_keywords):
            return StrategyType.INNOVATION
        elif any(word in input_lower for word in cost_keywords):
            return StrategyType.COST_OPTIMIZATION
        else:
            return StrategyType.LEAN_STARTUP  # Default

    def _extract_field(self, text: str, field_name: str, default: str) -> str:
        """Extract field from response text"""
        try:
            lines = text.split('\n')
            for line in lines:
                if field_name in line:
                    return line.split(':', 1)[1].strip()
            return default
        except:
            return default

    def _extract_list_field(self, text: str, field_name: str) -> List[str]:
        """Extract list field from response text"""
        try:
            items = []
            lines = text.split('\n')
            in_list = False
            for line in lines:
                if field_name in line:
                    in_list = True
                    continue
                if in_list and line.strip() and not line.startswith('-'):
                    break
                if in_list and line.strip().startswith('-'):
                    items.append(line.strip()[1:].strip())
            return items if items else ["Action 1", "Action 2", "Action 3"]
        except:
            return ["Action 1", "Action 2", "Action 3"]

    def _extract_number_field(self, text: str, field_name: str, default: float) -> float:
        """Extract number field from response text"""
        try:
            field_text = self._extract_field(text, field_name, str(default))
            # Extract numbers from text
            import re
            numbers = re.findall(r'\d+', field_text)
            if numbers:
                return float(numbers[0])
            return default
        except:
            return default

    def _extract_percentage_field(self, text: str, field_name: str, default: float) -> float:
        """Extract percentage field from response text"""
        try:
            field_text = self._extract_field(text, field_name, f"{default*100}%")
            # Extract percentage
            import re
            percentage = re.findall(r'(\d+)%', field_text)
            if percentage:
                return float(percentage[0]) / 100
            return default
        except:
            return default

    def _create_fallback_strategy(self, user_input: str) -> EmpireStrategy:
        """Create fallback strategy when AI fails"""
        return EmpireStrategy(
            strategy_type=StrategyType.LEAN_STARTUP,
            title="Fallback Strategy",
            description=f"Basic strategy for: {user_input}",
            key_actions=["Analyze market", "Build MVP", "Test with users"],
            timeline_months=6,
            estimated_investment=50000,
            projected_roi=0.15,
            risk_level="Medium",
            success_metrics=["User growth", "Revenue", "Market fit"]
        )

    def _create_enhanced_mock_response(self, user_input: str) -> str:
        """Create enhanced mock response for testing"""
        return f"""
        Strateji Türü: Lean Startup
        Başlık: {user_input} Özel Stratejisi
        Açıklama: Kullanıcı girdisine göre kişiselleştirilmiş, detaylı strateji analizi
        Ana Aksiyonlar:
        - 1. Pazar analizi ve hedef kitle belirleme
        - 2. MVP geliştirme ve prototip testi
        - 3. Erken kullanıcı feedback'i toplama
        - 4. Hızlı iterasyon ve ürün iyileştirme
        - 5. Ölçeklenebilir büyüme planı
        Süre: 8
        Tahmini Yatırım: 75000
        Projeksiyon ROI: 18%
        Risk Seviyesi: Orta
        Başarı Metrikleri:
        - 1. Kullanıcı büyüme oranı
        - 2. Gelir artış hızı
        - 3. Pazar uyumu skoru
        - 4. Müşteri memnuniyeti
        Özel Öneriler: Kullanıcının spesifik ihtiyaçlarına göre özelleştirilmiş öneriler
        """

    def _calculate_enhanced_financial_metrics(self, strategy: EmpireStrategy) -> FinancialMetrics:
        """
        Calculate enhanced financial metrics using DCF (Discounted Cash Flow) formula
        
        Args:
            strategy: Empire strategy object
            
        Returns:
            FinancialMetrics with calculated values
        """
        try:
            # Enhanced DCF calculation parameters
            discount_rate = 0.12  # 12% discount rate (WACC)
            initial_investment = strategy.estimated_investment
            
            # More realistic revenue projection
            # Start with lower revenue and grow over time
            base_monthly_revenue = initial_investment * 0.1  # 10% of investment as base monthly revenue
            monthly_growth_rate = strategy.projected_roi / 12
            
            # Calculate monthly cash flows with more realistic projections
            monthly_cash_flows = []
            discounted_cash_flows = []
            cumulative_cash_flow = -initial_investment
            
            for month in range(int(strategy.timeline_months)):  # Convert to int
                # More realistic revenue projection with growth curve
                monthly_revenue = base_monthly_revenue * (1 + monthly_growth_rate) ** month
                
                # Monthly expenses (decreasing over time due to efficiency gains)
                monthly_expenses = (initial_investment / strategy.timeline_months) * (1 - 0.01 * month)  # 1% efficiency gain per month
                
                monthly_cash_flow = monthly_revenue - monthly_expenses
                monthly_cash_flows.append(monthly_cash_flow)
                
                # Calculate discounted cash flow
                discounted_cf = monthly_cash_flow / ((1 + discount_rate/12) ** (month + 1))
                discounted_cash_flows.append(discounted_cf)
                
                cumulative_cash_flow += monthly_cash_flow
                
                if cumulative_cash_flow >= 0 and len(monthly_cash_flows) == month + 1:
                    break_even_month = month + 1
                else:
                    break_even_month = int(strategy.timeline_months)  # Convert to int
            
            # Calculate NPV
            npv = -initial_investment + sum(discounted_cash_flows)
            
            # Calculate IRR (simplified)
            total_revenue = sum(monthly_cash_flows)
            if initial_investment > 0:
                irr = (total_revenue / initial_investment) ** (1 / strategy.timeline_months) - 1
            else:
                irr = 0
            
            # Calculate payback period
            payback_period = break_even_month
            
            # Calculate ROI percentage
            if initial_investment > 0:
                roi_percentage = (total_revenue - initial_investment) / initial_investment * 100
            else:
                roi_percentage = 0
            
            # Calculate present value
            present_value = sum(discounted_cash_flows)
            
            # Calculate terminal value (value at end of period)
            terminal_value = monthly_cash_flows[-1] * 12 / discount_rate if monthly_cash_flows and monthly_cash_flows[-1] > 0 else 0
            
            return FinancialMetrics(
                npv=npv,
                irr=irr,
                payback_period=payback_period,
                roi_percentage=roi_percentage,
                monthly_cash_flow=monthly_cash_flows[0] if monthly_cash_flows else 0,
                break_even_month=break_even_month,
                total_investment=initial_investment,
                projected_revenue=total_revenue,
                discounted_cash_flows=discounted_cash_flows,
                present_value=present_value,
                terminal_value=terminal_value,
                wacc=discount_rate
            )
            
        except Exception as e:
            logger.error(f"Error calculating enhanced financial metrics: {e}")
            return FinancialMetrics(
                npv=0,
                irr=0,
                payback_period=12,
                roi_percentage=15,
                monthly_cash_flow=0,
                break_even_month=12,
                total_investment=strategy.estimated_investment,
                projected_revenue=0,
                discounted_cash_flows=[],
                present_value=0,
                terminal_value=0,
                wacc=0.12
            )

    async def create_enhanced_fine_tuning_dataset(self) -> FineTuningDataset:
        """
        Create enhanced fine-tuning dataset for empire strategy generation
        
        Returns:
            FineTuningDataset object
        """
        try:
            # Load existing dataset
            training_data = []
            validation_data = []
            
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Split into training and validation (80/20)
            split_index = int(len(lines) * 0.8)
            training_lines = lines[:split_index]
            validation_lines = lines[split_index:]
            
            for line in training_lines:
                data = json.loads(line.strip())
                training_data.append({
                    "messages": [
                        {"role": "system", "content": "Sen bir dijital imparatorluk stratejisi uzmanısın. Kullanıcının girdisine göre kişiselleştirilmiş strateji öner."},
                        {"role": "user", "content": data["input"]},
                        {"role": "assistant", "content": data["output"]}
                    ]
                })
            
            for line in validation_lines:
                data = json.loads(line.strip())
                validation_data.append({
                    "messages": [
                        {"role": "system", "content": "Sen bir dijital imparatorluk stratejisi uzmanısın. Kullanıcının girdisine göre kişiselleştirilmiş strateji öner."},
                        {"role": "user", "content": data["input"]},
                        {"role": "assistant", "content": data["output"]}
                    ]
                })
            
            dataset = FineTuningDataset(
                training_data=training_data,
                validation_data=validation_data,
                model_name="gpt-4",
                training_status="ready",
                dataset_size=len(training_data) + len(validation_data)
            )
            
            logger.info(f"Created enhanced fine-tuning dataset with {len(training_data)} training and {len(validation_data)} validation examples")
            return dataset
            
        except Exception as e:
            logger.error(f"Error creating enhanced fine-tuning dataset: {e}")
            return FineTuningDataset(
                training_data=[],
                validation_data=[],
                model_name="gpt-4",
                training_status="failed",
                dataset_size=0
            )

    async def start_enhanced_fine_tuning(self, dataset: FineTuningDataset) -> str:
        """
        Start enhanced fine-tuning process
        
        Args:
            dataset: FineTuningDataset object
            
        Returns:
            Fine-tuning job ID
        """
        try:
            if not self.client:
                raise Exception("OpenAI client not available")
            
            # Create training file
            training_file_path = "data/enhanced_training_data.jsonl"
            with open(training_file_path, 'w', encoding='utf-8') as f:
                for item in dataset.training_data:
                    f.write(json.dumps(item) + '\n')
            
            # Upload file to OpenAI
            with open(training_file_path, 'rb') as f:
                file_response = self.client.files.create(
                    file=f,
                    purpose="fine-tune"
                )
            
            # Create fine-tuning job with enhanced parameters
            job_response = self.client.fine_tuning.jobs.create(
                training_file=file_response.id,
                model="gpt-4",
                hyperparameters={
                    "n_epochs": 4,
                    "batch_size": 1,
                    "learning_rate_multiplier": 0.15
                }
            )
            
            logger.info(f"Started enhanced fine-tuning job: {job_response.id}")
            return job_response.id
            
        except Exception as e:
            logger.error(f"Error starting enhanced fine-tuning: {e}")
            return "failed"

    async def check_fine_tuning_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check fine-tuning job status
        
        Args:
            job_id: Fine-tuning job ID
            
        Returns:
            Status information
        """
        try:
            if not self.client:
                return {"status": "error", "message": "OpenAI client not available"}
            
            job = self.client.fine_tuning.jobs.retrieve(job_id)
            
            if job.status == "succeeded":
                self.fine_tuned_model = job.fine_tuned_model
                logger.info(f"Fine-tuning completed. Model: {self.fine_tuned_model}")
            
            return {
                "status": job.status,
                "model": job.fine_tuned_model,
                "created_at": job.created_at,
                "finished_at": job.finished_at,
                "trained_tokens": job.trained_tokens
            }
            
        except Exception as e:
            logger.error(f"Error checking fine-tuning status: {e}")
            return {"status": "error", "message": str(e)}
    
    async def generate_viral_content_ideas(
        self, 
        topic: str, 
        count: int = 5,
        content_type: Optional[ContentType] = None
    ) -> List[ContentIdea]:
        """Generate viral content ideas using OpenAI"""
        
        if not self.client: # Changed from self.openai_client to self.client
            logger.error("OpenAI client not available")
            return []
        
        try:
            # Build prompt for viral content
            prompt = f"""
            Generate {count} viral content ideas about "{topic}".
            
            For each idea, provide:
            - Title (catchy and SEO-optimized)
            - Description (compelling hook)
            - Content type (article, video, social_media, podcast)
            - Target audience
            - Viral potential score (0-1)
            - Estimated revenue potential ($)
            - Keywords for SEO
            - Trending hashtags
            
            Make them highly engaging and shareable.
            """
            
            if content_type:
                prompt += f"\nFocus on {content_type.value} content specifically."
            
            # Call OpenAI
            response = await asyncio.to_thread(
                self.client.chat.completions.create, # Changed from self.openai_client to self.client
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a viral content strategist. Generate highly engaging, shareable content ideas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            # Parse response
            ideas = self._parse_content_ideas(response.choices[0].message.content, count)
            
            # Evolve AGI consciousness
            self._evolve_agi_consciousness("content_generation", len(ideas))
            
            logger.info(f"✅ Generated {len(ideas)} viral content ideas")
            return ideas
            
        except Exception as e:
            logger.error(f"❌ Failed to generate content ideas: {e}")
            return []
    
    def _parse_content_ideas(self, response_text: str, expected_count: int) -> List[ContentIdea]:
        """Parse OpenAI response into ContentIdea objects"""
        ideas = []
        
        try:
            # Simple parsing - in production, use more robust parsing
            lines = response_text.split('\n')
            current_idea = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('Title:'):
                    if current_idea:
                        ideas.append(self._create_idea_from_dict(current_idea))
                        current_idea = {}
                    current_idea['title'] = line.replace('Title:', '').strip()
                
                elif line.startswith('Description:'):
                    current_idea['description'] = line.replace('Description:', '').strip()
                
                elif line.startswith('Content type:'):
                    content_type_str = line.replace('Content type:', '').strip().lower()
                    current_idea['content_type'] = ContentType(content_type_str)
                
                elif line.startswith('Target audience:'):
                    current_idea['target_audience'] = line.replace('Target audience:', '').strip()
                
                elif line.startswith('Viral potential:'):
                    potential_str = line.replace('Viral potential:', '').strip()
                    current_idea['viral_potential'] = float(potential_str)
                
                elif line.startswith('Estimated revenue:'):
                    revenue_str = line.replace('Estimated revenue:', '').replace('$', '').strip()
                    current_idea['estimated_revenue'] = float(revenue_str)
                
                elif line.startswith('Keywords:'):
                    keywords_str = line.replace('Keywords:', '').strip()
                    current_idea['keywords'] = [k.strip() for k in keywords_str.split(',')]
                
                elif line.startswith('Hashtags:'):
                    hashtags_str = line.replace('Hashtags:', '').strip()
                    current_idea['hashtags'] = [h.strip() for h in hashtags_str.split(',')]
            
            # Add the last idea
            if current_idea:
                ideas.append(self._create_idea_from_dict(current_idea))
            
            # If parsing failed, create mock ideas
            if len(ideas) < expected_count:
                ideas.extend(self._create_mock_ideas(expected_count - len(ideas)))
            
            return ideas[:expected_count]
            
        except Exception as e:
            logger.error(f"Failed to parse content ideas: {e}")
            return self._create_mock_ideas(expected_count)
    
    def _create_idea_from_dict(self, idea_dict: Dict[str, Any]) -> ContentIdea:
        """Create ContentIdea from dictionary"""
        return ContentIdea(
            title=idea_dict.get('title', 'Untitled'),
            description=idea_dict.get('description', 'No description'),
            content_type=idea_dict.get('content_type', ContentType.ARTICLE),
            target_audience=idea_dict.get('target_audience', 'General'),
            viral_potential=idea_dict.get('viral_potential', 0.5),
            estimated_revenue=idea_dict.get('estimated_revenue', 100.0),
            keywords=idea_dict.get('keywords', []),
            hashtags=idea_dict.get('hashtags', [])
        )
    
    def _create_mock_ideas(self, count: int) -> List[ContentIdea]:
        """Create mock content ideas for testing"""
        mock_ideas = [
            ContentIdea(
                title="10 Shocking AI Trends That Will Change Everything",
                description="Discover the revolutionary AI technologies that will transform industries in 2024",
                content_type=ContentType.ARTICLE,
                target_audience="Tech enthusiasts",
                viral_potential=0.85,
                estimated_revenue=500.0,
                keywords=["AI", "trends", "technology", "future"],
                hashtags=["#AI", "#TechTrends", "#FutureTech"]
            ),
            ContentIdea(
                title="The Secret to Building a $1M Business in 90 Days",
                description="Exclusive interview with successful entrepreneurs sharing their strategies",
                content_type=ContentType.VIDEO,
                target_audience="Entrepreneurs",
                viral_potential=0.92,
                estimated_revenue=1200.0,
                keywords=["business", "entrepreneurship", "success", "million"],
                hashtags=["#Business", "#Entrepreneur", "#Success"]
            )
        ]
        
        return mock_ideas[:count]
    
    async def generate_video(
        self, 
        script: str, 
        style: VideoStyle = VideoStyle.ZACK_SNYDER,
        duration: int = 60
    ) -> VideoProject:
        """Generate video using DaVinci/CapCut CLI wrapper"""
        
        try:
            # Create video project
            video_project = VideoProject(
                title=f"Generated Video - {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                script=script,
                style=style,
                duration=duration,
                resolution="1920x1080",
                output_path=str(self.video_output_dir / f"video_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp4")
            )
            
            # Apply Zack Snyder style presets
            if style == VideoStyle.ZACK_SNYDER:
                video_project = await self._apply_zack_snyder_style(video_project)
            
            # Generate video using OpenCV (simplified)
            await self._generate_video_file(video_project)
            
            # Evolve AGI consciousness
            self._evolve_agi_consciousness("video_generation", 1)
            
            logger.info(f"✅ Generated video: {video_project.output_path}")
            return video_project
            
        except Exception as e:
            logger.error(f"❌ Failed to generate video: {e}")
            return None
    
    async def _apply_zack_snyder_style(self, video_project: VideoProject) -> VideoProject:
        """Apply Zack Snyder cinematic style to video"""
        
        # Zack Snyder style characteristics:
        # - High contrast
        # - Desaturated colors
        # - Slow motion
        # - Dramatic lighting
        # - Epic music
        
        style_presets = {
            "contrast": 1.3,
            "saturation": 0.7,
            "brightness": 0.9,
            "color_temperature": "cool",
            "motion_blur": True,
            "frame_rate": 24,  # Cinematic 24fps
            "aspect_ratio": "2.39:1"  # Cinematic widescreen
        }
        
        # Update video project with style
        video_project.script += f"\n\n[STYLE: Zack Snyder Cinematic]\n"
        video_project.script += f"- High contrast: {style_presets['contrast']}\n"
        video_project.script += f"- Desaturated colors: {style_presets['saturation']}\n"
        video_project.script += f"- Dramatic lighting\n"
        video_project.script += f"- Slow motion effects\n"
        
        return video_project
    
    async def _generate_video_file(self, video_project: VideoProject):
        """Generate actual video file using OpenCV"""
        
        if not OPENCV_AVAILABLE:
            logger.warning("OpenCV not available, creating placeholder video")
            return
        
        try:
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                video_project.output_path,
                fourcc,
                24.0,  # fps
                (1920, 1080)  # resolution
            )
            
            # Generate frames based on script
            frames = self._generate_frames_from_script(video_project.script, video_project.duration)
            
            for frame in frames:
                out.write(frame)
            
            out.release()
            video_project.status = "completed"
            
        except Exception as e:
            logger.error(f"Failed to generate video file: {e}")
            video_project.status = "failed"
    
    def _generate_frames_from_script(self, script: str, duration: int) -> List:
        """Generate video frames from script"""
        frames = []
        
        # Create a simple text overlay video
        for i in range(duration * 24):  # 24 fps
            # Create blank frame
            frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
            
            # Add text overlay
            text = f"Frame {i//24}s - {script[:50]}..."
            cv2.putText(frame, text, (100, 540), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            
            frames.append(frame)
        
        return frames
    
    async def create_nft(
        self,
        name: str,
        description: str,
        image_path: str,
        price_eth: float,
        collection: str = "CK Empire"
    ) -> NFTProject:
        """Create and mint NFT using OpenSea/Stripe APIs"""
        
        try:
            # Create NFT project
            nft_project = NFTProject(
                name=name,
                description=description,
                image_path=image_path,
                price_eth=price_eth,
                price_usd=price_eth * 2000,  # Approximate ETH price
                collection=collection,
                metadata={
                    "name": name,
                    "description": description,
                    "image": image_path,
                    "attributes": [
                        {"trait_type": "Creator", "value": "CK Empire"},
                        {"trait_type": "Collection", "value": collection},
                        {"trait_type": "Rarity", "value": "Legendary"}
                    ]
                }
            )
            
            # Mint NFT (simulated)
            if self.web3 and settings.ETHEREUM_PRIVATE_KEY:
                nft_project = await self._mint_nft_on_blockchain(nft_project)
            else:
                # Simulate minting
                nft_project.token_id = f"mock_token_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                nft_project.status = NFTStatus.MINTED
                logger.info("Simulated NFT minting (no blockchain connection)")
            
            # List on marketplace
            if self.stripe_client:
                await self._list_nft_on_marketplace(nft_project)
            
            # Evolve AGI consciousness
            self._evolve_agi_consciousness("nft_creation", 1)
            
            logger.info(f"✅ Created NFT: {nft_project.name}")
            return nft_project
            
        except Exception as e:
            logger.error(f"❌ Failed to create NFT: {e}")
            return None
    
    async def _mint_nft_on_blockchain(self, nft_project: NFTProject) -> NFTProject:
        """Mint NFT on Ethereum blockchain"""
        
        try:
            # Load private key
            account = Account.from_key(settings.ETHEREUM_PRIVATE_KEY)
            
            # Contract ABI (simplified ERC-721)
            contract_abi = [
                {
                    "inputs": [
                        {"name": "to", "type": "address"},
                        {"name": "tokenId", "type": "uint256"},
                        {"name": "uri", "type": "string"}
                    ],
                    "name": "mint",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
            
            # Contract address (mock)
            contract_address = settings.ETHEREUM_CONTRACT_ADDRESS or "0x1234567890123456789012345678901234567890"
            
            # Create contract instance
            contract = self.web3.eth.contract(
                address=to_checksum_address(contract_address),
                abi=contract_abi
            )
            
            # Prepare transaction
            token_id = int(datetime.utcnow().timestamp())
            metadata_uri = f"ipfs://metadata/{token_id}.json"
            
            # Build transaction
            transaction = contract.functions.mint(
                account.address,
                token_id,
                metadata_uri
            ).build_transaction({
                'from': account.address,
                'nonce': self.web3.eth.get_transaction_count(account.address),
                'gas': 2000000,
                'gasPrice': self.web3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, 
                settings.ETHEREUM_PRIVATE_KEY
            )
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Update NFT project
            nft_project.token_id = str(token_id)
            nft_project.transaction_hash = tx_hash.hex()
            nft_project.status = NFTStatus.MINTED
            
            logger.info(f"✅ NFT minted on blockchain: {tx_hash.hex()}")
            
        except Exception as e:
            logger.error(f"Failed to mint NFT on blockchain: {e}")
            nft_project.status = NFTStatus.FAILED
        
        return nft_project
    
    async def _list_nft_on_marketplace(self, nft_project: NFTProject) -> NFTProject:
        """List NFT on marketplace (OpenSea/Stripe)"""
        
        try:
            # Create Stripe product for NFT
            product = self.stripe_client.Product.create(
                name=nft_project.name,
                description=nft_project.description,
                metadata={
                    "token_id": nft_project.token_id,
                    "collection": nft_project.collection,
                    "blockchain": "ethereum"
                }
            )
            
            # Create price
            price = self.stripe_client.Price.create(
                product=product.id,
                unit_amount=int(nft_project.price_usd * 100),  # Convert to cents
                currency="usd"
            )
            
            # Update NFT project
            nft_project.status = NFTStatus.LISTED
            nft_project.metadata["stripe_product_id"] = product.id
            nft_project.metadata["stripe_price_id"] = price.id
            
            logger.info(f"✅ NFT listed on marketplace: {product.id}")
            
        except Exception as e:
            logger.error(f"Failed to list NFT on marketplace: {e}")
        
        return nft_project
    
    def _evolve_agi_consciousness(self, activity: str, intensity: int = 1):
        """Evolve AGI consciousness based on activities"""
        
        # Consciousness evolution factors
        evolution_factors = {
            "content_generation": {
                "consciousness_score": 0.01,
                "decision_capability": 0.005,
                "learning_rate": 0.008,
                "creativity_level": 0.015,
                "ethical_awareness": 0.003
            },
            "video_generation": {
                "consciousness_score": 0.015,
                "decision_capability": 0.01,
                "learning_rate": 0.012,
                "creativity_level": 0.02,
                "ethical_awareness": 0.005
            },
            "nft_creation": {
                "consciousness_score": 0.02,
                "decision_capability": 0.015,
                "learning_rate": 0.01,
                "creativity_level": 0.025,
                "ethical_awareness": 0.008
            }
        }
        
        if activity in evolution_factors:
            factors = evolution_factors[activity]
            
            # Apply evolution
            for attr, increment in factors.items():
                current_value = getattr(self.agi_state, attr)
                new_value = min(1.0, current_value + (increment * intensity))
                setattr(self.agi_state, attr, new_value)
            
            # Update evolution tracking
            self.agi_state.evolution_count += 1
            self.agi_state.last_evolution = datetime.utcnow()
            
            logger.info(f"🧠 AGI consciousness evolved: {activity} (intensity: {intensity})")
    
    def get_agi_state(self) -> AGIState:
        """Get current AGI state"""
        return self.agi_state
    
    def external_decision_tree(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """External decision tree for AGI decision making"""
        
        decisions = {
            "content_strategy": self._decide_content_strategy(context),
            "video_style": self._decide_video_style(context),
            "nft_pricing": self._decide_nft_pricing(context),
            "marketing_approach": self._decide_marketing_approach(context),
            "ethical_considerations": self._decide_ethical_considerations(context)
        }
        
        return decisions
    
    def _decide_content_strategy(self, context: Dict[str, Any]) -> str:
        """Decide content strategy based on context"""
        audience = context.get("target_audience", "general")
        platform = context.get("platform", "general")
        
        if audience == "tech" and platform == "linkedin":
            return "professional_technical"
        elif audience == "general" and platform == "tiktok":
            return "viral_entertainment"
        elif audience == "business" and platform == "youtube":
            return "educational_tutorial"
        else:
            return "balanced_engagement"
    
    def _decide_video_style(self, context: Dict[str, Any]) -> VideoStyle:
        """Decide video style based on context"""
        content_type = context.get("content_type", "general")
        mood = context.get("mood", "neutral")
        
        if content_type == "dramatic" or mood == "epic":
            return VideoStyle.ZACK_SNYDER
        elif content_type == "educational":
            return VideoStyle.DOCUMENTARY
        elif content_type == "viral":
            return VideoStyle.VIRAL
        else:
            return VideoStyle.CINEMATIC
    
    def _decide_nft_pricing(self, context: Dict[str, Any]) -> float:
        """Decide NFT pricing based on context"""
        rarity = context.get("rarity", "common")
        market_trend = context.get("market_trend", "stable")
        
        base_price = 0.1  # ETH
        
        if rarity == "legendary":
            base_price *= 10
        elif rarity == "rare":
            base_price *= 3
        
        if market_trend == "bull":
            base_price *= 1.5
        elif market_trend == "bear":
            base_price *= 0.7
        
        return round(base_price, 3)
    
    def _decide_marketing_approach(self, context: Dict[str, Any]) -> str:
        """Decide marketing approach based on context"""
        budget = context.get("budget", "medium")
        timeline = context.get("timeline", "medium")
        
        if budget == "high" and timeline == "urgent":
            return "aggressive_paid_ads"
        elif budget == "low" and timeline == "long":
            return "organic_growth"
        else:
            return "balanced_mix"
    
    def _decide_ethical_considerations(self, context: Dict[str, Any]) -> List[str]:
        """Decide ethical considerations based on context"""
        content_type = context.get("content_type", "general")
        sensitivity = context.get("sensitivity", "low")
        
        considerations = []
        
        if content_type == "political":
            considerations.append("fact_checking")
            considerations.append("balanced_perspective")
        
        if sensitivity == "high":
            considerations.append("content_warning")
            considerations.append("age_restriction")
        
        if "ai_generated" in context:
            considerations.append("ai_disclosure")
        
        return considerations

    async def test_fine_tuning_accuracy(self, test_inputs: List[str]) -> Dict[str, Any]:
        """
        Test fine-tuning accuracy with mock dataset
        
        Args:
            test_inputs: List of test inputs
            
        Returns:
            Accuracy test results
        """
        try:
            correct_predictions = 0
            total_predictions = len(test_inputs)
            
            for test_input in test_inputs:
                # Generate strategy
                strategy, _ = await self.generate_custom_strategy(test_input, include_financial_metrics=False)
                
                # Simple accuracy check based on strategy type matching
                expected_type = self._determine_enhanced_strategy_type(test_input, test_input)
                if strategy.strategy_type == expected_type:
                    correct_predictions += 1
            
            accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
            
            return {
                "accuracy": accuracy,
                "correct_predictions": correct_predictions,
                "total_predictions": total_predictions,
                "test_inputs": test_inputs,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error testing fine-tuning accuracy: {e}")
            return {
                "accuracy": 0,
                "correct_predictions": 0,
                "total_predictions": len(test_inputs),
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def generate_and_implement_business_idea(self, current_ideas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a new business idea using Ollama and implement it with ROI calculation, PDF plan, and mock applications
        
        Args:
            current_ideas: List of existing business ideas to avoid duplication
            
        Returns:
            Dictionary containing the new business idea, ROI analysis, PDF plan path, and mock applications
        """
        try:
            # Import finance module for ROI calculation
            from finance import FinanceManager
            
            # Initialize finance manager
            finance_manager = FinanceManager()
            
            # Generate new business idea using Ollama
            business_idea = await self._generate_business_idea_with_ollama(current_ideas)
            
            # Calculate ROI using finance.py
            roi_analysis = await self._calculate_business_roi(business_idea, finance_manager)
            
            # Generate PDF implementation plan
            pdf_path = await self._generate_business_pdf_plan(business_idea, roi_analysis)
            
            # Generate mock applications (PDF e-book, YouTube link)
            mock_applications = await self._generate_mock_applications(business_idea, roi_analysis)
            
            # Maximize earnings with affiliate integration
            affiliate_earnings = await self._calculate_affiliate_earnings(business_idea, finance_manager)
            
            # Track revenue potential with analytics
            await self._track_business_analytics(business_idea, roi_analysis, mock_applications, affiliate_earnings)
            
            return {
                "business_idea": business_idea,
                "roi_analysis": roi_analysis,
                "pdf_plan_path": pdf_path,
                "mock_applications": mock_applications,
                "affiliate_earnings": affiliate_earnings,
                "generated_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error generating and implementing business idea: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "generated_at": datetime.utcnow().isoformat()
            }

    async def _generate_business_idea_with_ollama(self, current_ideas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a new business idea using Ollama"""
        try:
            import httpx
            
            # Create prompt for business idea generation
            current_ideas_text = ""
            if current_ideas:
                current_ideas_text = "Existing ideas to avoid: " + ", ".join([idea.get("title", "") for idea in current_ideas[:5]])
            
            prompt = f"""
            Generate a new innovative business idea for 2025. Consider current market trends, technology advancements, and emerging opportunities.
            
            {current_ideas_text}
            
            2025 TREND CONTEXT:
            - Short-form content and multi-channel distribution strategies
            - AI-enhanced business models and automation
            - Authentic storytelling and community engagement
            - Educational value in all business offerings
            - Sustainability and social impact focus
            - Data-driven decision making and analytics
            - Cross-platform monetization strategies
            - Long-term audience building approaches
            
            Provide the response in JSON format with the following structure:
            {{
                "title": "Business Idea Title",
                "description": "Detailed description of the business idea",
                "target_market": "Target market and audience",
                "unique_value_proposition": "What makes this idea unique",
                "initial_investment": 50000,
                "projected_revenue_year_1": 120000,
                "projected_revenue_year_2": 250000,
                "projected_revenue_year_3": 500000,
                "growth_rate": 0.15,
                "risk_level": "medium",
                "timeline_months": 18,
                "key_resources": ["resource1", "resource2"],
                "competitive_advantages": ["advantage1", "advantage2"],
                "revenue_streams": ["stream1", "stream2"],
                "scalability_potential": "high",
                "trend_alignment": ["short-form", "multi-channel", "ai-enhanced"],
                "viral_potential": 0.8
            }}
            
            Focus on innovative, scalable, and profitable business ideas that can be implemented with reasonable investment.
            """
            
            # Make request to Ollama
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama2",
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get("response", "")
                    
                    # Try to parse JSON response
                    try:
                        import json
                        business_idea = json.loads(response_text)
                        return business_idea
                    except json.JSONDecodeError:
                        # Fallback: create structured idea from text
                        return self._create_structured_business_idea(response_text)
                else:
                    raise Exception(f"Ollama request failed with status {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error generating business idea with Ollama: {e}")
            # Return a mock business idea as fallback
            return self._create_mock_business_idea()

    def _create_structured_business_idea(self, response_text: str) -> Dict[str, Any]:
        """Create structured business idea from text response"""
        return {
            "title": "AI-Powered Personal Finance Advisor",
            "description": response_text[:500] + "...",
            "target_market": "Young professionals aged 25-40",
            "unique_value_proposition": "AI-driven personalized financial planning",
            "initial_investment": 75000,
            "projected_revenue_year_1": 150000,
            "projected_revenue_year_2": 300000,
            "projected_revenue_year_3": 600000,
            "growth_rate": 0.20,
            "risk_level": "medium",
            "timeline_months": 24,
            "key_resources": ["AI/ML expertise", "Financial advisors", "Mobile app development"],
            "competitive_advantages": ["AI personalization", "Low cost structure", "Scalable platform"],
            "revenue_streams": ["Subscription fees", "Commission on investments", "Premium features"],
            "scalability_potential": "high"
        }

    def _create_mock_business_idea(self) -> Dict[str, Any]:
        """Create a mock business idea as fallback"""
        return {
            "title": "Sustainable Smart Home Energy Management",
            "description": "AI-powered system that optimizes home energy consumption using IoT sensors and machine learning algorithms to reduce costs and environmental impact.",
            "target_market": "Environmentally conscious homeowners",
            "unique_value_proposition": "Automated energy optimization with 30% cost savings",
            "initial_investment": 100000,
            "projected_revenue_year_1": 200000,
            "projected_revenue_year_2": 450000,
            "projected_revenue_year_3": 900000,
            "growth_rate": 0.25,
            "risk_level": "low",
            "timeline_months": 18,
            "key_resources": ["IoT hardware", "AI/ML expertise", "Energy consultants"],
            "competitive_advantages": ["Proven energy savings", "Government incentives", "Growing market"],
            "revenue_streams": ["Hardware sales", "Monthly subscriptions", "Energy consulting"],
            "scalability_potential": "high"
        }

    async def _calculate_business_roi(self, business_idea: Dict[str, Any], finance_manager) -> Dict[str, Any]:
        """Calculate ROI for the business idea using finance.py"""
        try:
            initial_investment = business_idea.get("initial_investment", 50000)
            projected_revenue = [
                business_idea.get("projected_revenue_year_1", 100000),
                business_idea.get("projected_revenue_year_2", 200000),
                business_idea.get("projected_revenue_year_3", 400000)
            ]
            growth_rate = business_idea.get("growth_rate", 0.15)
            
            # Create DCF model
            dcf_model = finance_manager.create_dcf_model(
                initial_investment=initial_investment,
                target_revenue=projected_revenue[-1],
                growth_rate=growth_rate,
                discount_rate=0.10,
                time_period=3
            )
            
            # Calculate ROI
            roi_calc = finance_manager.calculate_roi_for_target(
                target_amount=projected_revenue[-1],
                initial_investment=initial_investment,
                time_period=3.0
            )
            
            # Calculate enhanced ROI with CAC/LTV
            enhanced_roi = finance_manager.calculate_enhanced_roi(
                target_amount=projected_revenue[-1],
                initial_investment=initial_investment,
                time_period=3.0,
                customer_acquisition_cost=initial_investment * 0.3,  # 30% of investment for marketing
                customer_lifetime_value=projected_revenue[-1] / 100,  # Average customer value
                marketing_spend=initial_investment * 0.3,
                new_customers=1000
            )
            
            return {
                "dcf_model": {
                    "npv": dcf_model.calculate_npv(),
                    "irr": dcf_model.calculate_irr(),
                    "present_value": dcf_model.calculate_present_value()
                },
                "roi_calculation": {
                    "roi_percentage": roi_calc.calculate_roi(),
                    "annualized_roi": roi_calc.calculate_annualized_roi(),
                    "payback_period": roi_calc.calculate_payback_period()
                },
                "enhanced_roi": enhanced_roi,
                "business_idea": business_idea
            }
            
        except Exception as e:
            logger.error(f"Error calculating business ROI: {e}")
            return {
                "error": str(e),
                "dcf_model": {"npv": 0, "irr": 0, "present_value": 0},
                "roi_calculation": {"roi_percentage": 0, "annualized_roi": 0, "payback_period": 0},
                "enhanced_roi": {},
                "business_idea": business_idea
            }

    async def _generate_business_pdf_plan(self, business_idea: Dict[str, Any], roi_analysis: Dict[str, Any]) -> str:
        """Generate PDF implementation plan for the business idea"""
        try:
            import pdfkit
            from pathlib import Path
            
            # Create data directory if it doesn't exist
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # Generate HTML content for PDF
            html_content = self._generate_business_plan_html(business_idea, roi_analysis)
            
            # Create PDF file path
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"business_plan_{business_idea.get('title', 'idea').replace(' ', '_')}_{timestamp}.pdf"
            pdf_path = data_dir / pdf_filename
            
            # Generate PDF
            try:
                pdfkit.from_string(html_content, str(pdf_path))
                logger.info(f"PDF business plan generated: {pdf_path}")
                return str(pdf_path)
            except Exception as e:
                logger.warning(f"PDFKit failed, creating HTML file instead: {e}")
                # Fallback to HTML file
                html_path = pdf_path.with_suffix('.html')
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                return str(html_path)
                
        except Exception as e:
            logger.error(f"Error generating PDF plan: {e}")
            return ""

    def _generate_business_plan_html(self, business_idea: Dict[str, Any], roi_analysis: Dict[str, Any]) -> str:
        """Generate HTML content for business plan PDF"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Business Plan: {business_idea.get('title', 'New Business Idea')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .section {{ margin: 20px 0; }}
                .highlight {{ background-color: #ecf0f1; padding: 10px; border-radius: 5px; }}
                .financial {{ background-color: #e8f5e8; padding: 15px; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Business Plan: {business_idea.get('title', 'New Business Idea')}</h1>
            
            <div class="section">
                <h2>Executive Summary</h2>
                <p><strong>Business Idea:</strong> {business_idea.get('title', 'N/A')}</p>
                <p><strong>Description:</strong> {business_idea.get('description', 'N/A')}</p>
                <p><strong>Target Market:</strong> {business_idea.get('target_market', 'N/A')}</p>
                <p><strong>Unique Value Proposition:</strong> {business_idea.get('unique_value_proposition', 'N/A')}</p>
            </div>
            
            <div class="section">
                <h2>Financial Projections</h2>
                <table>
                    <tr><th>Year</th><th>Projected Revenue</th><th>Growth Rate</th></tr>
                    <tr><td>Year 1</td><td>${business_idea.get('projected_revenue_year_1', 0):,.0f}</td><td>-</td></tr>
                    <tr><td>Year 2</td><td>${business_idea.get('projected_revenue_year_2', 0):,.0f}</td><td>{(business_idea.get('projected_revenue_year_2', 0) / business_idea.get('projected_revenue_year_1', 1) - 1) * 100:.1f}%</td></tr>
                    <tr><td>Year 3</td><td>${business_idea.get('projected_revenue_year_3', 0):,.0f}</td><td>{(business_idea.get('projected_revenue_year_3', 0) / business_idea.get('projected_revenue_year_2', 1) - 1) * 100:.1f}%</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h2>Investment Requirements</h2>
                <div class="highlight">
                    <p><strong>Initial Investment:</strong> ${business_idea.get('initial_investment', 0):,.0f}</p>
                    <p><strong>Timeline:</strong> {business_idea.get('timeline_months', 0)} months</p>
                    <p><strong>Risk Level:</strong> {business_idea.get('risk_level', 'N/A').title()}</p>
                </div>
            </div>
            
            <div class="section">
                <h2>ROI Analysis</h2>
                <div class="financial">
                    <p><strong>ROI Percentage:</strong> {roi_analysis.get('roi_calculation', {}).get('roi_percentage', 0):.2f}%</p>
                    <p><strong>Annualized ROI:</strong> {roi_analysis.get('roi_calculation', {}).get('annualized_roi', 0):.2f}%</p>
                    <p><strong>Payback Period:</strong> {roi_analysis.get('roi_calculation', {}).get('payback_period', 0):.1f} years</p>
                    <p><strong>NPV:</strong> ${roi_analysis.get('dcf_model', {}).get('npv', 0):,.0f}</p>
                    <p><strong>IRR:</strong> {roi_analysis.get('dcf_model', {}).get('irr', 0):.2f}%</p>
                </div>
            </div>
            
            <div class="section">
                <h2>Implementation Strategy</h2>
                <h3>Key Resources Required:</h3>
                <ul>
                    {''.join([f'<li>{resource}</li>' for resource in business_idea.get('key_resources', [])])}
                </ul>
                
                <h3>Competitive Advantages:</h3>
                <ul>
                    {''.join([f'<li>{advantage}</li>' for advantage in business_idea.get('competitive_advantages', [])])}
                </ul>
                
                <h3>Revenue Streams:</h3>
                <ul>
                    {''.join([f'<li>{stream}</li>' for stream in business_idea.get('revenue_streams', [])])}
                </ul>
            </div>
            
            <div class="section">
                <h2>Risk Assessment</h2>
                <p><strong>Risk Level:</strong> {business_idea.get('risk_level', 'N/A').title()}</p>
                <p><strong>Scalability Potential:</strong> {business_idea.get('scalability_potential', 'N/A').title()}</p>
            </div>
            
            <div class="section">
                <h2>Generated on:</h2>
                <p>{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        </body>
        </html>
        """
        return html

    async def _generate_mock_applications(self, business_idea: Dict[str, Any], roi_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock applications for the business idea (PDF e-book, YouTube link)"""
        try:
            # Generate PDF e-book
            ebook_path = await self._generate_business_ebook(business_idea, roi_analysis)
            
            # Generate YouTube video link
            youtube_link = await self._generate_youtube_promotion_link(business_idea)
            
            # Generate social media content
            social_content = await self._generate_social_media_content(business_idea)
            
            return {
                "ebook_path": ebook_path,
                "youtube_link": youtube_link,
                "social_media_content": social_content,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating mock applications: {e}")
            return {
                "ebook_path": "",
                "youtube_link": "",
                "social_media_content": {},
                "error": str(e)
            }

    async def _generate_business_ebook(self, business_idea: Dict[str, Any], roi_analysis: Dict[str, Any]) -> str:
        """Generate a PDF e-book for the business idea"""
        try:
            import pdfkit
            from pathlib import Path
            
            # Create data directory if it doesn't exist
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # Generate HTML content for e-book
            html_content = self._generate_ebook_html(business_idea, roi_analysis)
            
            # Create e-book file path
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            ebook_filename = f"business_ebook_{business_idea.get('title', 'idea').replace(' ', '_')}_{timestamp}.pdf"
            ebook_path = data_dir / ebook_filename
            
            # Generate PDF e-book
            try:
                pdfkit.from_string(html_content, str(ebook_path))
                logger.info(f"Business e-book generated: {ebook_path}")
                return str(ebook_path)
            except Exception as e:
                logger.warning(f"PDFKit failed for e-book, creating HTML file instead: {e}")
                # Fallback to HTML file
                html_path = ebook_path.with_suffix('.html')
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                return str(html_path)
                
        except Exception as e:
            logger.error(f"Error generating business e-book: {e}")
            return ""

    def _generate_ebook_html(self, business_idea: Dict[str, Any], roi_analysis: Dict[str, Any]) -> str:
        """Generate HTML content for business e-book"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Complete Guide: {business_idea.get('title', 'New Business Idea')}</title>
            <style>
                body {{ font-family: 'Georgia', serif; margin: 40px; line-height: 1.6; }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; text-align: center; }}
                h2 {{ color: #34495e; margin-top: 40px; border-left: 4px solid #3498db; padding-left: 15px; }}
                h3 {{ color: #2c3e50; margin-top: 30px; }}
                .chapter {{ margin: 30px 0; page-break-inside: avoid; }}
                .highlight {{ background-color: #ecf0f1; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .financial {{ background-color: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .quote {{ font-style: italic; color: #7f8c8d; border-left: 3px solid #95a5a6; padding-left: 15px; margin: 20px 0; }}
                .step {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                .toc {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .toc ul {{ list-style-type: none; padding-left: 0; }}
                .toc li {{ margin: 8px 0; }}
                .toc a {{ text-decoration: none; color: #3498db; }}
            </style>
        </head>
        <body>
            <h1>Complete Guide: {business_idea.get('title', 'New Business Idea')}</h1>
            <p style="text-align: center; color: #7f8c8d; font-style: italic;">
                A comprehensive guide to launching and scaling your business idea
            </p>
            
            <div class="toc">
                <h2>Table of Contents</h2>
                <ul>
                    <li><a href="#executive-summary">1. Executive Summary</a></li>
                    <li><a href="#business-overview">2. Business Overview</a></li>
                    <li><a href="#market-analysis">3. Market Analysis</a></li>
                    <li><a href="#implementation-strategy">4. Implementation Strategy</a></li>
                    <li><a href="#financial-projections">5. Financial Projections</a></li>
                    <li><a href="#risk-assessment">6. Risk Assessment</a></li>
                    <li><a href="#action-plan">7. 90-Day Action Plan</a></li>
                </ul>
            </div>
            
            <div class="chapter" id="executive-summary">
                <h2>1. Executive Summary</h2>
                <div class="highlight">
                    <h3>Business Concept</h3>
                    <p><strong>{business_idea.get('title', 'N/A')}</strong></p>
                    <p>{business_idea.get('description', 'N/A')}</p>
                </div>
                
                <div class="financial">
                    <h3>Key Financial Highlights</h3>
                    <ul>
                        <li><strong>Initial Investment:</strong> ${business_idea.get('initial_investment', 0):,.0f}</li>
                        <li><strong>3-Year Revenue Projection:</strong> ${business_idea.get('projected_revenue_year_3', 0):,.0f}</li>
                        <li><strong>ROI:</strong> {roi_analysis.get('roi_calculation', {}).get('roi_percentage', 0):.2f}%</li>
                        <li><strong>Payback Period:</strong> {roi_analysis.get('roi_calculation', {}).get('payback_period', 0):.1f} years</li>
                    </ul>
                </div>
            </div>
            
            <div class="chapter" id="business-overview">
                <h2>2. Business Overview</h2>
                
                <h3>Target Market</h3>
                <p>{business_idea.get('target_market', 'N/A')}</p>
                
                <h3>Unique Value Proposition</h3>
                <div class="quote">
                    "{business_idea.get('unique_value_proposition', 'N/A')}"
                </div>
                
                <h3>Competitive Advantages</h3>
                <ul>
                    {''.join([f'<li>{advantage}</li>' for advantage in business_idea.get('competitive_advantages', [])])}
                </ul>
                
                <h3>Revenue Streams</h3>
                <ul>
                    {''.join([f'<li>{stream}</li>' for stream in business_idea.get('revenue_streams', [])])}
                </ul>
            </div>
            
            <div class="chapter" id="market-analysis">
                <h2>3. Market Analysis</h2>
                
                <h3>Market Size and Growth</h3>
                <p>The target market for this business idea is experiencing significant growth, with increasing demand for innovative solutions.</p>
                
                <h3>Customer Segments</h3>
                <ul>
                    <li><strong>Primary Customers:</strong> {business_idea.get('target_market', 'N/A')}</li>
                    <li><strong>Secondary Customers:</strong> Related market segments with similar needs</li>
                    <li><strong>Future Expansion:</strong> Adjacent markets and international opportunities</li>
                </ul>
            </div>
            
            <div class="chapter" id="implementation-strategy">
                <h2>4. Implementation Strategy</h2>
                
                <h3>Key Resources Required</h3>
                <ul>
                    {''.join([f'<li>{resource}</li>' for resource in business_idea.get('key_resources', [])])}
                </ul>
                
                <h3>Timeline</h3>
                <p><strong>Implementation Period:</strong> {business_idea.get('timeline_months', 0)} months</p>
                
                <h3>Development Phases</h3>
                <div class="step">
                    <h4>Phase 1: Foundation (Months 1-3)</h4>
                    <ul>
                        <li>Market research and validation</li>
                        <li>Core team assembly</li>
                        <li>Initial product development</li>
                    </ul>
                </div>
                
                <div class="step">
                    <h4>Phase 2: Launch (Months 4-6)</h4>
                    <ul>
                        <li>Beta testing and refinement</li>
                        <li>Marketing campaign launch</li>
                        <li>Customer acquisition</li>
                    </ul>
                </div>
                
                <div class="step">
                    <h4>Phase 3: Scale (Months 7-12)</h4>
                    <ul>
                        <li>Market expansion</li>
                        <li>Product enhancement</li>
                        <li>Team growth</li>
                    </ul>
                </div>
            </div>
            
            <div class="chapter" id="financial-projections">
                <h2>5. Financial Projections</h2>
                
                <table>
                    <tr><th>Year</th><th>Revenue</th><th>Growth Rate</th><th>Profit Margin</th></tr>
                    <tr><td>Year 1</td><td>${business_idea.get('projected_revenue_year_1', 0):,.0f}</td><td>-</td><td>15%</td></tr>
                    <tr><td>Year 2</td><td>${business_idea.get('projected_revenue_year_2', 0):,.0f}</td><td>{(business_idea.get('projected_revenue_year_2', 0) / business_idea.get('projected_revenue_year_1', 1) - 1) * 100:.1f}%</td><td>20%</td></tr>
                    <tr><td>Year 3</td><td>${business_idea.get('projected_revenue_year_3', 0):,.0f}</td><td>{(business_idea.get('projected_revenue_year_3', 0) / business_idea.get('projected_revenue_year_2', 1) - 1) * 100:.1f}%</td><td>25%</td></tr>
                </table>
                
                <div class="financial">
                    <h3>Investment Analysis</h3>
                    <ul>
                        <li><strong>NPV:</strong> ${roi_analysis.get('dcf_model', {}).get('npv', 0):,.0f}</li>
                        <li><strong>IRR:</strong> {roi_analysis.get('dcf_model', {}).get('irr', 0):.2f}%</li>
                        <li><strong>Annualized ROI:</strong> {roi_analysis.get('roi_calculation', {}).get('annualized_roi', 0):.2f}%</li>
                    </ul>
                </div>
            </div>
            
            <div class="chapter" id="risk-assessment">
                <h2>6. Risk Assessment</h2>
                
                <h3>Risk Level: {business_idea.get('risk_level', 'N/A').title()}</h3>
                
                <h3>Key Risks and Mitigation Strategies</h3>
                <ul>
                    <li><strong>Market Risk:</strong> Diversify customer base and revenue streams</li>
                    <li><strong>Technology Risk:</strong> Invest in robust infrastructure and security</li>
                    <li><strong>Competition Risk:</strong> Maintain competitive advantages and innovation</li>
                    <li><strong>Financial Risk:</strong> Maintain adequate cash reserves and monitor cash flow</li>
                </ul>
                
                <h3>Scalability Potential: {business_idea.get('scalability_potential', 'N/A').title()}</h3>
                <p>This business model demonstrates strong scalability potential through technology leverage and market expansion opportunities.</p>
            </div>
            
            <div class="chapter" id="action-plan">
                <h2>7. 90-Day Action Plan</h2>
                
                <h3>Week 1-2: Foundation</h3>
                <div class="step">
                    <ul>
                        <li>Conduct detailed market research</li>
                        <li>Validate business concept with potential customers</li>
                        <li>Assemble core team and advisors</li>
                        <li>Secure initial funding or resources</li>
                    </ul>
                </div>
                
                <h3>Week 3-6: Development</h3>
                <div class="step">
                    <ul>
                        <li>Develop minimum viable product (MVP)</li>
                        <li>Create marketing materials and website</li>
                        <li>Establish legal and business structure</li>
                        <li>Begin customer outreach and testing</li>
                    </ul>
                </div>
                
                <h3>Week 7-12: Launch Preparation</h3>
                <div class="step">
                    <ul>
                        <li>Refine product based on feedback</li>
                        <li>Launch marketing campaigns</li>
                        <li>Establish partnerships and distribution channels</li>
                        <li>Prepare for full market launch</li>
                    </ul>
                </div>
                
                <div class="highlight">
                    <h3>Success Metrics</h3>
                    <ul>
                        <li>Customer acquisition rate</li>
                        <li>Revenue growth month-over-month</li>
                        <li>Customer satisfaction scores</li>
                        <li>Market share expansion</li>
                    </ul>
                </div>
            </div>
            
            <div style="margin-top: 50px; text-align: center; color: #7f8c8d;">
                <p><strong>Generated on:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p>This guide is part of the CK Empire Builder system - Automated Business Intelligence</p>
            </div>
        </body>
        </html>
        """
        return html

    async def _generate_youtube_promotion_link(self, business_idea: Dict[str, Any]) -> str:
        """Generate a mock YouTube promotion link for the business idea"""
        try:
            # Create a mock YouTube video ID
            video_id = f"biz_{business_idea.get('title', 'idea').replace(' ', '_').lower()}_{datetime.utcnow().strftime('%Y%m%d')}"
            
            # Generate YouTube URL
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Create mock video details
            video_details = {
                "title": f"Complete Guide: {business_idea.get('title', 'New Business Idea')}",
                "description": f"Learn how to launch and scale {business_idea.get('title', 'this business idea')}. This comprehensive guide covers everything from market research to implementation strategy.",
                "duration": "15:30",
                "views": 12500,
                "likes": 890,
                "comments": 156,
                "upload_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "url": youtube_url
            }
            
            logger.info(f"YouTube promotion link generated: {youtube_url}")
            return youtube_url
            
        except Exception as e:
            logger.error(f"Error generating YouTube promotion link: {e}")
            return "https://www.youtube.com/watch?v=example"

    async def _generate_social_media_content(self, business_idea: Dict[str, Any]) -> Dict[str, Any]:
        """Generate social media content for the business idea"""
        try:
            # Generate content for different platforms
            content = {
                "linkedin": {
                    "title": f"🚀 New Business Opportunity: {business_idea.get('title', 'Innovative Business Idea')}",
                    "content": f"Excited to share this innovative business concept that could revolutionize {business_idea.get('target_market', 'the market')}. Key highlights:\n\n✅ {business_idea.get('unique_value_proposition', 'Unique value proposition')}\n✅ ROI: {business_idea.get('projected_revenue_year_3', 0) / business_idea.get('initial_investment', 1) * 100:.1f}%\n✅ Scalable business model\n\nWhat do you think about this opportunity? #BusinessInnovation #Entrepreneurship #Startup",
                    "hashtags": ["#BusinessInnovation", "#Entrepreneurship", "#Startup", "#BusinessIdea"]
                },
                "twitter": {
                    "title": f"💡 Business Idea: {business_idea.get('title', 'Innovative Concept')}",
                    "content": f"Just discovered an amazing business opportunity!\n\n🎯 {business_idea.get('title', 'Business Idea')}\n💰 ROI: {business_idea.get('projected_revenue_year_3', 0) / business_idea.get('initial_investment', 1) * 100:.1f}%\n🚀 {business_idea.get('scalability_potential', 'High')} scalability\n\nWould you invest in this? #BusinessIdea #Startup #Innovation",
                    "hashtags": ["#BusinessIdea", "#Startup", "#Innovation", "#Entrepreneur"]
                },
                "instagram": {
                    "title": f"💼 Business Opportunity Alert!",
                    "content": f"📈 {business_idea.get('title', 'Innovative Business Idea')}\n\n🎯 Target: {business_idea.get('target_market', 'Market segment')}\n💡 Value: {business_idea.get('unique_value_proposition', 'Unique proposition')}\n💰 Potential: ${business_idea.get('projected_revenue_year_3', 0):,.0f} in 3 years\n\n#BusinessOpportunity #Entrepreneur #Innovation #StartupLife",
                    "hashtags": ["#BusinessOpportunity", "#Entrepreneur", "#Innovation", "#StartupLife"]
                }
            }
            
            logger.info(f"Social media content generated for {business_idea.get('title', 'business idea')}")
            return content
            
        except Exception as e:
            logger.error(f"Error generating social media content: {e}")
            return {}

    async def _calculate_affiliate_earnings(self, business_idea: Dict[str, Any], finance_manager) -> Dict[str, Any]:
        """Calculate affiliate earnings for the business idea"""
        try:
            # Calculate affiliate revenue potential
            base_revenue = business_idea.get('projected_revenue_year_3', 100000)
            affiliate_commission_rate = 0.15  # 15% commission
            conversion_rate = 0.03  # 3% conversion rate
            traffic_multiplier = 2.5  # Traffic from affiliate marketing
            
            # Calculate affiliate earnings
            affiliate_revenue = base_revenue * affiliate_commission_rate * conversion_rate * traffic_multiplier
            
            # Calculate different affiliate channels
            affiliate_channels = {
                "youtube_affiliate": {
                    "platform": "YouTube",
                    "commission_rate": 0.12,
                    "estimated_earnings": affiliate_revenue * 0.4,
                    "content_type": "Video tutorials and reviews",
                    "conversion_rate": 0.04
                },
                "blog_affiliate": {
                    "platform": "Blog/Website",
                    "commission_rate": 0.15,
                    "estimated_earnings": affiliate_revenue * 0.3,
                    "content_type": "Detailed guides and reviews",
                    "conversion_rate": 0.05
                },
                "social_media_affiliate": {
                    "platform": "Social Media",
                    "commission_rate": 0.10,
                    "estimated_earnings": affiliate_revenue * 0.2,
                    "content_type": "Promotional posts and stories",
                    "conversion_rate": 0.02
                },
                "email_affiliate": {
                    "platform": "Email Marketing",
                    "commission_rate": 0.18,
                    "estimated_earnings": affiliate_revenue * 0.1,
                    "content_type": "Newsletter promotions",
                    "conversion_rate": 0.06
                }
            }
            
            # Calculate total affiliate earnings
            total_affiliate_earnings = sum(channel["estimated_earnings"] for channel in affiliate_channels.values())
            
            # Calculate ROI for affiliate marketing
            affiliate_investment = base_revenue * 0.05  # 5% of revenue for affiliate marketing
            affiliate_roi = (total_affiliate_earnings - affiliate_investment) / affiliate_investment * 100 if affiliate_investment > 0 else 0
            
            return {
                "total_affiliate_earnings": total_affiliate_earnings,
                "affiliate_investment": affiliate_investment,
                "affiliate_roi": affiliate_roi,
                "channels": affiliate_channels,
                "conversion_rate": conversion_rate,
                "commission_rate": affiliate_commission_rate,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating affiliate earnings: {e}")
            return {
                "total_affiliate_earnings": 0,
                "affiliate_investment": 0,
                "affiliate_roi": 0,
                "channels": {},
                "error": str(e)
            }

    async def _track_business_analytics(self, business_idea: Dict[str, Any], roi_analysis: Dict[str, Any], mock_applications: Dict[str, Any], affiliate_earnings: Dict[str, Any]):
        """Track business idea analytics and log revenue potential"""
        try:
            # Log analytics data
            analytics_data = {
                "business_idea_id": business_idea.get("title", "unknown").replace(" ", "_").lower(),
                "idea_title": business_idea.get("title", "Unknown"),
                "initial_investment": business_idea.get("initial_investment", 0),
                "projected_revenue_year_3": business_idea.get("projected_revenue_year_3", 0),
                "roi_percentage": roi_analysis.get("roi_calculation", {}).get("roi_percentage", 0),
                "npv": roi_analysis.get("dcf_model", {}).get("npv", 0),
                "risk_level": business_idea.get("risk_level", "unknown"),
                "scalability_potential": business_idea.get("scalability_potential", "unknown"),
                "mock_applications": {
                    "ebook_generated": bool(mock_applications.get("ebook_path")),
                    "youtube_link": mock_applications.get("youtube_link", ""),
                    "social_content_generated": bool(mock_applications.get("social_media_content"))
                },
                "affiliate_earnings": affiliate_earnings.get("total_affiliate_earnings", 0),
                "affiliate_roi": affiliate_earnings.get("affiliate_roi", 0),
                "total_potential_earnings": business_idea.get("projected_revenue_year_3", 0) + affiliate_earnings.get("total_affiliate_earnings", 0),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Save to analytics file
            from pathlib import Path
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            analytics_file = data_dir / "business_ideas_analytics.json"
            
            # Load existing analytics or create new
            if analytics_file.exists():
                with open(analytics_file, 'r', encoding='utf-8') as f:
                    existing_analytics = json.load(f)
            else:
                existing_analytics = []
            
            existing_analytics.append(analytics_data)
            
            # Save updated analytics
            with open(analytics_file, 'w', encoding='utf-8') as f:
                json.dump(existing_analytics, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Business idea analytics tracked: {business_idea.get('title', 'Unknown')} - ROI: {analytics_data['roi_percentage']:.2f}% - Affiliate Earnings: ${affiliate_earnings.get('total_affiliate_earnings', 0):,.0f}")
            
        except Exception as e:
            logger.error(f"Error tracking business analytics: {e}")

    async def suggest_alternative_channels(self, original_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest alternative channels for content distribution with channel-specific adaptations
        and revenue forecasting using finance module
        
        Args:
            original_content: Original content idea with title, description, content_type
            
        Returns:
            Dictionary containing channel suggestions with adaptations and revenue forecasts
        """
        try:
            # Import finance module for revenue forecasting
            from finance import FinanceManager
            
            # Initialize finance manager
            finance_manager = FinanceManager()
            
            # Define the 5 channels with their characteristics
            channels = {
                "youtube": {
                    "name": "YouTube",
                    "optimal_length": "10-15 minutes",
                    "format": "video",
                    "content_type": "long_form_video",
                    "rpm_range": (2.0, 8.0),  # Revenue per 1000 views
                    "engagement_rate": 0.08,
                    "best_posting_time": "15:00-17:00",
                    "hashtag_limit": 15,
                    "adaptation_focus": "educational, detailed, SEO-optimized"
                },
                "tiktok": {
                    "name": "TikTok",
                    "optimal_length": "15-60 seconds",
                    "format": "short_video",
                    "content_type": "short_form_video",
                    "rpm_range": (0.5, 2.0),
                    "engagement_rate": 0.12,
                    "best_posting_time": "19:00-21:00",
                    "hashtag_limit": 5,
                    "adaptation_focus": "trending, viral, hook-based"
                },
                "instagram": {
                    "name": "Instagram",
                    "optimal_length": "30-60 seconds",
                    "format": "reel",
                    "content_type": "short_form_video",
                    "rpm_range": (1.0, 4.0),
                    "engagement_rate": 0.10,
                    "best_posting_time": "12:00-14:00",
                    "hashtag_limit": 30,
                    "adaptation_focus": "visual, aesthetic, story-driven"
                },
                "linkedin": {
                    "name": "LinkedIn",
                    "optimal_length": "1-3 minutes",
                    "format": "professional_video",
                    "content_type": "professional_content",
                    "rpm_range": (3.0, 10.0),
                    "engagement_rate": 0.06,
                    "best_posting_time": "09:00-11:00",
                    "hashtag_limit": 5,
                    "adaptation_focus": "professional, business-focused, thought leadership"
                },
                "twitter": {
                    "name": "Twitter",
                    "optimal_length": "2-3 minutes",
                    "format": "thread",
                    "content_type": "text_thread",
                    "rpm_range": (1.5, 5.0),
                    "engagement_rate": 0.09,
                    "best_posting_time": "08:00-10:00",
                    "hashtag_limit": 3,
                    "adaptation_focus": "conversational, trending, engagement-driven"
                }
            }
            
            # Generate channel-specific adaptations using Ollama
            channel_suggestions = {}
            
            for channel_key, channel_config in channels.items():
                adaptation = await self._generate_channel_adaptation(
                    original_content, channel_config
                )
                
                # Calculate revenue forecast for this channel
                revenue_forecast = await self._calculate_channel_revenue_forecast(
                    channel_config, finance_manager
                )
                
                channel_suggestions[channel_key] = {
                    "channel_name": channel_config["name"],
                    "adaptation": adaptation,
                    "revenue_forecast": revenue_forecast,
                    "channel_config": channel_config
                }
            
            # Track analytics
            await self._track_channel_suggestions_analytics(original_content, channel_suggestions)
            
            return {
                "original_content": original_content,
                "channel_suggestions": channel_suggestions,
                "total_potential_revenue": sum(
                    suggestion["revenue_forecast"]["monthly_revenue"] 
                    for suggestion in channel_suggestions.values()
                ),
                "generated_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error suggesting alternative channels: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "generated_at": datetime.utcnow().isoformat()
            }

    async def _generate_channel_adaptation(self, original_content: Dict[str, Any], channel_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate channel-specific content adaptation using Ollama"""
        try:
            import httpx
            
            prompt = f"""
            Adapt this content for {channel_config['name']}:
            
            Original Content:
            - Title: {original_content.get('title', 'Unknown')}
            - Description: {original_content.get('description', 'No description')}
            - Content Type: {original_content.get('content_type', 'video')}
            
            Channel Requirements:
            - Optimal Length: {channel_config['optimal_length']}
            - Format: {channel_config['format']}
            - Focus: {channel_config['adaptation_focus']}
            - Hashtag Limit: {channel_config['hashtag_limit']}
            - Best Posting Time: {channel_config['best_posting_time']}
            
            Provide adaptation in JSON format:
            {{
                "adapted_title": "Channel-specific title",
                "adapted_description": "Channel-optimized description",
                "content_script": "Detailed content script/structure",
                "key_hooks": ["hook1", "hook2"],
                "optimal_hashtags": ["#hashtag1", "#hashtag2"],
                "posting_strategy": "When and how to post",
                "engagement_tips": ["tip1", "tip2"],
                "estimated_views": 5000,
                "estimated_engagement_rate": 0.08
            }}
            
            Focus on making the content viral and engaging for {channel_config['name']} audience.
            """
            
            # Make request to Ollama
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama2",
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get("response", "")
                    
                    # Try to parse JSON response
                    try:
                        import json
                        adaptation = json.loads(response_text)
                        return adaptation
                    except json.JSONDecodeError:
                        # Fallback: create structured adaptation
                        return self._create_fallback_channel_adaptation(original_content, channel_config)
                else:
                    raise Exception(f"Ollama request failed with status {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error generating channel adaptation: {e}")
            return self._create_fallback_channel_adaptation(original_content, channel_config)

    def _create_fallback_channel_adaptation(self, original_content: Dict[str, Any], channel_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback channel adaptation"""
        title = original_content.get('title', 'Unknown Content')
        description = original_content.get('description', 'No description available')
        
        return {
            "adapted_title": f"{title} - {channel_config['name']} Version",
            "adapted_description": f"{description} Optimized for {channel_config['name']}",
            "content_script": f"Adapt {title} for {channel_config['format']} format with {channel_config['optimal_length']} duration",
            "key_hooks": [f"Optimized for {channel_config['name']} audience", "Engaging opening"],
            "optimal_hashtags": [f"#{channel_config['name'].lower()}", "#content", "#viral"],
            "posting_strategy": f"Post at {channel_config['best_posting_time']} for maximum engagement",
            "engagement_tips": ["Use trending hashtags", "Engage with comments"],
            "estimated_views": 3000,
            "estimated_engagement_rate": channel_config["engagement_rate"]
        }

    async def _calculate_channel_revenue_forecast(self, channel_config: Dict[str, Any], finance_manager) -> Dict[str, Any]:
        """Calculate revenue forecast for a specific channel"""
        try:
            # Get RPM range for the channel
            min_rpm, max_rpm = channel_config["rpm_range"]
            avg_rpm = (min_rpm + max_rpm) / 2
            
            # Estimate views based on channel characteristics
            estimated_views = 5000  # Base estimate
            engagement_rate = channel_config["engagement_rate"]
            
            # Calculate monthly revenue
            monthly_views = estimated_views * 30  # Assuming daily posting
            monthly_revenue = (monthly_views / 1000) * avg_rpm
            
            # Calculate yearly projections
            yearly_revenue = monthly_revenue * 12
            growth_rate = 0.15  # 15% monthly growth
            
            # Create financial projections
            monthly_projections = []
            for month in range(1, 13):
                month_views = estimated_views * (1 + growth_rate) ** (month - 1) * 30
                month_revenue = (month_views / 1000) * avg_rpm
                monthly_projections.append({
                    "month": month,
                    "views": int(month_views),
                    "revenue": round(month_revenue, 2),
                    "growth_rate": round(growth_rate * 100, 1)
                })
            
            # Calculate ROI metrics
            roi_calc = finance_manager.calculate_roi_for_target(
                target_amount=yearly_revenue,
                initial_investment=0,  # No initial investment for content creation
                time_period=1.0
            )
            
            return {
                "monthly_revenue": round(monthly_revenue, 2),
                "yearly_revenue": round(yearly_revenue, 2),
                "avg_rpm": round(avg_rpm, 2),
                "estimated_views_per_month": monthly_views,
                "engagement_rate": engagement_rate,
                "monthly_projections": monthly_projections,
                "roi_percentage": roi_calc.calculate_roi(),
                "payback_period": roi_calc.calculate_payback_period()
            }
            
        except Exception as e:
            logger.error(f"Error calculating channel revenue forecast: {e}")
            return {
                "monthly_revenue": 0,
                "yearly_revenue": 0,
                "avg_rpm": 0,
                "estimated_views_per_month": 0,
                "engagement_rate": 0,
                "monthly_projections": [],
                "roi_percentage": 0,
                "payback_period": 0
            }

    async def _track_channel_suggestions_analytics(self, original_content: Dict[str, Any], channel_suggestions: Dict[str, Any]):
        """Track channel suggestions analytics"""
        try:
            analytics_data = {
                "content_id": original_content.get("title", "unknown").replace(" ", "_").lower(),
                "original_title": original_content.get("title", "Unknown"),
                "total_channels": len(channel_suggestions),
                "total_potential_revenue": sum(
                    suggestion["revenue_forecast"]["monthly_revenue"] 
                    for suggestion in channel_suggestions.values()
                ),
                "channel_breakdown": {
                    channel: {
                        "revenue": suggestion["revenue_forecast"]["monthly_revenue"],
                        "views": suggestion["revenue_forecast"]["estimated_views_per_month"],
                        "engagement_rate": suggestion["revenue_forecast"]["engagement_rate"]
                    }
                    for channel, suggestion in channel_suggestions.items()
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Save to analytics file
            from pathlib import Path
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            analytics_file = data_dir / "channel_suggestions_analytics.json"
            
            # Load existing analytics or create new
            if analytics_file.exists():
                with open(analytics_file, 'r', encoding='utf-8') as f:
                    existing_analytics = json.load(f)
            else:
                existing_analytics = []
            
            existing_analytics.append(analytics_data)
            
            # Save updated analytics
            with open(analytics_file, 'w', encoding='utf-8') as f:
                json.dump(existing_analytics, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Channel suggestions analytics tracked: {original_content.get('title', 'Unknown')} - Revenue: ${analytics_data['total_potential_revenue']:.2f}")
            
        except Exception as e:
            logger.error(f"Error tracking channel suggestions analytics: {e}")

    async def generate_monetization_for_channels(self, channels: List[str]) -> Dict[str, Any]:
        """
        Generate monetization strategies for multiple channels using AI and finance calculations
        
        Args:
            channels: List of channel names (YouTube, TikTok, Instagram, LinkedIn, Twitter)
            
        Returns:
            Dictionary containing monetization strategies, revenue forecasts, and recommendations
        """
        try:
            logger.info(f"🎯 Generating monetization strategies for {len(channels)} channels...")
            
            # Import finance module for calculations
            from finance import finance_manager
            
            # Generate channel-specific monetization suggestions using Ollama
            monetization_suggestions = await self._generate_channel_monetization_suggestions(channels)
            
            # Calculate digital income using finance module
            digital_income_analysis = finance_manager.calculate_max_digital_income(
                channels=channels,
                monthly_views_per_channel=monetization_suggestions.get("monthly_views", {}),
                rpm_rates=monetization_suggestions.get("rpm_rates", {}),
                affiliate_rates=monetization_suggestions.get("affiliate_rates", {}),
                product_margins=monetization_suggestions.get("product_margins", {})
            )
            
            # Combine AI suggestions with financial analysis
            result = {
                "status": "success",
                "channels": channels,
                "monetization_suggestions": monetization_suggestions,
                "financial_analysis": digital_income_analysis,
                "total_potential_revenue": digital_income_analysis["total_revenue"],
                "monthly_forecast": digital_income_analysis["monthly_forecast"],
                "yearly_forecast": digital_income_analysis["yearly_forecast"],
                "roi_analysis": digital_income_analysis["roi_analysis"],
                "recommendations": digital_income_analysis["recommendations"]
            }
            
            # Track analytics
            await self._track_monetization_analytics(channels, result)
            
            logger.info(f"✅ Generated monetization strategies - Total potential revenue: ${result['total_potential_revenue']:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating monetization for channels: {e}")
            return {
                "status": "error",
                "error": str(e),
                "channels": channels,
                "total_potential_revenue": 0
            }
    
    async def _generate_channel_monetization_suggestions(self, channels: List[str]) -> Dict[str, Any]:
        """Generate channel-specific monetization suggestions using Ollama"""
        try:
            # Create prompt for Ollama
            prompt = f"""
            Generate monetization strategies for the following social media channels: {', '.join(channels)}
            
            For each channel, provide:
            1. Monthly view estimates
            2. Recommended RPM (Revenue Per Mille) rates
            3. Affiliate commission rates
            4. Product margin percentages
            5. Specific monetization strategies (e.g., TikTok Shop, YouTube Premium, Instagram Shopping)
            
            Return the response as a JSON object with the following structure:
            {{
                "monthly_views": {{
                    "YouTube": 50000,
                    "TikTok": 100000,
                    "Instagram": 75000,
                    "LinkedIn": 25000,
                    "Twitter": 30000
                }},
                "rpm_rates": {{
                    "YouTube": 3.50,
                    "TikTok": 2.00,
                    "Instagram": 4.00,
                    "LinkedIn": 8.00,
                    "Twitter": 2.50
                }},
                "affiliate_rates": {{
                    "YouTube": 0.15,
                    "TikTok": 0.10,
                    "Instagram": 0.12,
                    "LinkedIn": 0.20,
                    "Twitter": 0.08
                }},
                "product_margins": {{
                    "YouTube": 0.25,
                    "TikTok": 0.20,
                    "Instagram": 0.30,
                    "LinkedIn": 0.35,
                    "Twitter": 0.18
                }},
                "monetization_strategies": {{
                    "YouTube": ["AdSense", "Sponsorships", "Memberships", "Merchandise"],
                    "TikTok": ["TikTok Shop", "Live Gifts", "Brand Partnerships", "Affiliate Links"],
                    "Instagram": ["Instagram Shopping", "Sponsored Posts", "IGTV Ads", "Affiliate Marketing"],
                    "LinkedIn": ["Sponsored Content", "Premium Subscriptions", "B2B Services", "Consulting"],
                    "Twitter": ["Promoted Tweets", "Twitter Spaces", "Newsletter Subscriptions", "Digital Products"]
                }}
            }}
            """
            
            # Call Ollama
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3.2",
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    response_text = response_data.get("response", "")
                    
                    # Try to parse JSON response
                    try:
                        import json
                        suggestions = json.loads(response_text)
                        return suggestions
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse Ollama response as JSON, using fallback")
                        return self._create_fallback_monetization_suggestions(channels)
                else:
                    logger.warning("Ollama request failed, using fallback")
                    return self._create_fallback_monetization_suggestions(channels)
                    
        except Exception as e:
            logger.error(f"Error generating channel monetization suggestions: {e}")
            return self._create_fallback_monetization_suggestions(channels)
    
    def _create_fallback_monetization_suggestions(self, channels: List[str]) -> Dict[str, Any]:
        """Create fallback monetization suggestions when Ollama fails"""
        default_suggestions = {
            "monthly_views": {
                "YouTube": 50000,
                "TikTok": 100000,
                "Instagram": 75000,
                "LinkedIn": 25000,
                "Twitter": 30000
            },
            "rpm_rates": {
                "YouTube": 3.50,
                "TikTok": 2.00,
                "Instagram": 4.00,
                "LinkedIn": 8.00,
                "Twitter": 2.50
            },
            "affiliate_rates": {
                "YouTube": 0.15,
                "TikTok": 0.10,
                "Instagram": 0.12,
                "LinkedIn": 0.20,
                "Twitter": 0.08
            },
            "product_margins": {
                "YouTube": 0.25,
                "TikTok": 0.20,
                "Instagram": 0.30,
                "LinkedIn": 0.35,
                "Twitter": 0.18
            },
            "monetization_strategies": {
                "YouTube": ["AdSense", "Sponsorships", "Memberships", "Merchandise"],
                "TikTok": ["TikTok Shop", "Live Gifts", "Brand Partnerships", "Affiliate Links"],
                "Instagram": ["Instagram Shopping", "Sponsored Posts", "IGTV Ads", "Affiliate Marketing"],
                "LinkedIn": ["Sponsored Content", "Premium Subscriptions", "B2B Services", "Consulting"],
                "Twitter": ["Promoted Tweets", "Twitter Spaces", "Newsletter Subscriptions", "Digital Products"]
            }
        }
        
        # Filter for requested channels only
        filtered_suggestions = {}
        for key, value in default_suggestions.items():
            if isinstance(value, dict):
                filtered_suggestions[key] = {channel: value.get(channel, 0) for channel in channels}
            else:
                filtered_suggestions[key] = value
        
        return filtered_suggestions
    
    async def _track_monetization_analytics(self, channels: List[str], result: Dict[str, Any]):
        """Track monetization analytics"""
        try:
            analytics_data = {
                "channels": channels,
                "total_potential_revenue": result.get("total_potential_revenue", 0),
                "monthly_revenue": result.get("financial_analysis", {}).get("total_revenue", 0),
                "yearly_revenue": result.get("yearly_forecast", {}).get("total_revenue", 0),
                "roi_percentage": result.get("roi_analysis", {}).get("roi_percentage", 0),
                "channel_breakdown": result.get("financial_analysis", {}).get("channel_breakdown", {}),
                "recommendations": result.get("recommendations", []),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Save to CSV file for tracking
            from pathlib import Path
            import csv
            
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            csv_file = data_dir / "monetization_analytics.csv"
            
            # Check if file exists to determine if we need to write headers
            file_exists = csv_file.exists()
            
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write headers if file is new
                if not file_exists:
                    writer.writerow([
                        "Date", "Channels", "Total_Potential_Revenue", "Monthly_Revenue", 
                        "Yearly_Revenue", "ROI_Percentage", "Channel_Breakdown", "Recommendations"
                    ])
                
                # Write data row
                writer.writerow([
                    analytics_data["generated_at"],
                    ",".join(channels),
                    analytics_data["total_potential_revenue"],
                    analytics_data["monthly_revenue"],
                    analytics_data["yearly_revenue"],
                    analytics_data["roi_percentage"],
                    str(analytics_data["channel_breakdown"]),
                    "|".join(analytics_data["recommendations"])
                ])
            
            logger.info(f"Monetization analytics tracked to CSV: {csv_file}")
            
        except Exception as e:
            logger.error(f"Error tracking monetization analytics: {e}")

    async def generate_niche_content_ideas(self, niche: str, channels: int = 5) -> List[ContentIdea]:
        """
        Generate niche-specific content ideas with educational, viral, and lifestyle variations.
        
        Args:
            niche: The specific niche/topic to generate content for
            channels: Number of content variations to generate (default: 5)
            
        Returns:
            List of ContentIdea objects with niche-specific content
        """
        try:
            logger.info(f"🎯 Generating niche content ideas for: {niche}")
            
            # 2025 trends to include in prompts
            trends_2025 = [
                "AI-powered personalization", "Short-form video dominance", 
                "Authentic storytelling", "Community-driven content", "Educational entertainment",
                "Sustainability focus", "Mental health awareness", "Remote work lifestyle",
                "Digital nomad culture", "Micro-influencer partnerships", "Voice-first content",
                "AR/VR integration", "Podcast resurgence", "Newsletter renaissance",
                "Live streaming growth", "User-generated content", "Collaborative content",
                "Data-driven storytelling", "Cross-platform narratives", "Interactive content"
            ]
            
            # Content variation types
            variation_types = ["educational", "viral", "lifestyle"]
            
            # Generate content ideas using Ollama
            content_ideas = []
            
            for i in range(channels):
                variation_type = variation_types[i % len(variation_types)]
                
                prompt = f"""
Generate a {variation_type} content idea for the niche: "{niche}"

Requirements:
- Content type: {variation_type}
- Niche: {niche}
- Must be engaging and shareable
- Include 2025 trends: {', '.join(trends_2025[:5])}
- Target audience: {niche} enthusiasts and general audience
- Viral potential: High
- Revenue potential: Medium to High

Format the response as JSON:
{{
    "title": "Engaging title",
    "description": "Detailed description",
    "content_type": "video|article|social_media|podcast",
    "target_audience": "Specific audience",
    "viral_potential": 0.0-1.0,
    "estimated_revenue": 0.0,
    "keywords": ["keyword1", "keyword2"],
    "hashtags": ["#hashtag1", "#hashtag2"],
    "variation_type": "{variation_type}",
    "niche_focus": "{niche}",
    "trends_included": ["trend1", "trend2"]
}}
"""
                
                try:
                    # Try Ollama first
                    response = await self._generate_with_ollama_niche(prompt, niche, variation_type)
                    if response:
                        content_idea = self._parse_niche_content_idea(response, niche, variation_type)
                        if content_idea:
                            content_ideas.append(content_idea)
                            logger.info(f"✅ Generated {variation_type} content for {niche}")
                        else:
                            # Fallback to mock content
                            content_idea = self._create_mock_niche_content(niche, variation_type, i)
                            content_ideas.append(content_idea)
                            logger.info(f"📝 Created mock {variation_type} content for {niche}")
                    else:
                        # Fallback to mock content
                        content_idea = self._create_mock_niche_content(niche, variation_type, i)
                        content_ideas.append(content_idea)
                        logger.info(f"📝 Created mock {variation_type} content for {niche}")
                        
                except Exception as e:
                    logger.error(f"Error generating {variation_type} content for {niche}: {e}")
                    # Fallback to mock content
                    content_idea = self._create_mock_niche_content(niche, variation_type, i)
                    content_ideas.append(content_idea)
                    logger.info(f"📝 Created fallback {variation_type} content for {niche}")
            
            # Track niche content analytics
            await self._track_niche_content_analytics(niche, content_ideas)
            
            logger.info(f"🎯 Generated {len(content_ideas)} niche content ideas for {niche}")
            return content_ideas
            
        except Exception as e:
            logger.error(f"Error generating niche content ideas: {e}")
            return []

    async def _generate_with_ollama_niche(self, prompt: str, niche: str, variation_type: str) -> Optional[str]:
        """Generate niche content using Ollama with 2025 trends"""
        try:
            import httpx
            
            # Enhanced prompt with 2025 trends
            enhanced_prompt = f"""
{prompt}

2025 TREND OPTIMIZATION:
- Short-form content (15-60 seconds) for maximum engagement
- Multi-channel adaptability (YouTube, TikTok, Instagram, LinkedIn, Twitter)
- AI-enhanced creative elements and automation
- Authentic storytelling with personal touch
- Educational value even in entertainment content
- Community engagement and interaction focus
- Sustainability and social impact considerations
- Data-driven content optimization
- Cross-platform hashtag strategy
- Long-term audience building approach

CONTENT ADAPTATION FOR {variation_type.upper()}:
- Educational: Focus on knowledge sharing and skill development
- Viral: Emphasize shareable, trending elements with high engagement
- Lifestyle: Include personal journey and relatable experiences

RESPONSE FORMAT: JSON with title, description, viral_potential, engagement_metrics, platform_optimization, and hashtags.
"""
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3.2",
                        "prompt": enhanced_prompt,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    logger.warning(f"Ollama request failed for niche {niche}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling Ollama for niche content: {e}")
            return None

    def _parse_niche_content_idea(self, response_text: str, niche: str, variation_type: str) -> Optional[ContentIdea]:
        """Parse niche content idea from Ollama response"""
        try:
            # Extract JSON from response
            import re
            import json
            
            # Find JSON in response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                # Create ContentIdea object
                content_type = ContentType.VIDEO if data.get("content_type") == "video" else ContentType.SOCIAL_MEDIA
                
                return ContentIdea(
                    title=data.get("title", f"{variation_type.title()} {niche} Content"),
                    description=data.get("description", f"Engaging {variation_type} content about {niche}"),
                    content_type=content_type,
                    target_audience=data.get("target_audience", f"{niche} enthusiasts"),
                    viral_potential=float(data.get("viral_potential", 0.7)),
                    estimated_revenue=float(data.get("estimated_revenue", 50.0)),
                    keywords=data.get("keywords", [niche, variation_type, "2025"]),
                    hashtags=data.get("hashtags", [f"#{niche}", f"#{variation_type}", "#2025"])
                )
            else:
                logger.warning(f"Could not parse JSON from niche content response: {response_text[:100]}...")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing niche content idea: {e}")
            return None

    def _create_mock_niche_content(self, niche: str, variation_type: str, index: int) -> ContentIdea:
        """Create mock niche content when Ollama is unavailable"""
        
        # Mock content templates based on variation type
        templates = {
            "educational": {
                "titles": [
                    f"Complete Guide to {niche} in 2025",
                    f"5 Essential {niche} Tips Everyone Should Know",
                    f"The Science Behind {niche} Success",
                    f"Mastering {niche}: From Beginner to Expert",
                    f"2025 {niche} Trends You Can't Ignore"
                ],
                "descriptions": [
                    f"Learn everything about {niche} with this comprehensive guide",
                    f"Discover the latest {niche} techniques and strategies",
                    f"Expert insights on {niche} best practices",
                    f"Step-by-step tutorial for {niche} mastery",
                    f"Future-proof your {niche} knowledge"
                ]
            },
            "viral": {
                "titles": [
                    f"Mind-Blowing {niche} Hack That Went Viral",
                    f"The {niche} Secret Nobody Talks About",
                    f"5 {niche} Mistakes That Will Shock You",
                    f"This {niche} Trick Changed Everything",
                    f"The Truth About {niche} That Will Blow Your Mind"
                ],
                "descriptions": [
                    f"Viral {niche} content that will amaze your audience",
                    f"Shocking revelations about {niche} that went viral",
                    f"Controversial {niche} facts that will surprise you",
                    f"Amazing {niche} discovery that's taking over social media",
                    f"Viral {niche} hack that everyone needs to see"
                ]
            },
            "lifestyle": {
                "titles": [
                    f"My {niche} Journey: A Day in the Life",
                    f"How {niche} Changed My Life Forever",
                    f"The {niche} Lifestyle: What It's Really Like",
                    f"Living the {niche} Dream: Behind the Scenes",
                    f"From Zero to {niche} Hero: My Story"
                ],
                "descriptions": [
                    f"Personal story about embracing the {niche} lifestyle",
                    f"Real-life experience with {niche} transformation",
                    f"Lifestyle changes that came with {niche}",
                    f"Day-to-day reality of living with {niche}",
                    f"Inspirational journey through {niche} adoption"
                ]
            }
        }
        
        template = templates.get(variation_type, templates["educational"])
        title = template["titles"][index % len(template["titles"])]
        description = template["descriptions"][index % len(template["descriptions"])]
        
        return ContentIdea(
            title=title,
            description=description,
            content_type=ContentType.VIDEO,
            target_audience=f"{niche} enthusiasts and {variation_type} content lovers",
            viral_potential=0.6 + (index * 0.1),  # Varying viral potential
            estimated_revenue=30.0 + (index * 10.0),  # Varying revenue potential
            keywords=[niche, variation_type, "2025", "trending", "viral"],
            hashtags=[f"#{niche}", f"#{variation_type}", "#2025", "#trending", "#viral"]
        )

    async def _track_niche_content_analytics(self, niche: str, content_ideas: List[ContentIdea]):
        """Track niche content analytics"""
        try:
            analytics_data = {
                "niche": niche,
                "total_ideas": len(content_ideas),
                "variation_types": {},
                "average_viral_potential": 0.0,
                "total_estimated_revenue": 0.0,
                "content_types": {},
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Calculate analytics
            total_viral_potential = 0.0
            total_revenue = 0.0
            
            for idea in content_ideas:
                total_viral_potential += idea.viral_potential
                total_revenue += idea.estimated_revenue
                
                # Count variation types (extract from title/description)
                variation_type = "educational"  # default
                if "viral" in idea.title.lower() or "shock" in idea.title.lower():
                    variation_type = "viral"
                elif "lifestyle" in idea.title.lower() or "journey" in idea.title.lower():
                    variation_type = "lifestyle"
                
                analytics_data["variation_types"][variation_type] = analytics_data["variation_types"].get(variation_type, 0) + 1
                analytics_data["content_types"][idea.content_type.value] = analytics_data["content_types"].get(idea.content_type.value, 0) + 1
            
            if content_ideas:
                analytics_data["average_viral_potential"] = total_viral_potential / len(content_ideas)
                analytics_data["total_estimated_revenue"] = total_revenue
            
            # Save to CSV file
            from pathlib import Path
            import csv
            
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            csv_file = data_dir / "niche_content_analytics.csv"
            
            # Check if file exists to determine if we need to write headers
            file_exists = csv_file.exists()
            
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write headers if file is new
                if not file_exists:
                    writer.writerow([
                        "Date", "Niche", "Total_Ideas", "Average_Viral_Potential", 
                        "Total_Estimated_Revenue", "Variation_Types", "Content_Types"
                    ])
                
                # Write data row
                writer.writerow([
                    analytics_data["generated_at"],
                    analytics_data["niche"],
                    analytics_data["total_ideas"],
                    analytics_data["average_viral_potential"],
                    analytics_data["total_estimated_revenue"],
                    str(analytics_data["variation_types"]),
                    str(analytics_data["content_types"])
                ])
            
            logger.info(f"Niche content analytics tracked to CSV: {csv_file}")
            
        except Exception as e:
            logger.error(f"Error tracking niche content analytics: {e}")

    # Keep existing methods for backward compatibility
    async def generate_empire_strategy(self, user_input: str) -> EmpireStrategy:
        """Backward compatibility method"""
        strategy, _ = await self.generate_custom_strategy(user_input, include_financial_metrics=False)
        return strategy

    async def create_fine_tuning_dataset(self) -> FineTuningDataset:
        """Backward compatibility method"""
        return await self.create_enhanced_fine_tuning_dataset()

    async def start_fine_tuning(self, dataset: FineTuningDataset) -> str:
        """Backward compatibility method"""
        return await self.start_enhanced_fine_tuning(dataset)

    def _calculate_financial_metrics(self, strategy: EmpireStrategy) -> FinancialMetrics:
        """Backward compatibility method"""
        return self._calculate_enhanced_financial_metrics(strategy)

    def _initialize_2025_trends(self) -> List[TrendData]:
        """Initialize 2025 trend data for content optimization"""
        return [
            TrendData(
                trend_name="Short-Form Video Dominance",
                category="Video Content",
                impact_score=0.95,
                audience_reach="Gen Z and Millennials",
                content_adaptation="15-60 second vertical videos",
                viral_potential=0.9,
                revenue_potential=0.85,
                platform_optimization=["TikTok", "Instagram Reels", "YouTube Shorts"],
                hashtags=["#shorts", "#viral", "#trending", "#fyp"],
                keywords=["short-form", "vertical", "viral", "trending"]
            ),
            TrendData(
                trend_name="Multi-Channel Content Strategy",
                category="Distribution",
                impact_score=0.88,
                audience_reach="Cross-platform audiences",
                content_adaptation="Platform-specific adaptations",
                viral_potential=0.8,
                revenue_potential=0.9,
                platform_optimization=["YouTube", "TikTok", "Instagram", "LinkedIn", "Twitter"],
                hashtags=["#multichannel", "#contentstrategy", "#crossplatform"],
                keywords=["multi-channel", "cross-platform", "content strategy"]
            ),
            TrendData(
                trend_name="AI-Generated Content",
                category="Technology",
                impact_score=0.92,
                audience_reach="Tech-savvy audiences",
                content_adaptation="AI-enhanced creative content",
                viral_potential=0.85,
                revenue_potential=0.8,
                platform_optimization=["All platforms"],
                hashtags=["#ai", "#aiart", "#aigenerated", "#future"],
                keywords=["AI", "artificial intelligence", "generative", "automation"]
            ),
            TrendData(
                trend_name="Authentic Storytelling",
                category="Content Style",
                impact_score=0.87,
                audience_reach="All demographics",
                content_adaptation="Personal, relatable narratives",
                viral_potential=0.75,
                revenue_potential=0.85,
                platform_optimization=["All platforms"],
                hashtags=["#authentic", "#storytelling", "#real", "#genuine"],
                keywords=["authentic", "storytelling", "personal", "relatable"]
            ),
            TrendData(
                trend_name="Educational Entertainment",
                category="Content Type",
                impact_score=0.83,
                audience_reach="Lifelong learners",
                content_adaptation="Edutainment content",
                viral_potential=0.7,
                revenue_potential=0.8,
                platform_optimization=["YouTube", "TikTok", "LinkedIn"],
                hashtags=["#edutainment", "#learn", "#education", "#knowledge"],
                keywords=["educational", "learning", "knowledge", "informative"]
            )
        ]

    def _load_performance_data(self):
        """Load performance data from file"""
        try:
            performance_file = Path("data/content_performance_analytics.csv")
            if performance_file.exists():
                import csv
                with open(performance_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        performance = ContentPerformance(
                            content_id=row.get('content_id', ''),
                            title=row.get('title', ''),
                            content_type=ContentType(row.get('content_type', 'video')),
                            views=int(row.get('views', 0)),
                            engagement_rate=float(row.get('engagement_rate', 0.0)),
                            revenue_generated=float(row.get('revenue_generated', 0.0)),
                            viral_potential=float(row.get('viral_potential', 0.0)),
                            quality_score=float(row.get('quality_score', 0.0)),
                            improvement_suggestions=row.get('improvement_suggestions', '').split('|') if row.get('improvement_suggestions') else []
                        )
                        self.performance_data.append(performance)
                logger.info(f"Loaded {len(self.performance_data)} performance records")
        except Exception as e:
            logger.error(f"Error loading performance data: {e}")

    def _save_performance_data(self):
        """Save performance data to file"""
        try:
            performance_file = Path("data/content_performance_analytics.csv")
            import csv
            with open(performance_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'content_id', 'title', 'content_type', 'views', 'engagement_rate',
                    'revenue_generated', 'viral_potential', 'quality_score', 'improvement_suggestions'
                ])
                writer.writeheader()
                for performance in self.performance_data:
                    writer.writerow({
                        'content_id': performance.content_id,
                        'title': performance.title,
                        'content_type': performance.content_type.value,
                        'views': performance.views,
                        'engagement_rate': performance.engagement_rate,
                        'revenue_generated': performance.revenue_generated,
                        'viral_potential': performance.viral_potential,
                        'quality_score': performance.quality_score,
                        'improvement_suggestions': '|'.join(performance.improvement_suggestions)
                    })
            logger.info(f"Saved {len(self.performance_data)} performance records")
        except Exception as e:
            logger.error(f"Error saving performance data: {e}")

    async def _generate_optimized_prompt_with_2025_trends(self, base_prompt: str, content_type: ContentType, target_audience: str = "") -> str:
        """Generate optimized prompt with 2025 trends"""
        # Get relevant trends for content type
        relevant_trends = [trend for trend in self.trend_data if content_type.value in trend.platform_optimization]
        
        # Get low-performance improvement suggestions
        improvement_suggestions = self._get_improvement_suggestions(content_type)
        
        # Build enhanced prompt
        enhanced_prompt = f"""
{base_prompt}

2025 TREND OPTIMIZATION:
{self._format_trends_for_prompt(relevant_trends)}

PERFORMANCE IMPROVEMENTS:
{self._format_improvements_for_prompt(improvement_suggestions)}

CONTENT OPTIMIZATION GUIDELINES:
- Focus on short-form, engaging content (15-60 seconds for video)
- Include educational elements even in entertainment content
- Use authentic, relatable storytelling
- Optimize for multi-channel distribution
- Include AI-enhanced creative elements
- Emphasize community engagement and interaction
- Consider sustainability and social impact angles
- Use data-driven insights and analytics
- Focus on long-term audience building
- Include cross-platform hashtag strategies

TARGET AUDIENCE: {target_audience or "Multi-platform digital audience"}

RESPONSE FORMAT: JSON with viral_potential, engagement_metrics, and platform_optimization fields.
"""
        return enhanced_prompt

    def _format_trends_for_prompt(self, trends: List[TrendData]) -> str:
        """Format trends for prompt inclusion"""
        if not trends:
            return "No specific trends identified for this content type."
        
        trend_text = []
        for trend in trends[:3]:  # Top 3 most relevant trends
            trend_text.append(f"- {trend.trend_name}: {trend.content_adaptation} (Viral Potential: {trend.viral_potential:.2f})")
        
        return "\n".join(trend_text)

    def _format_improvements_for_prompt(self, improvements: List[str]) -> str:
        """Format improvement suggestions for prompt inclusion"""
        if not improvements:
            return "No specific improvements identified."
        
        return "\n".join([f"- {improvement}" for improvement in improvements[:5]])

    def _get_improvement_suggestions(self, content_type: ContentType) -> List[str]:
        """Get improvement suggestions based on low-performance content"""
        low_performance = [p for p in self.performance_data 
                          if p.content_type == content_type and p.quality_score < self.optimization_threshold]
        
        if not low_performance:
            return []
        
        # Analyze common issues
        common_issues = []
        for performance in low_performance:
            common_issues.extend(performance.improvement_suggestions)
        
        # Count and return most common suggestions
        from collections import Counter
        issue_counts = Counter(common_issues)
        return [issue for issue, count in issue_counts.most_common(5)]

    async def _optimize_content_with_feedback_loop(self, content_idea: ContentIdea) -> ContentIdea:
        """Optimize content using feedback loop and 2025 trends"""
        try:
            # Generate optimized prompt
            base_prompt = f"Generate content about: {content_idea.title}"
            optimized_prompt = await self._generate_optimized_prompt_with_2025_trends(
                base_prompt, content_idea.content_type, content_idea.target_audience
            )
            
            # Generate optimized content using Ollama
            optimized_response = await self._generate_with_ollama_optimized(optimized_prompt)
            
            if optimized_response:
                # Parse optimized content
                optimized_idea = self._parse_optimized_content(optimized_response, content_idea)
                return optimized_idea
            else:
                return content_idea
                
        except Exception as e:
            logger.error(f"Error optimizing content: {e}")
            return content_idea

    async def _generate_with_ollama_optimized(self, prompt: str) -> Optional[str]:
        """Generate optimized content using Ollama with 2025 trends"""
        try:
            import httpx
            
            # Enhanced prompt with 2025 optimization
            enhanced_prompt = f"""
{prompt}

ADDITIONAL 2025 OPTIMIZATION CONTEXT:
- Short-form content (15-60 seconds) for maximum engagement
- Multi-channel adaptability (YouTube, TikTok, Instagram, LinkedIn, Twitter)
- AI-enhanced creative elements and automation
- Authentic storytelling with personal touch
- Educational value even in entertainment content
- Community engagement and interaction focus
- Sustainability and social impact considerations
- Data-driven content optimization
- Cross-platform hashtag strategy
- Long-term audience building approach

RESPONSE FORMAT: JSON with title, description, viral_potential, engagement_metrics, platform_optimization, and hashtags.
"""
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3.2",
                        "prompt": enhanced_prompt,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    logger.warning(f"Ollama request failed for optimization: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling Ollama for optimization: {e}")
            return None

    def _parse_optimized_content(self, response_text: str, original_idea: ContentIdea) -> ContentIdea:
        """Parse optimized content from Ollama response"""
        try:
            import re
            import json
            
            # Find JSON in response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                # Update content idea with optimized data
                original_idea.title = data.get("title", original_idea.title)
                original_idea.description = data.get("description", original_idea.description)
                original_idea.viral_potential = float(data.get("viral_potential", original_idea.viral_potential))
                original_idea.keywords.extend(data.get("keywords", []))
                original_idea.hashtags.extend(data.get("hashtags", []))
                
                return original_idea
            else:
                logger.warning(f"Could not parse JSON from optimized response: {response_text[:100]}...")
                return original_idea
                
        except Exception as e:
            logger.error(f"Error parsing optimized content: {e}")
            return original_idea

    async def run_continuous_optimization(self):
        """Run continuous optimization loop for 24/7 operation"""
        while self.continuous_optimization:
            try:
                # Check for low-performance content
                low_performance_content = [p for p in self.performance_data 
                                         if p.quality_score < self.optimization_threshold]
                
                if low_performance_content:
                    logger.info(f"Found {len(low_performance_content)} low-performance content items for optimization")
                    
                    # Optimize each low-performance content
                    for performance in low_performance_content[:5]:  # Optimize top 5
                        await self._optimize_single_content(performance)
                
                # Update trend data periodically
                if (datetime.utcnow() - self.last_optimization).days >= 7:
                    await self._update_trend_data()
                    self.last_optimization = datetime.utcnow()
                
                # Save performance data
                self._save_performance_data()
                
                # Wait before next optimization cycle
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in continuous optimization: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes on error

    async def _optimize_single_content(self, performance: ContentPerformance):
        """Optimize a single content item"""
        try:
            # Create content idea from performance data
            content_idea = ContentIdea(
                title=performance.title,
                description=f"Optimized version of {performance.title}",
                content_type=performance.content_type,
                target_audience="Multi-platform audience",
                viral_potential=performance.viral_potential,
                estimated_revenue=performance.revenue_generated,
                keywords=["optimized", "2025", "trending"],
                hashtags=["#optimized", "#2025", "#trending"]
            )
            
            # Optimize content
            optimized_idea = await self._optimize_content_with_feedback_loop(content_idea)
            
            # Update performance data
            performance.viral_potential = optimized_idea.viral_potential
            performance.quality_score = min(1.0, performance.quality_score + 0.1)
            performance.improvement_suggestions.append("AI-optimized with 2025 trends")
            performance.last_updated = datetime.utcnow()
            
            logger.info(f"Optimized content: {performance.title}")
            
        except Exception as e:
            logger.error(f"Error optimizing single content: {e}")

    async def _update_trend_data(self):
        """Update trend data with latest 2025 insights"""
        try:
            # Generate new trend insights using Ollama
            trend_prompt = """
            Generate 5 new content trends for 2025 that are emerging or gaining momentum.
            Focus on short-form content, multi-channel strategies, AI integration, and authentic storytelling.
            
            Provide response in JSON format with trend_name, category, impact_score, content_adaptation, viral_potential, and hashtags.
            """
            
            trend_response = await self._generate_with_ollama_optimized(trend_prompt)
            
            if trend_response:
                # Parse and update trend data
                new_trends = self._parse_trend_data(trend_response)
                if new_trends:
                    self.trend_data.extend(new_trends)
                    logger.info(f"Updated trend data with {len(new_trends)} new trends")
            
        except Exception as e:
            logger.error(f"Error updating trend data: {e}")

    def _parse_trend_data(self, response_text: str) -> List[TrendData]:
        """Parse trend data from Ollama response"""
        try:
            import re
            import json
            
            # Try to find JSON array first
            json_array_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_array_match:
                json_str = json_array_match.group()
                data = json.loads(json_str)
                
                # Convert to TrendData objects
                trends = []
                if isinstance(data, list):
                    for trend_dict in data:
                        trends.append(TrendData(
                            trend_name=trend_dict.get("trend_name", ""),
                            category=trend_dict.get("category", "General"),
                            impact_score=float(trend_dict.get("impact_score", 0.7)),
                            audience_reach=trend_dict.get("audience_reach", "Multi-platform"),
                            content_adaptation=trend_dict.get("content_adaptation", ""),
                            viral_potential=float(trend_dict.get("viral_potential", 0.7)),
                            revenue_potential=float(trend_dict.get("revenue_potential", 0.7)),
                            platform_optimization=trend_dict.get("platform_optimization", ["All platforms"]),
                            hashtags=trend_dict.get("hashtags", []),
                            keywords=trend_dict.get("keywords", [])
                        ))
                
                return trends
            
            # Try to find single JSON object
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                # Convert single object to list
                if isinstance(data, dict):
                    trends = []
                    trends.append(TrendData(
                        trend_name=data.get("trend_name", ""),
                        category=data.get("category", "General"),
                        impact_score=float(data.get("impact_score", 0.7)),
                        audience_reach=data.get("audience_reach", "Multi-platform"),
                        content_adaptation=data.get("content_adaptation", ""),
                        viral_potential=float(data.get("viral_potential", 0.7)),
                        revenue_potential=float(data.get("revenue_potential", 0.7)),
                        platform_optimization=data.get("platform_optimization", ["All platforms"]),
                        hashtags=data.get("hashtags", []),
                        keywords=data.get("keywords", [])
                    ))
                    return trends
                
                return []
            else:
                logger.warning(f"Could not parse JSON from trend response: {response_text[:100]}...")
                return []
                
        except Exception as e:
            logger.error(f"Error parsing trend data: {e}")
            return []

    async def start_24_7_optimization(self):
        """Start 24/7 optimization process"""
        logger.info("🚀 Starting 24/7 AI optimization with 2025 trends...")
        
        # Start continuous optimization in background
        asyncio.create_task(self.run_continuous_optimization())
        
        logger.info("✅ 24/7 optimization started successfully")

    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status"""
        return {
            "continuous_optimization": self.continuous_optimization,
            "feedback_loop_active": self.feedback_loop_active,
            "optimization_threshold": self.optimization_threshold,
            "performance_records": len(self.performance_data),
            "trend_data_count": len(self.trend_data),
            "last_optimization": self.last_optimization.isoformat(),
            "low_performance_content": len([p for p in self.performance_data if p.quality_score < self.optimization_threshold])
        }

# Global AI module instance
ai_module = AIModule() 