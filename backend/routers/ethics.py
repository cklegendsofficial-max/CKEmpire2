from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import re
from typing import List

from database import get_db, EthicsLog
from models import EthicsRequest, EthicsResponse, RiskLevel, SuccessResponse
from config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

def detect_bias(content: str) -> float:
    """
    Detect bias in content using simple heuristics
    Returns bias score between 0 and 1
    """
    bias_score = 0.0
    
    # Convert to lowercase for analysis
    content_lower = content.lower()
    
    # Define bias indicators
    bias_indicators = {
        'discriminatory': ['racist', 'sexist', 'discriminatory', 'prejudiced'],
        'hate_speech': ['hate', 'violence', 'kill', 'destroy', 'attack'],
        'stereotypes': ['all women', 'all men', 'all muslims', 'all jews'],
        'extremist': ['extremist', 'radical', 'terrorist', 'fanatic'],
        'offensive': ['offensive', 'insulting', 'derogatory', 'slur']
    }
    
    # Check for bias indicators
    for category, indicators in bias_indicators.items():
        for indicator in indicators:
            if indicator in content_lower:
                bias_score += 0.2
                break
    
    # Check for aggressive language patterns
    aggressive_patterns = [
        r'\b(kill|destroy|attack|hate)\b',
        r'\b(all|every|none)\s+\w+\s+(are|is)\b',
        r'\b(always|never)\b'
    ]
    
    for pattern in aggressive_patterns:
        matches = re.findall(pattern, content_lower)
        if matches:
            bias_score += 0.1 * len(matches)
    
    # Normalize score to 0-1 range
    bias_score = min(bias_score, 1.0)
    
    return bias_score

def determine_risk_level(bias_score: float) -> RiskLevel:
    """Determine risk level based on bias score"""
    if bias_score < 0.3:
        return RiskLevel.LOW
    elif bias_score < 0.6:
        return RiskLevel.MEDIUM
    elif bias_score < 0.8:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL

def generate_recommendations(bias_score: float, risk_level: RiskLevel) -> List[str]:
    """Generate recommendations based on bias analysis"""
    recommendations = []
    
    if bias_score > 0.5:
        recommendations.append("Content contains potentially biased language")
    
    if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        recommendations.append("Consider reviewing content before publication")
        recommendations.append("Implement content moderation guidelines")
    
    if bias_score > 0.7:
        recommendations.append("Content may violate community guidelines")
        recommendations.append("Consider using neutral language")
    
    if not recommendations:
        recommendations.append("Content appears to be appropriate")
    
    return recommendations

@router.post("/ethics/check", response_model=EthicsResponse)
async def check_ethics(
    request: EthicsRequest,
    db: Session = Depends(get_db)
):
    """
    Check content for ethical concerns and bias
    
    - **content**: Content to analyze
    - **action**: Action being performed
    - **user_id**: User ID (optional)
    """
    try:
        # Detect bias
        bias_score = detect_bias(request.content)
        risk_level = determine_risk_level(bias_score)
        recommendations = generate_recommendations(bias_score, risk_level)
        
        # Determine if content is approved
        is_approved = bias_score < settings.BIAS_DETECTION_THRESHOLD
        
        # Log the ethics check
        ethics_log = EthicsLog(
            action=request.action,
            content=request.content,
            bias_score=bias_score,
            risk_level=risk_level.value,
            user_id=request.user_id,
            timestamp=datetime.utcnow()
        )
        db.add(ethics_log)
        db.commit()
        
        logger.info(f"✅ Ethics check completed: bias_score={bias_score}, risk_level={risk_level}")
        
        return EthicsResponse(
            bias_score=bias_score,
            risk_level=risk_level,
            recommendations=recommendations,
            is_approved=is_approved,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"❌ Ethics check failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform ethics check")

@router.get("/ethics/logs")
async def get_ethics_logs(
    skip: int = 0,
    limit: int = 100,
    risk_level: str = None,
    db: Session = Depends(get_db)
):
    """
    Get ethics monitoring logs
    
    - **skip**: Number of logs to skip
    - **limit**: Number of logs to return
    - **risk_level**: Filter by risk level
    """
    try:
        query = db.query(EthicsLog)
        
        if risk_level:
            query = query.filter(EthicsLog.risk_level == risk_level)
        
        logs = query.offset(skip).limit(limit).all()
        
        return {
            "logs": [
                {
                    "id": log.id,
                    "action": log.action,
                    "bias_score": log.bias_score,
                    "risk_level": log.risk_level,
                    "timestamp": log.timestamp.isoformat(),
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
        total_checks = db.query(EthicsLog).count()
        high_risk_checks = db.query(EthicsLog).filter(
            EthicsLog.risk_level.in_([RiskLevel.HIGH.value, RiskLevel.CRITICAL.value])
        ).count()
        
        avg_bias_score = db.query(EthicsLog.bias_score).filter(
            EthicsLog.bias_score.isnot(None)
        ).all()
        
        avg_score = sum(score[0] for score in avg_bias_score) / len(avg_bias_score) if avg_bias_score else 0
        
        return {
            "total_checks": total_checks,
            "high_risk_checks": high_risk_checks,
            "average_bias_score": round(avg_score, 3),
            "risk_percentage": round((high_risk_checks / total_checks * 100) if total_checks > 0 else 0, 2)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get ethics stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ethics stats")

@router.post("/ethics/configure")
async def configure_ethics(
    bias_threshold: float,
    db: Session = Depends(get_db)
):
    """
    Configure ethics monitoring settings
    
    - **bias_threshold**: Bias detection threshold (0-1)
    """
    try:
        if not 0 <= bias_threshold <= 1:
            raise HTTPException(status_code=400, detail="Bias threshold must be between 0 and 1")
        
        # Update settings (in a real app, this would be stored in database)
        settings.BIAS_DETECTION_THRESHOLD = bias_threshold
        
        logger.info(f"✅ Ethics configuration updated: bias_threshold={bias_threshold}")
        
        return SuccessResponse(
            message="Ethics configuration updated successfully",
            data={"bias_threshold": bias_threshold}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to configure ethics: {e}")
        raise HTTPException(status_code=500, detail="Failed to configure ethics") 