from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from datetime import datetime
from typing import List, Dict, Any

from database import get_db, EthicsLog
from models import EthicsRequest, EthicsResponse, SuccessResponse
from ethics import EthicsModule, BiasType, ContentStatus

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize ethics module
ethics_module = EthicsModule()

@router.post("/ethics/check", response_model=EthicsResponse)
async def check_ethics(
    request: EthicsRequest,
    db: Session = Depends(get_db)
):
    """
    Check content for ethical concerns and bias using AIF360
    
    - **content**: Content to analyze
    - **content_id**: Optional content ID for tracking
    - **user_id**: User ID (optional)
    """
    try:
        logger.info(f"Starting ethics analysis for content: {request.content[:100]}...")
        
        # Analyze content using EthicsModule
        report = ethics_module.analyze_content_ethical(
            content_data=request.content,
            content_id=request.content_id
        )
        
        # Convert report to response format
        response = EthicsResponse(
            bias_score=report.bias_metrics.bias_score,
            fairness_score=report.bias_metrics.fairness_score,
            bias_detected=report.bias_detected,
            bias_types=[bt.value for bt in report.bias_types],
            content_status=report.content_status.value,
            recommendations=report.recommendations,
            confidence_score=report.confidence_score,
            flagged_keywords=report.flagged_keywords,
            sensitive_topics=report.sensitive_topics,
            analysis_timestamp=report.analysis_timestamp,
            is_approved=report.content_status == ContentStatus.APPROVED
        )
        
        logger.info(f"✅ Ethics analysis completed: bias_score={report.bias_metrics.bias_score}, status={report.content_status}")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Ethics analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to perform ethics analysis: {str(e)}")

@router.get("/ethics/logs")
async def get_ethics_logs(
    skip: int = 0,
    limit: int = 100,
    bias_detected: bool = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    Get ethics monitoring logs
    
    - **skip**: Number of logs to skip
    - **limit**: Number of logs to return
    - **bias_detected**: Filter by bias detection
    - **status**: Filter by content status
    """
    try:
        query = db.query(EthicsLog)
        
        if bias_detected is not None:
            query = query.filter(EthicsLog.bias_detected == bias_detected)
        
        if status:
            query = query.filter(EthicsLog.status == status)
        
        logs = query.offset(skip).limit(limit).all()
        
        return {
            "logs": [
                {
                    "id": log.id,
                    "content_id": log.content_id,
                    "bias_detected": log.bias_detected,
                    "bias_score": log.bias_score,
                    "fairness_score": log.fairness_score,
                    "bias_types": log.bias_types,
                    "status": log.status,
                    "recommendations": log.recommendations,
                    "confidence_score": log.confidence_score,
                    "analysis_timestamp": log.analysis_timestamp.isoformat(),
                    "user_id": log.user_id
                }
                for log in logs
            ],
            "total": query.count(),
            "page": skip // limit + 1,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get ethics logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ethics logs")

@router.get("/ethics/stats")
async def get_ethics_stats(db: Session = Depends(get_db)):
    """
    Get ethics monitoring statistics
    """
    try:
        # Get summary from ethics module
        summary = ethics_module.get_ethics_summary()
        
        # Get additional stats from database
        total_analyses = db.query(EthicsLog).count()
        flagged_content = db.query(EthicsLog).filter(
            EthicsLog.bias_detected == True
        ).count()
        
        # Get status distribution
        status_counts = db.query(EthicsLog.status, db.func.count(EthicsLog.id)).group_by(
            EthicsLog.status
        ).all()
        
        # Get average bias and fairness scores
        avg_bias_score = db.query(db.func.avg(EthicsLog.bias_score)).scalar() or 0.0
        avg_fairness_score = db.query(db.func.avg(EthicsLog.fairness_score)).scalar() or 0.0
        
        return {
            "total_analyses": total_analyses,
            "flagged_content": flagged_content,
            "flag_rate": flagged_content / total_analyses if total_analyses > 0 else 0,
            "average_bias_score": round(avg_bias_score, 3),
            "average_fairness_score": round(avg_fairness_score, 3),
            "status_distribution": {
                status: count for status, count in status_counts
            },
            "module_summary": summary
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get ethics stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ethics stats")

@router.get("/ethics/summary")
async def get_ethics_summary():
    """
    Get comprehensive ethics analysis summary
    """
    try:
        summary = ethics_module.get_ethics_summary()
        
        return {
            "summary": summary,
            "bias_types": [bt.value for bt in BiasType],
            "content_statuses": [cs.value for cs in ContentStatus],
            "module_info": {
                "name": "AIF360 Ethics Module",
                "version": "1.0.0",
                "features": [
                    "Statistical Parity Difference",
                    "Equalized Odds Difference", 
                    "Average Odds Difference",
                    "Theil Index",
                    "Keyword-based detection",
                    "Content status classification",
                    "Recommendation generation"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get ethics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ethics summary")

@router.post("/ethics/configure")
async def configure_ethics(
    bias_threshold: float = None,
    fairness_threshold: float = None
):
    """
    Configure ethics monitoring settings
    
    - **bias_threshold**: Bias detection threshold (0-1)
    - **fairness_threshold**: Minimum fairness score (0-1)
    """
    try:
        if bias_threshold is not None:
            if not 0 <= bias_threshold <= 1:
                raise HTTPException(status_code=400, detail="Bias threshold must be between 0 and 1")
            ethics_module.bias_threshold = bias_threshold
        
        if fairness_threshold is not None:
            if not 0 <= fairness_threshold <= 1:
                raise HTTPException(status_code=400, detail="Fairness threshold must be between 0 and 1")
            ethics_module.fairness_threshold = fairness_threshold
        
        logger.info(f"✅ Ethics configuration updated: bias_threshold={ethics_module.bias_threshold}, fairness_threshold={ethics_module.fairness_threshold}")
        
        return SuccessResponse(
            message="Ethics configuration updated successfully",
            data={
                "bias_threshold": ethics_module.bias_threshold,
                "fairness_threshold": ethics_module.fairness_threshold
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to configure ethics: {e}")
        raise HTTPException(status_code=500, detail="Failed to configure ethics")

@router.post("/ethics/analyze-batch")
async def analyze_batch_ethics(
    contents: List[str],
    db: Session = Depends(get_db)
):
    """
    Analyze multiple content items for ethics
    
    - **contents**: List of content strings to analyze
    """
    try:
        results = []
        
        for i, content in enumerate(contents):
            try:
                report = ethics_module.analyze_content_ethical(
                    content_data=content,
                    content_id=i + 1  # Use index as content_id
                )
                
                results.append({
                    "content_id": i + 1,
                    "bias_detected": report.bias_detected,
                    "bias_score": report.bias_metrics.bias_score,
                    "fairness_score": report.bias_metrics.fairness_score,
                    "content_status": report.content_status.value,
                    "bias_types": [bt.value for bt in report.bias_types],
                    "flagged_keywords": report.flagged_keywords,
                    "sensitive_topics": report.sensitive_topics
                })
                
            except Exception as e:
                logger.error(f"Error analyzing content {i}: {e}")
                results.append({
                    "content_id": i + 1,
                    "error": str(e),
                    "bias_detected": False,
                    "bias_score": 0.0,
                    "fairness_score": 1.0,
                    "content_status": "needs_review"
                })
        
        return {
            "total_analyzed": len(contents),
            "successful_analyses": len([r for r in results if "error" not in r]),
            "failed_analyses": len([r for r in results if "error" in r]),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Batch ethics analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform batch ethics analysis")

@router.get("/ethics/health")
async def ethics_health_check():
    """
    Health check for ethics module
    """
    try:
        # Test basic functionality
        test_content = "This is a test content for health check."
        report = ethics_module.analyze_content_ethical(test_content)
        
        return {
            "status": "healthy",
            "module": "AIF360 Ethics Module",
            "test_analysis": {
                "bias_detected": report.bias_detected,
                "bias_score": report.bias_metrics.bias_score,
                "fairness_score": report.bias_metrics.fairness_score,
                "content_status": report.content_status.value
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Ethics health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        } 