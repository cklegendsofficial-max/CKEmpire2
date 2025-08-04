"""
Content Scheduler Router for FastAPI
Provides API endpoints for managing automated content generation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import asyncio
import logging

from content_scheduler import content_scheduler, start_content_scheduler, stop_content_scheduler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/content-scheduler", tags=["Content Scheduler"])

@router.post("/start")
async def start_scheduler(background_tasks: BackgroundTasks):
    """Start the content scheduler"""
    try:
        background_tasks.add_task(start_content_scheduler)
        return {
            "status": "success",
            "message": "Content scheduler started successfully",
            "scheduler_status": content_scheduler.get_scheduler_status()
        }
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")

@router.post("/stop")
async def stop_scheduler(background_tasks: BackgroundTasks):
    """Stop the content scheduler"""
    try:
        background_tasks.add_task(stop_content_scheduler)
        return {
            "status": "success",
            "message": "Content scheduler stopped successfully"
        }
    except Exception as e:
        logger.error(f"Failed to stop scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")

@router.get("/status")
async def get_scheduler_status():
    """Get current scheduler status"""
    try:
        status = content_scheduler.get_scheduler_status()
        return {
            "status": "success",
            "scheduler_status": status
        }
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler status: {str(e)}")

@router.post("/generate-content")
async def manual_generate_content():
    """Manually trigger content generation"""
    try:
        content = await content_scheduler.manual_generate_content()
        
        # Convert content to serializable format
        content_data = []
        for item in content:
            content_dict = {
                "channel": item.channel.value,
                "adapted_title": item.adapted_title,
                "adapted_description": item.adapted_description,
                "platform_specific_hooks": item.platform_specific_hooks,
                "optimal_posting_time": item.optimal_posting_time,
                "hashtags": item.hashtags,
                "content_format": item.content_format,
                "estimated_engagement": item.estimated_engagement,
                "created_at": item.created_at.isoformat(),
                "original_idea": {
                    "title": item.original_idea.title,
                    "description": item.original_idea.description,
                    "content_type": item.original_idea.content_type.value,
                    "target_audience": item.original_idea.target_audience,
                    "viral_potential": item.original_idea.viral_potential,
                    "estimated_revenue": item.original_idea.estimated_revenue,
                    "keywords": item.original_idea.keywords,
                    "hashtags": item.original_idea.hashtags
                }
            }
            content_data.append(content_dict)
        
        return {
            "status": "success",
            "message": f"Generated {len(content)} content pieces",
            "content": content_data
        }
    except Exception as e:
        logger.error(f"Failed to generate content: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate content: {str(e)}")

@router.get("/content-history")
async def get_content_history(limit: int = 50):
    """Get content generation history"""
    try:
        history = content_scheduler.content_history[-limit:] if content_scheduler.content_history else []
        
        # Convert to serializable format
        history_data = []
        for item in history:
            history_dict = {
                "channel": item.channel.value,
                "adapted_title": item.adapted_title,
                "adapted_description": item.adapted_description,
                "platform_specific_hooks": item.platform_specific_hooks,
                "optimal_posting_time": item.optimal_posting_time,
                "hashtags": item.hashtags,
                "content_format": item.content_format,
                "estimated_engagement": item.estimated_engagement,
                "created_at": item.created_at.isoformat(),
                "original_idea": {
                    "title": item.original_idea.title,
                    "description": item.original_idea.description,
                    "content_type": item.original_idea.content_type.value,
                    "target_audience": item.original_idea.target_audience,
                    "viral_potential": item.original_idea.viral_potential,
                    "estimated_revenue": item.original_idea.estimated_revenue,
                    "keywords": item.original_idea.keywords,
                    "hashtags": item.original_idea.hashtags
                }
            }
            history_data.append(history_dict)
        
        return {
            "status": "success",
            "total_items": len(history_data),
            "content_history": history_data
        }
    except Exception as e:
        logger.error(f"Failed to get content history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get content history: {str(e)}")

@router.get("/channels")
async def get_supported_channels():
    """Get list of supported content channels"""
    try:
        channels = [
            {
                "name": channel.value,
                "display_name": channel.value.title(),
                "config": content_scheduler.platform_configs[channel]
            }
            for channel in content_scheduler.channels
        ]
        
        return {
            "status": "success",
            "channels": channels
        }
    except Exception as e:
        logger.error(f"Failed to get channels: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get channels: {str(e)}")

@router.post("/test-ollama")
async def test_ollama_connection():
    """Test Ollama connection"""
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{content_scheduler.ollama_url}/api/generate",
                json={
                    "model": "llama2",
                    "prompt": "Hello, this is a test.",
                    "stream": False
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "Ollama connection successful",
                    "response": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Ollama connection failed: {response.status_code}",
                    "response": response.text
                }
    except Exception as e:
        logger.error(f"Ollama test failed: {e}")
        return {
            "status": "error",
            "message": f"Ollama connection failed: {str(e)}"
        }

@router.get("/analytics")
async def get_content_analytics():
    """Get content analytics and performance metrics"""
    try:
        # Calculate basic analytics
        total_content = len(content_scheduler.content_history)
        
        if total_content == 0:
            return {
                "status": "success",
                "analytics": {
                    "total_content": 0,
                    "avg_engagement": 0,
                    "channel_distribution": {},
                    "top_performing_content": []
                }
            }
        
        # Calculate channel distribution
        channel_distribution = {}
        total_engagement = 0
        
        for content in content_scheduler.content_history:
            channel = content.channel.value
            if channel not in channel_distribution:
                channel_distribution[channel] = {
                    "count": 0,
                    "total_engagement": 0,
                    "avg_engagement": 0
                }
            
            channel_distribution[channel]["count"] += 1
            channel_distribution[channel]["total_engagement"] += content.estimated_engagement
            total_engagement += content.estimated_engagement
        
        # Calculate averages
        for channel in channel_distribution:
            channel_distribution[channel]["avg_engagement"] = (
                channel_distribution[channel]["total_engagement"] / 
                channel_distribution[channel]["count"]
            )
        
        avg_engagement = total_engagement / total_content
        
        # Get top performing content
        sorted_content = sorted(
            content_scheduler.content_history,
            key=lambda x: x.estimated_engagement,
            reverse=True
        )[:5]
        
        top_performing = []
        for content in sorted_content:
            top_performing.append({
                "title": content.adapted_title,
                "channel": content.channel.value,
                "engagement": content.estimated_engagement,
                "created_at": content.created_at.isoformat()
            })
        
        return {
            "status": "success",
            "analytics": {
                "total_content": total_content,
                "avg_engagement": round(avg_engagement, 3),
                "channel_distribution": channel_distribution,
                "top_performing_content": top_performing
            }
        }
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.delete("/clear-history")
async def clear_content_history():
    """Clear content generation history"""
    try:
        content_scheduler.content_history.clear()
        return {
            "status": "success",
            "message": "Content history cleared successfully"
        }
    except Exception as e:
        logger.error(f"Failed to clear history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}") 