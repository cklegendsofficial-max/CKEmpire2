"""
AI Router for CK Empire Builder
Handles content generation, video production, NFT automation, and AGI evolution
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio

from database import get_db
from models import (
    ContentIdeaRequest, ContentIdeaResponse, VideoRequest, VideoResponse,
    NFTRequest, NFTResponse, AGIStateResponse, DecisionRequest, DecisionResponse,
    SuccessResponse
)
from ai import ai_module, ContentType, VideoStyle, NFTStatus

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/ai/ideas", response_model=List[ContentIdeaResponse])
async def generate_content_ideas(
    request: ContentIdeaRequest,
    db: Session = Depends(get_db)
):
    """
    Generate viral content ideas using OpenAI
    
    - **topic**: Topic for content generation
    - **count**: Number of ideas to generate (default: 5)
    - **content_type**: Specific content type (optional)
    """
    try:
        logger.info(f"Generating {request.count} content ideas for topic: {request.topic}")
        
        # Generate ideas using AI module
        ideas = await ai_module.generate_viral_content_ideas(
            topic=request.topic,
            count=request.count,
            content_type=request.content_type
        )
        
        # Convert to response format
        responses = []
        for idea in ideas:
            response = ContentIdeaResponse(
                title=idea.title,
                description=idea.description,
                content_type=idea.content_type.value,
                target_audience=idea.target_audience,
                viral_potential=idea.viral_potential,
                estimated_revenue=idea.estimated_revenue,
                keywords=idea.keywords,
                hashtags=idea.hashtags,
                ai_generated=idea.ai_generated,
                created_at=idea.created_at
            )
            responses.append(response)
        
        logger.info(f"✅ Generated {len(responses)} content ideas")
        return responses
        
    except Exception as e:
        logger.error(f"❌ Failed to generate content ideas: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate content ideas: {str(e)}")

@router.post("/video/generate", response_model=VideoResponse)
async def generate_video(
    request: VideoRequest,
    db: Session = Depends(get_db)
):
    """
    Generate video using AI with specified style
    
    - **script**: Video script/content
    - **style**: Video style (zack_snyder, cinematic, documentary, viral, corporate)
    - **duration**: Video duration in seconds
    """
    try:
        logger.info(f"Generating video with style: {request.style}")
        
        # Convert string style to enum
        video_style = VideoStyle(request.style)
        
        # Generate video using AI module
        video_project = await ai_module.generate_video(
            script=request.script,
            style=video_style,
            duration=request.duration
        )
        
        if not video_project:
            raise HTTPException(status_code=500, detail="Failed to generate video")
        
        # Convert to response format
        response = VideoResponse(
            title=video_project.title,
            script=video_project.script,
            style=video_project.style.value,
            duration=video_project.duration,
            resolution=video_project.resolution,
            output_path=video_project.output_path,
            status=video_project.status,
            created_at=video_project.created_at
        )
        
        logger.info(f"✅ Generated video: {video_project.output_path}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to generate video: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")

@router.post("/nft/mint", response_model=NFTResponse)
async def mint_nft(
    request: NFTRequest,
    db: Session = Depends(get_db)
):
    """
    Create and mint NFT
    
    - **name**: NFT name
    - **description**: NFT description
    - **image_path**: Path to NFT image
    - **price_eth**: Price in ETH
    - **collection**: NFT collection name
    """
    try:
        logger.info(f"Minting NFT: {request.name}")
        
        # Create NFT using AI module
        nft_project = await ai_module.create_nft(
            name=request.name,
            description=request.description,
            image_path=request.image_path,
            price_eth=request.price_eth,
            collection=request.collection
        )
        
        if not nft_project:
            raise HTTPException(status_code=500, detail="Failed to create NFT")
        
        # Convert to response format
        response = NFTResponse(
            name=nft_project.name,
            description=nft_project.description,
            image_path=nft_project.image_path,
            price_eth=nft_project.price_eth,
            price_usd=nft_project.price_usd,
            collection=nft_project.collection,
            status=nft_project.status.value,
            token_id=nft_project.token_id,
            transaction_hash=nft_project.transaction_hash,
            metadata=nft_project.metadata,
            created_at=nft_project.created_at
        )
        
        logger.info(f"✅ Minted NFT: {nft_project.name} (Token ID: {nft_project.token_id})")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to mint NFT: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to mint NFT: {str(e)}")

@router.get("/ai/agi-state", response_model=AGIStateResponse)
async def get_agi_state():
    """
    Get current AGI consciousness state
    """
    try:
        agi_state = ai_module.get_agi_state()
        
        response = AGIStateResponse(
            consciousness_score=agi_state.consciousness_score,
            decision_capability=agi_state.decision_capability,
            learning_rate=agi_state.learning_rate,
            creativity_level=agi_state.creativity_level,
            ethical_awareness=agi_state.ethical_awareness,
            last_evolution=agi_state.last_evolution,
            evolution_count=agi_state.evolution_count
        )
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to get AGI state: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get AGI state: {str(e)}")

@router.post("/ai/decide", response_model=DecisionResponse)
async def make_decision(
    request: DecisionRequest
):
    """
    Use external decision tree for AGI decision making
    
    - **context**: Context information for decision making
    """
    try:
        logger.info("Making AGI decision based on context")
        
        # Use external decision tree
        decisions = ai_module.external_decision_tree(request.context)
        
        response = DecisionResponse(
            decisions=decisions,
            agi_state=ai_module.get_agi_state(),
            timestamp=datetime.utcnow()
        )
        
        logger.info("✅ AGI decision made successfully")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to make AGI decision: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to make AGI decision: {str(e)}")

@router.get("/ai/health", response_model=SuccessResponse)
async def ai_health_check():
    """
    Check AI module health and dependencies
    """
    try:
        health_status = {
            "openai_available": ai_module.openai_client is not None,
            "stripe_available": ai_module.stripe_client is not None,
            "web3_available": ai_module.web3 is not None,
            "opencv_available": hasattr(ai_module, '_generate_frames_from_script'),
            "agi_consciousness": ai_module.get_agi_state().consciousness_score
        }
        
        all_healthy = any([
            health_status["openai_available"],
            health_status["stripe_available"],
            health_status["web3_available"]
        ])
        
        if not all_healthy:
            logger.warning("AI module has limited functionality")
        
        return SuccessResponse(
            message="AI module health check completed",
            data=health_status
        )
        
    except Exception as e:
        logger.error(f"❌ AI health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI health check failed: {str(e)}")

@router.post("/ai/upload-image", response_model=SuccessResponse)
async def upload_nft_image(
    file: UploadFile = File(...)
):
    """
    Upload image for NFT creation
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create upload directory
        upload_dir = ai_module.nft_output_dir / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"✅ Uploaded image: {file_path}")
        
        return SuccessResponse(
            message="Image uploaded successfully",
            data={"file_path": str(file_path)}
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to upload image: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

@router.get("/ai/content-types", response_model=List[str])
async def get_content_types():
    """
    Get available content types
    """
    return [ct.value for ct in ContentType]

@router.get("/ai/video-styles", response_model=List[str])
async def get_video_styles():
    """
    Get available video styles
    """
    return [vs.value for vs in VideoStyle]

@router.get("/ai/nft-statuses", response_model=List[str])
async def get_nft_statuses():
    """
    Get available NFT statuses
    """
    return [ns.value for ns in NFTStatus] 