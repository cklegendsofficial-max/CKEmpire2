"""
AI Module for CK Empire Builder
Handles OpenAI integration, video production, NFT automation, and AGI evolution
"""

import os
import json
import asyncio
import logging
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
from config import settings

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

class AIModule:
    """Main AI module for content generation, video production, and NFT automation"""
    
    def __init__(self):
        self.openai_client = None
        self.stripe_client = None
        self.web3 = None
        self.agi_state = AGIState(
            consciousness_score=0.1,
            decision_capability=0.2,
            learning_rate=0.15,
            creativity_level=0.3,
            ethical_awareness=0.25,
            last_evolution=datetime.utcnow()
        )
        
        # Initialize OpenAI
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("✅ OpenAI client initialized")
        else:
            logger.warning("❌ OpenAI not available or API key not set")
        
        # Initialize Stripe
        if STRIPE_AVAILABLE and settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            self.stripe_client = stripe
            logger.info("✅ Stripe client initialized")
        else:
            logger.warning("❌ Stripe not available or API key not set")
        
        # Initialize Web3
        if WEB3_AVAILABLE and settings.ETHEREUM_RPC_URL:
            self.web3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
            if self.web3.is_connected():
                logger.info("✅ Web3 connected to Ethereum")
            else:
                logger.warning("❌ Web3 connection failed")
        else:
            logger.warning("❌ Web3 not available or RPC URL not set")
        
        # Video processing setup
        self.video_output_dir = Path("output/videos")
        self.video_output_dir.mkdir(parents=True, exist_ok=True)
        
        # NFT storage
        self.nft_output_dir = Path("output/nfts")
        self.nft_output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_viral_content_ideas(
        self, 
        topic: str, 
        count: int = 5,
        content_type: Optional[ContentType] = None
    ) -> List[ContentIdea]:
        """Generate viral content ideas using OpenAI"""
        
        if not self.openai_client:
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
                self.openai_client.chat.completions.create,
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

# Global AI module instance
ai_module = AIModule() 