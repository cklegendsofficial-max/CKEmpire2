"""
AI Router for CK Empire Builder
Handles content generation, video production, NFT automation, AGI evolution, and empire strategies
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
    SuccessResponse, EmpireStrategyRequest, EmpireStrategyResponse, FinancialMetricsResponse,
    FineTuningRequest, FineTuningResponse, FineTuningStatusResponse
)
try:
    from ..ai import ai_module
    from ..models import (
        EmpireStrategyRequest,
        EmpireStrategyResponse,
        FineTuningRequest,
        FineTuningResponse,
        FineTuningStatusResponse
    )
except ImportError:
    ai_module = None
    EmpireStrategyRequest = None
    EmpireStrategyResponse = None
    FineTuningRequest = None
    FineTuningResponse = None
    FineTuningStatusResponse = None

from ai import ai_module, ContentType, VideoStyle, NFTStatus, StrategyType

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/ai/custom-strategy", response_model=EmpireStrategyResponse)
async def generate_custom_strategy(
    request: EmpireStrategyRequest,
    db: Session = Depends(get_db)
):
    """
    Generate personalized custom empire strategy based on user input with enhanced DCF calculations
    
    - **user_input**: User's strategy requirements (e.g., "Revenue hedefi $20K, AI öneri ver")
    - **include_financial_metrics**: Whether to include enhanced DCF calculations
    """
    try:
        logger.info(f"Generating custom empire strategy for input: {request.user_input}")
        
        # Generate strategy using enhanced AI module
        strategy, financial_metrics = await ai_module.generate_custom_strategy(
            request.user_input, 
            include_financial_metrics=request.include_financial_metrics
        )
        
        # Convert to response format
        response = EmpireStrategyResponse(
            strategy_type=strategy.strategy_type.value,
            title=strategy.title,
            description=strategy.description,
            key_actions=strategy.key_actions,
            timeline_months=strategy.timeline_months,
            estimated_investment=strategy.estimated_investment,
            projected_roi=strategy.projected_roi,
            risk_level=strategy.risk_level,
            success_metrics=strategy.success_metrics,
            created_at=strategy.created_at,
            financial_metrics=financial_metrics
        )
        
        logger.info(f"✅ Generated custom empire strategy: {strategy.title}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to generate custom empire strategy: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate custom empire strategy: {str(e)}")

@router.post("/ai/empire-strategy", response_model=EmpireStrategyResponse)
async def generate_empire_strategy(
    request: EmpireStrategyRequest,
    db: Session = Depends(get_db)
):
    """
    Generate personalized empire strategy based on user input (legacy endpoint)
    
    - **user_input**: User's strategy requirements (e.g., "Revenue hedefi $20K, AI öneri ver")
    - **include_financial_metrics**: Whether to include DCF calculations
    """
    try:
        logger.info(f"Generating empire strategy for input: {request.user_input}")
        
        # Generate strategy using AI module
        strategy = await ai_module.generate_empire_strategy(request.user_input)
        
        # Calculate financial metrics if requested
        financial_metrics = None
        if request.include_financial_metrics:
            financial_metrics = ai_module._calculate_financial_metrics(strategy)
        
        # Convert to response format
        response = EmpireStrategyResponse(
            strategy_type=strategy.strategy_type.value,
            title=strategy.title,
            description=strategy.description,
            key_actions=strategy.key_actions,
            timeline_months=strategy.timeline_months,
            estimated_investment=strategy.estimated_investment,
            projected_roi=strategy.projected_roi,
            risk_level=strategy.risk_level,
            success_metrics=strategy.success_metrics,
            created_at=strategy.created_at,
            financial_metrics=financial_metrics
        )
        
        logger.info(f"✅ Generated empire strategy: {strategy.title}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to generate empire strategy: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate empire strategy: {str(e)}")

@router.post("/ai/fine-tuning/create-dataset", response_model=FineTuningResponse)
async def create_fine_tuning_dataset():
    """
    Create enhanced fine-tuning dataset for empire strategy generation
    
    Creates a dataset with 100+ diverse examples for training the AI model
    """
    try:
        logger.info("Creating enhanced fine-tuning dataset")
        
        # Create dataset using enhanced AI module
        dataset = await ai_module.create_enhanced_fine_tuning_dataset()
        
        response = FineTuningResponse(
            training_examples=len(dataset.training_data),
            validation_examples=len(dataset.validation_data),
            model_name=dataset.model_name,
            training_status=dataset.training_status,
            created_at=dataset.created_at
        )
        
        logger.info(f"✅ Created enhanced fine-tuning dataset with {len(dataset.training_data)} training examples")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to create fine-tuning dataset: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create fine-tuning dataset: {str(e)}")

@router.post("/ai/fine-tuning/start", response_model=FineTuningStatusResponse)
async def start_fine_tuning(
    request: FineTuningRequest
):
    """
    Start enhanced fine-tuning process for empire strategy generation
    
    - **model_name**: Base model to fine-tune (default: gpt-4)
    - **epochs**: Number of training epochs (default: 4)
    """
    try:
        logger.info("Starting enhanced fine-tuning process")
        
        # Create dataset first
        dataset = await ai_module.create_enhanced_fine_tuning_dataset()
        
        # Start fine-tuning
        job_id = await ai_module.start_enhanced_fine_tuning(dataset)
        
        response = FineTuningStatusResponse(
            job_id=job_id,
            status="started" if job_id != "failed" else "failed",
            model_name=request.model_name,
            epochs=request.epochs,
            created_at=datetime.utcnow()
        )
        
        logger.info(f"✅ Started enhanced fine-tuning job: {job_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to start fine-tuning: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start fine-tuning: {str(e)}")

@router.post("/ai/fine-tuning/test-accuracy", response_model=Dict[str, Any])
async def test_fine_tuning_accuracy():
    """
    Test fine-tuning accuracy with mock dataset
    
    Returns accuracy metrics and test results
    """
    try:
        logger.info("Testing fine-tuning accuracy")
        
        # Test inputs for accuracy evaluation
        test_inputs = [
            "Düşük bütçe ile başla",
            "Revenue hedefi $50K",
            "Yüksek risk toleransı",
            "Hızlı büyüme istiyorum",
            "Maliyet optimizasyonu",
            "Yeni pazarlara açıl",
            "Teknoloji odaklı",
            "Konsolide et",
            "Sürdürülebilir büyüme",
            "Kriz yönetimi"
        ]
        
        # Test accuracy
        accuracy_results = await ai_module.test_fine_tuning_accuracy(test_inputs)
        
        logger.info(f"✅ Fine-tuning accuracy test completed: {accuracy_results['accuracy']:.2%}")
        return accuracy_results
        
    except Exception as e:
        logger.error(f"❌ Failed to test fine-tuning accuracy: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test fine-tuning accuracy: {str(e)}")

@router.get("/ai/fine-tuning/status/{job_id}", response_model=FineTuningStatusResponse)
async def check_fine_tuning_status(job_id: str):
    """
    Check fine-tuning job status
    
    - **job_id**: Fine-tuning job ID
    """
    try:
        logger.info(f"Checking fine-tuning status for job: {job_id}")
        
        # Check status using AI module
        status_info = await ai_module.check_fine_tuning_status(job_id)
        
        response = FineTuningStatusResponse(
            job_id=job_id,
            status=status_info.get("status", "unknown"),
            model_name=status_info.get("model", ""),
            epochs=4,  # Default value for enhanced fine-tuning
            created_at=datetime.utcnow(),
            finished_at=status_info.get("finished_at"),
            trained_tokens=status_info.get("trained_tokens", 0)
        )
        
        logger.info(f"✅ Fine-tuning status: {status_info.get('status', 'unknown')}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to check fine-tuning status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check fine-tuning status: {str(e)}")

@router.get("/ai/strategy-types", response_model=List[str])
async def get_strategy_types():
    """
    Get available empire strategy types
    """
    try:
        strategy_types = [strategy_type.value for strategy_type in StrategyType]
        logger.info(f"✅ Retrieved {len(strategy_types)} strategy types")
        return strategy_types
        
    except Exception as e:
        logger.error(f"❌ Failed to get strategy types: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get strategy types: {str(e)}")

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