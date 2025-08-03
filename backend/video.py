import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
from pathlib import Path

# Optional imports for video processing
try:
    import cv2
    import numpy as np
    from PIL import Image
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logging.warning("OpenCV not available. Video processing features will be limited.")

try:
    import moviepy.editor as mp
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logging.warning("MoviePy not available. Video editing features will be limited.")

# OpenAI integration
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available. AI features will be limited.")

# Web3 integration for NFT
try:
    from web3 import Web3
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    logging.warning("Web3 not available. NFT features will be limited.")

# Stripe integration
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logging.warning("Stripe not available. Payment features will be limited.")

@dataclass
class VideoStyle:
    """Video style configuration for Zack Snyder style"""
    name: str
    description: str
    color_grading: Dict[str, float]
    aspect_ratio: str
    frame_rate: int
    resolution: tuple
    effects: List[str]

@dataclass
class NFTMetadata:
    """NFT metadata structure"""
    name: str
    description: str
    image_url: str
    animation_url: Optional[str]
    attributes: List[Dict[str, Any]]
    external_url: str
    seller_fee_basis_points: int
    collection: Dict[str, str]

@dataclass
class PricingPrediction:
    """AI-powered pricing prediction"""
    predicted_price: float
    confidence: float
    factors: List[str]
    market_analysis: Dict[str, Any]
    recommendation: str

class VideoProductionManager:
    """Manages AI-powered video production with Zack Snyder style"""
    
    def __init__(self):
        self.openai_client = None
        self.stripe_client = None
        self.web3_client = None
        self.setup_clients()
        
        # Zack Snyder style configurations
        self.zack_snyder_style = VideoStyle(
            name="Zack Snyder Style",
            description="Dark, cinematic, high contrast with slow motion",
            color_grading={
                "contrast": 1.3,
                "saturation": 0.8,
                "brightness": 0.9,
                "gamma": 1.1
            },
            aspect_ratio="2.35:1",
            frame_rate=24,
            resolution=(1920, 1080),
            effects=["slow_motion", "dark_contrast", "cinematic_lighting"]
        )
        
        self.video_styles = {
            "zack_snyder": self.zack_snyder_style,
            "action": VideoStyle("Action", "Fast-paced action sequences", {}, "16:9", 30, (1920, 1080), ["fast_cuts", "dynamic_lighting"]),
            "dramatic": VideoStyle("Dramatic", "Emotional storytelling", {}, "2.35:1", 24, (1920, 1080), ["close_ups", "emotional_lighting"])
        }
    
    def setup_clients(self):
        """Setup external service clients"""
        # OpenAI setup
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
            else:
                logging.warning("OPENAI_API_KEY not set")
        
        # Stripe setup
        if STRIPE_AVAILABLE:
            stripe_key = os.getenv("STRIPE_SECRET_KEY")
            if stripe_key:
                self.stripe_client = stripe
                stripe.api_key = stripe_key
            else:
                logging.warning("STRIPE_SECRET_KEY not set")
        
        # Web3 setup
        if WEB3_AVAILABLE:
            web3_url = os.getenv("WEB3_PROVIDER_URL")
            if web3_url:
                self.web3_client = Web3(Web3.HTTPProvider(web3_url))
            else:
                logging.warning("WEB3_PROVIDER_URL not set")
    
    async def generate_video_prompt(self, theme: str, duration: int, style: str = "zack_snyder") -> str:
        """Generate AI prompt for video production"""
        if not self.openai_client:
            return self._generate_mock_prompt(theme, duration, style)
        
        try:
            style_config = self.video_styles.get(style, self.zack_snyder_style)
            
            prompt = f"""
            Create a {duration}-second video in {style_config.name} style with the theme: "{theme}"
            
            Style requirements:
            - Aspect ratio: {style_config.aspect_ratio}
            - Frame rate: {style_config.frame_rate} fps
            - Resolution: {style_config.resolution[0]}x{style_config.resolution[1]}
            - Effects: {', '.join(style_config.effects)}
            - Color grading: {style_config.color_grading}
            
            Generate a detailed video production script with:
            1. Scene breakdown
            2. Camera movements
            3. Lighting setup
            4. Color grading instructions
            5. Music/sound recommendations
            """
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional video director specializing in cinematic production."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error generating video prompt: {e}")
            return self._generate_mock_prompt(theme, duration, style)
    
    def _generate_mock_prompt(self, theme: str, duration: int, style: str) -> str:
        """Generate mock prompt when OpenAI is not available"""
        style_config = self.video_styles.get(style, self.zack_snyder_style)
        
        return f"""
        {style_config.name} Video Production Script
        
        Theme: {theme}
        Duration: {duration} seconds
        Style: {style_config.description}
        
        Scene Breakdown:
        1. Opening shot (0-5s): Wide establishing shot with dramatic lighting
        2. Main sequence (5-{duration-5}s): Dynamic camera movements with {style_config.aspect_ratio} aspect ratio
        3. Closing shot ({duration-5}-{duration}s): Slow motion close-up with emotional impact
        
        Technical Specifications:
        - Resolution: {style_config.resolution[0]}x{style_config.resolution[1]}
        - Frame rate: {style_config.frame_rate} fps
        - Color grading: {style_config.color_grading}
        - Effects: {', '.join(style_config.effects)}
        
        Camera Movements:
        - Slow dolly shots for dramatic effect
        - Handheld for action sequences
        - Steadicam for smooth transitions
        
        Lighting Setup:
        - High contrast lighting
        - Dramatic shadows
        - Cinematic color temperature
        
        Music: Epic orchestral score with emotional crescendos
        """
    
    async def create_video_metadata(self, video_prompt: str, style: str) -> Dict[str, Any]:
        """Create metadata for video production"""
        style_config = self.video_styles.get(style, self.zack_snyder_style)
        
        metadata = {
            "title": f"Cinematic {style_config.name} Video",
            "description": video_prompt[:200] + "...",
            "style": style_config.name,
            "duration": "Variable",
            "resolution": f"{style_config.resolution[0]}x{style_config.resolution[1]}",
            "frame_rate": f"{style_config.frame_rate} fps",
            "aspect_ratio": style_config.aspect_ratio,
            "color_grading": style_config.color_grading,
            "effects": style_config.effects,
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        return metadata
    
    async def generate_nft_metadata(self, video_metadata: Dict[str, Any], 
                                  collection_name: str = "CKEmpire Videos") -> NFTMetadata:
        """Generate NFT metadata for video"""
        
        # Generate AI-powered description
        if self.openai_client:
            try:
                response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an NFT metadata specialist."},
                        {"role": "user", "content": f"Create compelling NFT metadata for this video: {video_metadata['title']}"}
                    ],
                    max_tokens=200
                )
                ai_description = response.choices[0].message.content
            except Exception as e:
                logging.error(f"Error generating AI description: {e}")
                ai_description = f"Cinematic {video_metadata['style']} video with {video_metadata['aspect_ratio']} aspect ratio"
        else:
            ai_description = f"Cinematic {video_metadata['style']} video with {video_metadata['aspect_ratio']} aspect ratio"
        
        # Generate attributes
        attributes = [
            {"trait_type": "Style", "value": video_metadata['style']},
            {"trait_type": "Resolution", "value": video_metadata['resolution']},
            {"trait_type": "Frame Rate", "value": video_metadata['frame_rate']},
            {"trait_type": "Aspect Ratio", "value": video_metadata['aspect_ratio']},
            {"trait_type": "Effects", "value": len(video_metadata['effects'])},
            {"trait_type": "Rarity", "value": "Legendary" if video_metadata['style'] == "Zack Snyder Style" else "Rare"}
        ]
        
        return NFTMetadata(
            name=video_metadata['title'],
            description=ai_description,
            image_url="https://ckempire.com/video-preview.jpg",  # Placeholder
            animation_url="https://ckempire.com/video.mp4",  # Placeholder
            attributes=attributes,
            external_url="https://ckempire.com/nft",
            seller_fee_basis_points=500,  # 5% royalty
            collection={
                "name": collection_name,
                "family": "CKEmpire"
            }
        )
    
    async def predict_nft_pricing(self, nft_metadata: NFTMetadata, 
                                market_data: Dict[str, Any] = None) -> PricingPrediction:
        """Predict NFT pricing using AI"""
        
        if not self.openai_client:
            return self._generate_mock_pricing(nft_metadata)
        
        try:
            # Analyze market factors
            market_analysis = {
                "style_popularity": self._analyze_style_popularity(nft_metadata),
                "collection_value": self._analyze_collection_value(nft_metadata),
                "rarity_score": self._calculate_rarity_score(nft_metadata),
                "market_trends": market_data or {}
            }
            
            prompt = f"""
            Analyze this NFT for pricing prediction:
            
            Name: {nft_metadata.name}
            Description: {nft_metadata.description}
            Style: {next((attr['value'] for attr in nft_metadata.attributes if attr['trait_type'] == 'Style'), 'Unknown')}
            Rarity: {next((attr['value'] for attr in nft_metadata.attributes if attr['trait_type'] == 'Rarity'), 'Unknown')}
            Effects Count: {next((attr['value'] for attr in nft_metadata.attributes if attr['trait_type'] == 'Effects'), 0)}
            
            Market Analysis:
            - Style Popularity: {market_analysis['style_popularity']}
            - Collection Value: {market_analysis['collection_value']}
            - Rarity Score: {market_analysis['rarity_score']}
            
            Provide:
            1. Predicted price in ETH
            2. Confidence level (0-1)
            3. Key pricing factors
            4. Market recommendation
            """
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an NFT pricing expert with deep knowledge of the digital art market."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            
            # Extract pricing information (simplified parsing)
            predicted_price = self._extract_price_from_response(ai_response)
            confidence = self._extract_confidence_from_response(ai_response)
            
            return PricingPrediction(
                predicted_price=predicted_price,
                confidence=confidence,
                factors=["Style popularity", "Rarity", "Collection value", "Market trends"],
                market_analysis=market_analysis,
                recommendation=ai_response
            )
            
        except Exception as e:
            logging.error(f"Error predicting NFT pricing: {e}")
            return self._generate_mock_pricing(nft_metadata)
    
    def _generate_mock_pricing(self, nft_metadata: NFTMetadata) -> PricingPrediction:
        """Generate mock pricing when AI is not available"""
        base_price = 0.5  # ETH
        rarity_multiplier = 2.0 if "Legendary" in str(nft_metadata.attributes) else 1.0
        style_multiplier = 1.5 if "Zack Snyder" in nft_metadata.name else 1.0
        
        predicted_price = base_price * rarity_multiplier * style_multiplier
        
        return PricingPrediction(
            predicted_price=predicted_price,
            confidence=0.7,
            factors=["Style popularity", "Rarity", "Collection value"],
            market_analysis={
                "style_popularity": "High",
                "collection_value": "Premium",
                "rarity_score": 0.8
            },
            recommendation="List at 0.5-1.0 ETH based on rarity and style"
        )
    
    def _analyze_style_popularity(self, nft_metadata: NFTMetadata) -> str:
        """Analyze style popularity"""
        style = next((attr['value'] for attr in nft_metadata.attributes if attr['trait_type'] == 'Style'), 'Unknown')
        
        popularity_map = {
            "Zack Snyder Style": "Very High",
            "Action": "High",
            "Dramatic": "Medium",
            "Unknown": "Low"
        }
        
        return popularity_map.get(style, "Medium")
    
    def _analyze_collection_value(self, nft_metadata: NFTMetadata) -> str:
        """Analyze collection value"""
        collection_name = nft_metadata.collection.get('name', '')
        
        if 'CKEmpire' in collection_name:
            return "Premium"
        elif 'Video' in collection_name:
            return "High"
        else:
            return "Medium"
    
    def _calculate_rarity_score(self, nft_metadata: NFTMetadata) -> float:
        """Calculate rarity score"""
        rarity = next((attr['value'] for attr in nft_metadata.attributes if attr['trait_type'] == 'Rarity'), 'Common')
        
        rarity_scores = {
            "Legendary": 0.9,
            "Epic": 0.8,
            "Rare": 0.6,
            "Common": 0.3
        }
        
        return rarity_scores.get(rarity, 0.5)
    
    def _extract_price_from_response(self, response: str) -> float:
        """Extract price from AI response"""
        try:
            # Simple extraction - look for ETH amounts
            import re
            eth_pattern = r'(\d+\.?\d*)\s*ETH'
            match = re.search(eth_pattern, response)
            if match:
                return float(match.group(1))
        except:
            pass
        return 0.5  # Default fallback
    
    def _extract_confidence_from_response(self, response: str) -> float:
        """Extract confidence from AI response"""
        try:
            # Simple extraction - look for confidence percentages
            import re
            confidence_pattern = r'(\d+\.?\d*)%'
            match = re.search(confidence_pattern, response)
            if match:
                return float(match.group(1)) / 100
        except:
            pass
        return 0.7  # Default fallback
    
    async def create_stripe_product(self, nft_metadata: NFTMetadata, 
                                  pricing_prediction: PricingPrediction) -> Dict[str, Any]:
        """Create Stripe product for NFT sale"""
        
        if not self.stripe_client:
            return self._create_mock_stripe_product(nft_metadata, pricing_prediction)
        
        try:
            # Convert ETH price to USD (simplified conversion)
            eth_to_usd_rate = 2000  # Placeholder rate
            price_usd = pricing_prediction.predicted_price * eth_to_usd_rate
            
            # Create Stripe product
            product = stripe.Product.create(
                name=nft_metadata.name,
                description=nft_metadata.description,
                metadata={
                    "nft_collection": nft_metadata.collection['name'],
                    "rarity": next((attr['value'] for attr in nft_metadata.attributes if attr['trait_type'] == 'Rarity'), 'Unknown'),
                    "style": next((attr['value'] for attr in nft_metadata.attributes if attr['trait_type'] == 'Style'), 'Unknown')
                }
            )
            
            # Create price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(price_usd * 100),  # Stripe uses cents
                currency="usd"
            )
            
            return {
                "product_id": product.id,
                "price_id": price.id,
                "price_usd": price_usd,
                "price_eth": pricing_prediction.predicted_price,
                "status": "active"
            }
            
        except Exception as e:
            logging.error(f"Error creating Stripe product: {e}")
            return self._create_mock_stripe_product(nft_metadata, pricing_prediction)
    
    def _create_mock_stripe_product(self, nft_metadata: NFTMetadata, 
                                   pricing_prediction: PricingPrediction) -> Dict[str, Any]:
        """Create mock Stripe product when Stripe is not available"""
        eth_to_usd_rate = 2000
        price_usd = pricing_prediction.predicted_price * eth_to_usd_rate
        
        return {
            "product_id": f"prod_{nft_metadata.name.lower().replace(' ', '_')}",
            "price_id": f"price_{nft_metadata.name.lower().replace(' ', '_')}",
            "price_usd": price_usd,
            "price_eth": pricing_prediction.predicted_price,
            "status": "active"
        }
    
    async def process_video_production(self, theme: str, duration: int, 
                                     style: str = "zack_snyder") -> Dict[str, Any]:
        """Complete video production workflow"""
        
        # Step 1: Generate video prompt
        video_prompt = await self.generate_video_prompt(theme, duration, style)
        
        # Step 2: Create video metadata
        video_metadata = await self.create_video_metadata(video_prompt, style)
        
        # Step 3: Generate NFT metadata
        nft_metadata = await self.generate_nft_metadata(video_metadata)
        
        # Step 4: Predict pricing
        pricing_prediction = await self.predict_nft_pricing(nft_metadata)
        
        # Step 5: Create Stripe product
        stripe_product = await self.create_stripe_product(nft_metadata, pricing_prediction)
        
        return {
            "video_prompt": video_prompt,
            "video_metadata": video_metadata,
            "nft_metadata": nft_metadata,
            "pricing_prediction": pricing_prediction,
            "stripe_product": stripe_product,
            "production_id": f"prod_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }

# Global instance
video_manager = VideoProductionManager() 