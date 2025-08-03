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
        NFTMetadataResponse,
        AIMintingConfigResponse,
        NFTMintingRequest,
        NFTMintingResponse
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
    AIMintingConfigResponse = None
    NFTMintingRequest = None
    NFTMintingResponse = None

router = APIRouter(prefix="/video", tags=["video"])

@router.post("/generate/nft", response_model=NFTGenerationResponse)
async def generate_nft_with_ai(request: VideoProductionRequest):
    """Generate NFT directly with AI enhancement - one-step process"""
    try:
        logging.info(f"Generating NFT with AI for theme: {request.theme}, style: {request.style}")
        
        # Step 1: Generate AI video prompt
        video_prompt = await video_manager.generate_ai_video_prompt(
            theme=request.theme,
            duration=request.duration,
            style=request.style
        )
        
        # Step 2: Create enhanced video metadata
        video_metadata = await video_manager.create_enhanced_video_metadata(video_prompt, request.style)
        
        # Step 3: Generate AI-optimized NFT metadata
        nft_metadata = await video_manager.generate_optimized_nft_metadata(video_metadata)
        
        # Step 4: Predict enhanced pricing with ML model
        pricing_prediction = await video_manager.predict_enhanced_nft_pricing(nft_metadata)
        
        # Step 5: Create enhanced Stripe product
        stripe_product = await video_manager.create_enhanced_stripe_product(nft_metadata, pricing_prediction)
        
        return NFTGenerationResponse(
            nft_metadata=nft_metadata,
            pricing_prediction=pricing_prediction,
            stripe_product=stripe_product,
            rarity_score=nft_metadata.rarity_score,
            ai_enhanced=nft_metadata.ai_generated,
            blockchain_ready=True,
            status="completed",
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logging.error(f"Error generating NFT with AI: {e}")
        raise HTTPException(status_code=500, detail=f"AI NFT generation failed: {str(e)}")

@router.post("/generate", response_model=VideoProductionResponse)
async def generate_ai_video(request: VideoProductionRequest):
    """Generate AI-enhanced video with advanced minting capabilities"""
    try:
        logging.info(f"Generating AI-enhanced video with theme: {request.theme}, duration: {request.duration}, style: {request.style}")
        
        # Process enhanced video production
        result = await video_manager.process_enhanced_video_production(
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
            ai_minting_config=result["ai_minting_config"],
            minting_history_count=result["minting_history_count"],
            status="completed",
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logging.error(f"Error generating AI-enhanced video: {e}")
        raise HTTPException(status_code=500, detail=f"AI video generation failed: {str(e)}")

@router.post("/nft/generate", response_model=NFTGenerationResponse)
async def generate_ai_nft(request: NFTGenerationRequest):
    """Generate AI-optimized NFT metadata for existing video"""
    try:
        logging.info(f"Generating AI-optimized NFT for video: {request.video_metadata}")
        
        # Generate AI-optimized NFT metadata
        nft_metadata = await video_manager.generate_optimized_nft_metadata(
            video_metadata=request.video_metadata,
            collection_name=request.collection_name
        )
        
        # Predict enhanced pricing with ML model
        pricing_prediction = await video_manager.predict_enhanced_nft_pricing(nft_metadata)
        
        # Create enhanced Stripe product
        stripe_product = await video_manager.create_enhanced_stripe_product(nft_metadata, pricing_prediction)
        
        return NFTGenerationResponse(
            nft_metadata=nft_metadata,
            pricing_prediction=pricing_prediction,
            stripe_product=stripe_product,
            rarity_score=nft_metadata.rarity_score,
            ai_enhanced=nft_metadata.ai_generated,
            blockchain_ready=True,
            status="completed",
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logging.error(f"Error generating AI-optimized NFT: {e}")
        raise HTTPException(status_code=500, detail=f"AI NFT generation failed: {str(e)}")

@router.post("/nft/pricing", response_model=PricingPredictionResponse)
async def predict_enhanced_nft_pricing(request: PricingPredictionRequest):
    """Predict enhanced NFT pricing using advanced AI and ML models"""
    try:
        logging.info(f"Predicting enhanced pricing for NFT with ML model: {request.ml_model_version}")
        
        # Convert dict to NFTMetadata object
        from ..video import NFTMetadata
        nft_obj = NFTMetadata(
            name=request.nft_metadata.get("name", "Unknown NFT"),
            description=request.nft_metadata.get("description", ""),
            image_url=request.nft_metadata.get("image_url", ""),
            animation_url=request.nft_metadata.get("animation_url"),
            attributes=request.nft_metadata.get("attributes", []),
            external_url=request.nft_metadata.get("external_url", ""),
            seller_fee_basis_points=request.nft_metadata.get("seller_fee_basis_points", 500),
            collection=request.nft_metadata.get("collection", {}),
            ai_generated=request.nft_metadata.get("ai_generated", True),
            minting_timestamp=datetime.now(),
            blockchain_metadata=request.nft_metadata.get("blockchain_metadata", {}),
            rarity_score=request.nft_metadata.get("rarity_score", 0.5),
            market_analysis=request.nft_metadata.get("market_analysis", {})
        )
        
        # Predict enhanced pricing
        pricing_prediction = await video_manager.predict_enhanced_nft_pricing(
            nft_metadata=nft_obj,
            market_data=request.market_data
        )
        
        return PricingPredictionResponse(
            predicted_price=pricing_prediction.predicted_price,
            confidence=pricing_prediction.confidence,
            factors=pricing_prediction.factors,
            market_analysis=pricing_prediction.market_analysis,
            recommendation=pricing_prediction.recommendation,
            ml_model_version=pricing_prediction.ml_model_version,
            training_data_points=pricing_prediction.training_data_points,
            market_volatility=pricing_prediction.market_volatility,
            competitor_analysis=pricing_prediction.competitor_analysis,
            status="completed"
        )
        
    except Exception as e:
        logging.error(f"Error predicting enhanced NFT pricing: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced pricing prediction failed: {str(e)}")

@router.get("/styles", response_model=VideoStyleResponse)
async def get_enhanced_video_styles():
    """Get enhanced video styles with AI minting capabilities"""
    try:
        styles = {}
        ai_enhanced_count = 0
        blockchain_ready_count = 0
        
        for style_id, style_config in video_manager.video_styles.items():
            is_ai_enhanced = "ai_enhanced" in style_config.effects or "ai_generated" in style_config.effects
            is_blockchain_ready = hasattr(style_config, 'minting_rarity') and hasattr(style_config, 'base_price')
            
            if is_ai_enhanced:
                ai_enhanced_count += 1
            if is_blockchain_ready:
                blockchain_ready_count += 1
            
            styles[style_id] = {
                "name": style_config.name,
                "description": style_config.description,
                "aspect_ratio": style_config.aspect_ratio,
                "frame_rate": style_config.frame_rate,
                "resolution": f"{style_config.resolution[0]}x{style_config.resolution[1]}",
                "effects": style_config.effects,
                "ai_enhanced": is_ai_enhanced,
                "blockchain_ready": is_blockchain_ready,
                "minting_rarity": getattr(style_config, 'minting_rarity', 'Unknown'),
                "base_price": getattr(style_config, 'base_price', 0.0),
                "ai_prompt_template": getattr(style_config, 'ai_prompt_template', '')
            }
        
        return VideoStyleResponse(
            styles=styles,
            total_styles=len(styles),
            ai_enhanced_styles=ai_enhanced_count,
            blockchain_ready_styles=blockchain_ready_count
        )
        
    except Exception as e:
        logging.error(f"Error getting enhanced video styles: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get enhanced video styles: {str(e)}")

@router.get("/nft/metadata/{production_id}", response_model=NFTMetadataResponse)
async def get_enhanced_nft_metadata(production_id: str):
    """Get AI-optimized NFT metadata for a specific production"""
    try:
        # This would typically fetch from database
        # For now, return enhanced mock data
        mock_metadata = {
            "name": f"AI-Enhanced Cinematic Video #{production_id}",
            "description": "AI-generated cinematic video with enhanced blockchain-ready metadata",
            "image_url": "https://ckempire.com/ai-video-preview.jpg",
            "animation_url": "https://ckempire.com/ai-video.mp4",
            "attributes": [
                {"trait_type": "Style", "value": "Zack Snyder Style"},
                {"trait_type": "Resolution", "value": "1920x1080"},
                {"trait_type": "Frame Rate", "value": "24 fps"},
                {"trait_type": "Aspect Ratio", "value": "2.35:1"},
                {"trait_type": "Effects", "value": 4},
                {"trait_type": "AI Enhanced", "value": "Yes"},
                {"trait_type": "Minting Ready", "value": "Yes"},
                {"trait_type": "Rarity", "value": "Legendary"},
                {"trait_type": "Rarity Score", "value": 0.85},
                {"trait_type": "Base Price", "value": "2.0 ETH"},
                {"trait_type": "AI Model", "value": "gpt-4-turbo"},
                {"trait_type": "Blockchain", "value": "Ethereum"},
                {"trait_type": "Smart Contract", "value": "ERC-721"}
            ],
            "external_url": "https://ckempire.com/nft",
            "seller_fee_basis_points": 500,
            "collection": {
                "name": "CKEmpire AI Videos",
                "family": "CKEmpire AI"
            },
            "ai_generated": True,
            "blockchain_metadata": {
                "contract_address": "0x1234567890abcdef",
                "token_standard": "ERC-721",
                "blockchain": "Ethereum",
                "gas_estimate": "50000",
                "minting_cost": "0.01 ETH"
            },
            "rarity_score": 0.85,
            "market_analysis": {
                "similar_nfts": 150,
                "average_price": 1.2,
                "market_trend": "bullish",
                "demand_score": 0.85,
                "liquidity_score": 0.72
            }
        }
        
        return NFTMetadataResponse(
            production_id=production_id,
            metadata=mock_metadata,
            rarity_score=0.85,
            ai_enhanced=True,
            blockchain_metadata=mock_metadata["blockchain_metadata"],
            market_analysis=mock_metadata["market_analysis"],
            status="found"
        )
        
    except Exception as e:
        logging.error(f"Error getting enhanced NFT metadata: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get enhanced NFT metadata: {str(e)}")

@router.get("/ai-minting-config", response_model=AIMintingConfigResponse)
async def get_ai_minting_config():
    """Get AI minting configuration"""
    try:
        config = video_manager.ai_minting_config
        
        return AIMintingConfigResponse(
            model_version=config.model_version,
            prompt_optimization=config.prompt_optimization,
            metadata_enhancement=config.metadata_enhancement,
            rarity_calculation=config.rarity_calculation,
            market_analysis=config.market_analysis,
            blockchain_integration=config.blockchain_integration,
            minting_history_count=len(video_manager.minting_history)
        )
        
    except Exception as e:
        logging.error(f"Error getting AI minting config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI minting config: {str(e)}")

@router.post("/nft/mint", response_model=NFTMintingResponse)
async def mint_nft(request: NFTMintingRequest):
    """Mint NFT with AI optimization"""
    try:
        logging.info(f"Minting NFT for production: {request.production_id}")
        
        # Mock minting process (in real implementation, this would interact with blockchain)
        mock_transaction_hash = f"0x{request.production_id.replace('_', '')[:64]}"
        mock_token_id = f"{len(video_manager.minting_history) + 1}"
        
        return NFTMintingResponse(
            production_id=request.production_id,
            transaction_hash=mock_transaction_hash,
            token_id=mock_token_id,
            contract_address="0x1234567890abcdef",
            gas_used=50000,
            minting_cost=0.01,
            status="minted",
            blockchain_metadata={
                "blockchain": request.blockchain,
                "gas_limit": request.gas_limit or 50000,
                "auto_price": request.auto_price
            },
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logging.error(f"Error minting NFT: {e}")
        raise HTTPException(status_code=500, detail=f"NFT minting failed: {str(e)}")

@router.post("/nft/create-stripe-product")
async def create_enhanced_stripe_product_for_nft(nft_metadata: Dict[str, Any]):
    """Create enhanced Stripe product for NFT sale with AI optimization"""
    try:
        logging.info(f"Creating enhanced Stripe product for NFT: {nft_metadata.get('name', 'Unknown')}")
        
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
            collection=nft_metadata.get("collection", {}),
            ai_generated=nft_metadata.get("ai_generated", True),
            minting_timestamp=datetime.now(),
            blockchain_metadata=nft_metadata.get("blockchain_metadata", {}),
            rarity_score=nft_metadata.get("rarity_score", 0.5),
            market_analysis=nft_metadata.get("market_analysis", {})
        )
        
        # Predict enhanced pricing
        pricing_prediction = await video_manager.predict_enhanced_nft_pricing(nft_obj)
        
        # Create enhanced Stripe product
        stripe_product = await video_manager.create_enhanced_stripe_product(nft_obj, pricing_prediction)
        
        return {
            "stripe_product": stripe_product,
            "pricing_prediction": {
                "predicted_price": pricing_prediction.predicted_price,
                "confidence": pricing_prediction.confidence,
                "ml_model_version": pricing_prediction.ml_model_version,
                "market_volatility": pricing_prediction.market_volatility,
                "recommendation": pricing_prediction.recommendation
            },
            "ai_enhanced": True,
            "status": "created"
        }
        
    except Exception as e:
        logging.error(f"Error creating enhanced Stripe product: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create enhanced Stripe product: {str(e)}")

@router.get("/health")
async def enhanced_video_health_check():
    """Enhanced health check for video module with AI minting"""
    try:
        # Check if video manager is properly initialized
        styles_count = len(video_manager.video_styles)
        ai_enhanced_styles = sum(1 for style in video_manager.video_styles.values() 
                               if "ai_enhanced" in style.effects or "ai_generated" in style.effects)
        
        return {
            "status": "healthy",
            "video_styles_available": styles_count,
            "ai_enhanced_styles": ai_enhanced_styles,
            "openai_available": video_manager.openai_client is not None,
            "stripe_available": video_manager.stripe_client is not None,
            "web3_available": video_manager.web3_client is not None,
            "ai_minting_enabled": True,
            "ml_model_version": video_manager.ai_minting_config.model_version,
            "minting_history_count": len(video_manager.minting_history),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Enhanced video health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced video module unhealthy: {str(e)}") 