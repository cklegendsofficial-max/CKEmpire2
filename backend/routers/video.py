from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import logging
from datetime import datetime

try:
    from ..video import video_manager
    from ..models import (
        VideoProductionRequest,
        VideoProductionResponse,
        NFTGenerationRequest,
        NFTGenerationResponse,
        PricingPredictionRequest,
        PricingPredictionResponse,
        VideoStyleResponse,
        NFTMetadataResponse
    )
except ImportError:
    video_manager = None
    VideoProductionRequest = None
    VideoProductionResponse = None
    NFTGenerationRequest = None
    NFTGenerationResponse = None
    PricingPredictionRequest = None
    PricingPredictionResponse = None
    VideoStyleResponse = None
    NFTMetadataResponse = None

router = APIRouter(prefix="/video", tags=["video"])

@router.post("/generate", response_model=VideoProductionResponse)
async def generate_video(request: VideoProductionRequest):
    """Generate AI-powered video with Zack Snyder style"""
    try:
        logging.info(f"Generating video with theme: {request.theme}, duration: {request.duration}, style: {request.style}")
        
        # Process video production
        result = await video_manager.process_video_production(
            theme=request.theme,
            duration=request.duration,
            style=request.style
        )
        
        return VideoProductionResponse(
            production_id=result["production_id"],
            video_prompt=result["video_prompt"],
            video_metadata=result["video_metadata"],
            nft_metadata=result["nft_metadata"],
            pricing_prediction=result["pricing_prediction"],
            stripe_product=result["stripe_product"],
            status="completed",
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logging.error(f"Error generating video: {e}")
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

@router.post("/nft/generate", response_model=NFTGenerationResponse)
async def generate_nft(request: NFTGenerationRequest):
    """Generate NFT metadata for existing video"""
    try:
        logging.info(f"Generating NFT for video: {request.video_metadata}")
        
        # Generate NFT metadata
        nft_metadata = await video_manager.generate_nft_metadata(
            video_metadata=request.video_metadata,
            collection_name=request.collection_name
        )
        
        # Predict pricing
        pricing_prediction = await video_manager.predict_nft_pricing(nft_metadata)
        
        # Create Stripe product
        stripe_product = await video_manager.create_stripe_product(nft_metadata, pricing_prediction)
        
        return NFTGenerationResponse(
            nft_metadata=nft_metadata,
            pricing_prediction=pricing_prediction,
            stripe_product=stripe_product,
            status="completed",
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logging.error(f"Error generating NFT: {e}")
        raise HTTPException(status_code=500, detail=f"NFT generation failed: {str(e)}")

@router.post("/nft/pricing", response_model=PricingPredictionResponse)
async def predict_nft_pricing(request: PricingPredictionRequest):
    """Predict NFT pricing using AI"""
    try:
        logging.info(f"Predicting pricing for NFT: {request.nft_metadata.name}")
        
        # Predict pricing
        pricing_prediction = await video_manager.predict_nft_pricing(
            nft_metadata=request.nft_metadata,
            market_data=request.market_data
        )
        
        return PricingPredictionResponse(
            predicted_price=pricing_prediction.predicted_price,
            confidence=pricing_prediction.confidence,
            factors=pricing_prediction.factors,
            market_analysis=pricing_prediction.market_analysis,
            recommendation=pricing_prediction.recommendation,
            status="completed"
        )
        
    except Exception as e:
        logging.error(f"Error predicting NFT pricing: {e}")
        raise HTTPException(status_code=500, detail=f"Pricing prediction failed: {str(e)}")

@router.get("/styles", response_model=VideoStyleResponse)
async def get_video_styles():
    """Get available video styles"""
    try:
        styles = {}
        for style_id, style_config in video_manager.video_styles.items():
            styles[style_id] = {
                "name": style_config.name,
                "description": style_config.description,
                "aspect_ratio": style_config.aspect_ratio,
                "frame_rate": style_config.frame_rate,
                "resolution": f"{style_config.resolution[0]}x{style_config.resolution[1]}",
                "effects": style_config.effects
            }
        
        return VideoStyleResponse(
            styles=styles,
            total_styles=len(styles)
        )
        
    except Exception as e:
        logging.error(f"Error getting video styles: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get video styles: {str(e)}")

@router.get("/nft/metadata/{production_id}", response_model=NFTMetadataResponse)
async def get_nft_metadata(production_id: str):
    """Get NFT metadata for a specific production"""
    try:
        # This would typically fetch from database
        # For now, return mock data
        mock_metadata = {
            "name": f"Cinematic Video #{production_id}",
            "description": "AI-generated cinematic video with Zack Snyder style",
            "image_url": "https://ckempire.com/video-preview.jpg",
            "animation_url": "https://ckempire.com/video.mp4",
            "attributes": [
                {"trait_type": "Style", "value": "Zack Snyder Style"},
                {"trait_type": "Resolution", "value": "1920x1080"},
                {"trait_type": "Frame Rate", "value": "24 fps"},
                {"trait_type": "Aspect Ratio", "value": "2.35:1"},
                {"trait_type": "Effects", "value": 3},
                {"trait_type": "Rarity", "value": "Legendary"}
            ],
            "external_url": "https://ckempire.com/nft",
            "seller_fee_basis_points": 500,
            "collection": {
                "name": "CKEmpire Videos",
                "family": "CKEmpire"
            }
        }
        
        return NFTMetadataResponse(
            production_id=production_id,
            metadata=mock_metadata,
            status="found"
        )
        
    except Exception as e:
        logging.error(f"Error getting NFT metadata: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get NFT metadata: {str(e)}")

@router.post("/nft/create-stripe-product")
async def create_stripe_product_for_nft(nft_metadata: Dict[str, Any]):
    """Create Stripe product for NFT sale"""
    try:
        logging.info(f"Creating Stripe product for NFT: {nft_metadata.get('name', 'Unknown')}")
        
        # Convert dict to NFTMetadata object
        from ..video import NFTMetadata
        nft_obj = NFTMetadata(
            name=nft_metadata.get("name", "Unknown NFT"),
            description=nft_metadata.get("description", ""),
            image_url=nft_metadata.get("image_url", ""),
            animation_url=nft_metadata.get("animation_url"),
            attributes=nft_metadata.get("attributes", []),
            external_url=nft_metadata.get("external_url", ""),
            seller_fee_basis_points=nft_metadata.get("seller_fee_basis_points", 500),
            collection=nft_metadata.get("collection", {})
        )
        
        # Predict pricing
        pricing_prediction = await video_manager.predict_nft_pricing(nft_obj)
        
        # Create Stripe product
        stripe_product = await video_manager.create_stripe_product(nft_obj, pricing_prediction)
        
        return {
            "stripe_product": stripe_product,
            "pricing_prediction": {
                "predicted_price": pricing_prediction.predicted_price,
                "confidence": pricing_prediction.confidence,
                "recommendation": pricing_prediction.recommendation
            },
            "status": "created"
        }
        
    except Exception as e:
        logging.error(f"Error creating Stripe product: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create Stripe product: {str(e)}")

@router.get("/health")
async def video_health_check():
    """Health check for video module"""
    try:
        # Check if video manager is properly initialized
        styles_count = len(video_manager.video_styles)
        
        return {
            "status": "healthy",
            "video_styles_available": styles_count,
            "openai_available": video_manager.openai_client is not None,
            "stripe_available": video_manager.stripe_client is not None,
            "web3_available": video_manager.web3_client is not None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Video health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Video module unhealthy: {str(e)}") 