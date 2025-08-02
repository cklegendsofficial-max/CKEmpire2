from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import openai
from typing import Optional

from database import get_db, AILog
from models import AIRequest, AIResponse, SuccessResponse
from config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize OpenAI client
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY
else:
    logger.warning("⚠️  OpenAI API key not configured")

def calculate_cost(tokens_used: int, model: str) -> float:
    """Calculate cost based on tokens used and model"""
    # Approximate costs per 1K tokens (USD)
    costs = {
        "gpt-4": 0.03,
        "gpt-4-turbo": 0.01,
        "gpt-3.5-turbo": 0.002,
        "gpt-3.5-turbo-16k": 0.003
    }
    
    model_cost = costs.get(model, 0.01)  # Default cost
    return (tokens_used / 1000) * model_cost

@router.post("/ai/generate", response_model=AIResponse)
async def generate_ai_response(
    request: AIRequest,
    db: Session = Depends(get_db)
):
    """
    Generate AI response using OpenAI
    
    - **prompt**: AI prompt
    - **model**: AI model to use
    - **max_tokens**: Maximum tokens
    - **temperature**: AI temperature
    """
    try:
        if not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model=request.model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for the CK Empire Builder platform."},
                {"role": "user", "content": request.prompt}
            ],
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Extract response data
        ai_response = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        cost = calculate_cost(tokens_used, request.model)
        
        # Log the AI interaction
        ai_log = AILog(
            prompt=request.prompt,
            response=ai_response,
            model=request.model,
            tokens_used=tokens_used,
            cost=cost,
            timestamp=datetime.utcnow()
        )
        db.add(ai_log)
        db.commit()
        
        logger.info(f"✅ AI response generated: model={request.model}, tokens={tokens_used}")
        
        return AIResponse(
            response=ai_response,
            model=request.model,
            tokens_used=tokens_used,
            cost=cost,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"❌ AI generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI response: {str(e)}")

@router.post("/ai/analyze-project")
async def analyze_project_ai(
    project_id: int,
    analysis_type: str = "general",
    db: Session = Depends(get_db)
):
    """
    Analyze project using AI
    
    - **project_id**: Project ID
    - **analysis_type**: Type of analysis (general, financial, risk)
    """
    try:
        # Get project data
        from database import get_project_by_id
        project = get_project_by_id(db, project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Create analysis prompt
        if analysis_type == "financial":
            prompt = f"""
            Analyze the financial performance of project '{project.name}':
            - Budget: ${project.budget}
            - Revenue: ${project.revenue}
            - Status: {project.status}
            
            Provide financial insights and recommendations.
            """
        elif analysis_type == "risk":
            prompt = f"""
            Analyze the risk factors for project '{project.name}':
            - Budget utilization: {(project.revenue/project.budget*100) if project.budget > 0 else 0}%
            - Status: {project.status}
            
            Identify potential risks and mitigation strategies.
            """
        else:
            prompt = f"""
            Provide a comprehensive analysis of project '{project.name}':
            - Description: {project.description}
            - Budget: ${project.budget}
            - Revenue: ${project.revenue}
            - Status: {project.status}
            
            Include strengths, weaknesses, opportunities, and threats.
            """
        
        # Generate AI response
        ai_request = AIRequest(
            prompt=prompt,
            model="gpt-4",
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = await generate_ai_response(ai_request, db)
        
        return {
            "project_id": project_id,
            "analysis_type": analysis_type,
            "analysis": ai_response.response,
            "tokens_used": ai_response.tokens_used,
            "cost": ai_response.cost
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Project analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze project")

@router.post("/ai/generate-content")
async def generate_content_ai(
    content_type: str,
    topic: str,
    length: str = "medium",
    db: Session = Depends(get_db)
):
    """
    Generate content using AI
    
    - **content_type**: Type of content (blog, social, email)
    - **topic**: Content topic
    - **length**: Content length (short, medium, long)
    """
    try:
        # Create content generation prompt
        length_tokens = {
            "short": 200,
            "medium": 500,
            "long": 1000
        }
        
        max_tokens = length_tokens.get(length, 500)
        
        prompt = f"""
        Generate {content_type} content about: {topic}
        
        Requirements:
        - Content type: {content_type}
        - Length: {length}
        - Tone: Professional and engaging
        - Include relevant keywords naturally
        
        Please provide the content in a clear, well-structured format.
        """
        
        # Generate AI response
        ai_request = AIRequest(
            prompt=prompt,
            model="gpt-4",
            max_tokens=max_tokens,
            temperature=0.8
        )
        
        ai_response = await generate_ai_response(ai_request, db)
        
        return {
            "content_type": content_type,
            "topic": topic,
            "length": length,
            "content": ai_response.response,
            "tokens_used": ai_response.tokens_used,
            "cost": ai_response.cost
        }
        
    except Exception as e:
        logger.error(f"❌ Content generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate content")

@router.get("/ai/logs")
async def get_ai_logs(
    skip: int = 0,
    limit: int = 100,
    model: str = None,
    db: Session = Depends(get_db)
):
    """
    Get AI interaction logs
    
    - **skip**: Number of logs to skip
    - **limit**: Number of logs to return
    - **model**: Filter by AI model
    """
    try:
        query = db.query(AILog)
        
        if model:
            query = query.filter(AILog.model == model)
        
        logs = query.offset(skip).limit(limit).all()
        
        return {
            "logs": [
                {
                    "id": log.id,
                    "model": log.model,
                    "tokens_used": log.tokens_used,
                    "cost": log.cost,
                    "timestamp": log.timestamp.isoformat()
                }
                for log in logs
            ],
            "total": query.count(),
            "page": skip // limit + 1,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get AI logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI logs")

@router.get("/ai/stats")
async def get_ai_stats(db: Session = Depends(get_db)):
    """
    Get AI usage statistics
    """
    try:
        total_requests = db.query(AILog).count()
        total_tokens = db.query(AILog.tokens_used).filter(
            AILog.tokens_used.isnot(None)
        ).all()
        
        total_cost = db.query(AILog.cost).filter(
            AILog.cost.isnot(None)
        ).all()
        
        avg_tokens = sum(t[0] for t in total_tokens) / len(total_tokens) if total_tokens else 0
        total_cost_sum = sum(c[0] for c in total_cost) if total_cost else 0
        
        # Get model usage
        model_stats = db.query(AILog.model, db.func.count(AILog.id)).group_by(AILog.model).all()
        
        return {
            "total_requests": total_requests,
            "total_tokens": sum(t[0] for t in total_tokens),
            "average_tokens_per_request": round(avg_tokens, 2),
            "total_cost": round(total_cost_sum, 4),
            "model_usage": {model: count for model, count in model_stats}
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get AI stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI stats")

@router.post("/ai/configure")
async def configure_ai(
    model: str,
    max_tokens: int,
    temperature: float,
    db: Session = Depends(get_db)
):
    """
    Configure AI settings
    
    - **model**: Default AI model
    - **max_tokens**: Default max tokens
    - **temperature**: Default temperature
    """
    try:
        # Update settings (in a real app, this would be stored in database)
        settings.AI_MODEL = model
        settings.AI_MAX_TOKENS = max_tokens
        settings.AI_TEMPERATURE = temperature
        
        logger.info(f"✅ AI configuration updated: model={model}, max_tokens={max_tokens}")
        
        return SuccessResponse(
            message="AI configuration updated successfully",
            data={
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to configure AI: {e}")
        raise HTTPException(status_code=500, detail="Failed to configure AI") 