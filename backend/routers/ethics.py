"""
Enhanced Ethics Router with AIF360 Integration
Handles bias detection, correction, auto-fix, and ethical reporting
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from database import get_db
from models import (
    BiasDetectionRequest, BiasDetectionResponse, BiasCorrectionRequest,
    BiasCorrectionResponse, EthicalReportResponse, EthicsDashboardResponse,
    BiasMetricsResponse, CorrectionMethod, BiasType
)
try:
    from ethics import ethics_manager
    from models import (
        BiasDetectionRequest,
        BiasDetectionResponse,
        BiasCorrectionRequest,
        BiasCorrectionResponse,
        EthicalReportResponse,
        EthicsDashboardResponse
    )
except ImportError:
    ethics_manager = None
    BiasDetectionRequest = None
    BiasDetectionResponse = None
    BiasCorrectionRequest = None
    BiasCorrectionResponse = None
    EthicalReportResponse = None
    EthicsDashboardResponse = None

router = APIRouter(prefix="/ethics", tags=["ethics"])

@router.post("/detect-bias", response_model=BiasDetectionResponse)
async def detect_bias(
    request: BiasDetectionRequest,
    db: Session = Depends(get_db)
):
    """
    Detect bias in dataset using AIF360 methods
    
    Args:
        request: Bias detection request with data and parameters
        db: Database session
        
    Returns:
        Bias detection results
    """
    try:
        # Convert request data to DataFrame
        data = pd.DataFrame(request.data)
        
        # Detect bias using AIF360 methods
        bias_metrics = ethics_manager.detect_bias(
            data=data,
            protected_attributes=request.protected_attributes,
            target_column=request.target_column,
            privileged_groups=request.privileged_groups
        )
        
        # Convert to response format
        metrics_responses = []
        for metric in bias_metrics:
            metrics_responses.append(BiasMetricsResponse(
                statistical_parity_difference=metric.statistical_parity_difference,
                equal_opportunity_difference=metric.equal_opportunity_difference,
                average_odds_difference=metric.average_odds_difference,
                theil_index=metric.theil_index,
                overall_bias_score=metric.overall_bias_score,
                bias_type=metric.bias_type.value,
                protected_attribute=metric.protected_attribute,
                privileged_group=metric.privileged_group,
                unprivileged_group=metric.unprivileged_group
            ))
        
        return BiasDetectionResponse(
            bias_detected=any(metric.overall_bias_score > 0.1 for metric in bias_metrics),
            bias_metrics=metrics_responses,
            total_metrics=len(bias_metrics),
            detection_timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bias detection failed: {str(e)}"
        )

@router.post("/correct-bias", response_model=BiasCorrectionResponse)
async def correct_bias(
    request: BiasCorrectionRequest,
    db: Session = Depends(get_db)
):
    """
    Apply bias correction using AIF360 reweighing
    
    Args:
        request: Bias correction request
        db: Database session
        
    Returns:
        Bias correction results
    """
    try:
        # Convert request data to DataFrame
        data = pd.DataFrame(request.data)
        
        # Apply bias correction using AIF360
        corrected_data, correction_info = ethics_manager.apply_bias_correction(
            data=data,
            protected_attributes=request.protected_attributes,
            target_column=request.target_column,
            privileged_groups=request.privileged_groups,
            method=CorrectionMethod(request.correction_method.value)
        )
        
        return BiasCorrectionResponse(
            correction_successful=correction_info.get('correction_successful', False),
            method=request.correction_method.value,
            original_bias=correction_info.get('original_bias', 0.0),
            corrected_bias=correction_info.get('corrected_bias', 0.0),
            bias_reduction=correction_info.get('bias_reduction', 0.0),
            protected_attribute=correction_info.get('protected_attribute', ''),
            weights_applied=correction_info.get('weights_applied', False),
            corrected_data=corrected_data.to_dict('records') if isinstance(corrected_data, pd.DataFrame) else [],
            correction_info=correction_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bias correction failed: {str(e)}"
        )

@router.post("/auto-fix", response_model=BiasCorrectionResponse)
async def auto_fix_bias(
    request: BiasDetectionRequest,
    db: Session = Depends(get_db)
):
    """
    Automatically fix bias if detected using AIF360
    
    Args:
        request: Auto-fix request with data and parameters
        db: Database session
        
    Returns:
        Auto-fix results
    """
    try:
        # Convert request data to DataFrame
        data = pd.DataFrame(request.data)
        
        # Apply auto-fix
        corrected_data, auto_fix_info = ethics_manager.auto_fix_bias(
            data=data,
            protected_attributes=request.protected_attributes,
            target_column=request.target_column,
            privileged_groups=request.privileged_groups
        )
        
        correction_info = auto_fix_info.get('correction_info', {})
        
        return BiasCorrectionResponse(
            correction_successful=auto_fix_info.get('auto_fix_applied', False),
            method='reweighing' if auto_fix_info.get('auto_fix_applied', False) else 'none',
            original_bias=auto_fix_info.get('overall_bias', 0.0),
            corrected_bias=correction_info.get('corrected_bias', 0.0),
            bias_reduction=auto_fix_info.get('bias_reduction', 0.0),
            protected_attribute=correction_info.get('protected_attribute', ''),
            weights_applied=correction_info.get('weights_applied', False),
            corrected_data=corrected_data.to_dict('records') if isinstance(corrected_data, pd.DataFrame) else [],
            correction_info=auto_fix_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auto-fix failed: {str(e)}"
        )

@router.post("/report", response_model=EthicalReportResponse)
async def generate_ethical_report(
    request: BiasDetectionRequest,
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive ethical analysis report with auto-fix and revert
    
    Args:
        request: Report generation request
        db: Database session
        
    Returns:
        Comprehensive ethical report
    """
    try:
        # Convert request data to DataFrame
        data = pd.DataFrame(request.data)
        
        # Generate ethical report with auto-fix and revert
        report = ethics_manager.generate_ethical_report(
            data=data,
            protected_attributes=request.protected_attributes,
            target_column=request.target_column,
            privileged_groups=request.privileged_groups
        )
        
        # Convert bias metrics to response format
        metrics_responses = []
        for metric in report.bias_metrics:
            metrics_responses.append(BiasMetricsResponse(
                statistical_parity_difference=metric.statistical_parity_difference,
                equal_opportunity_difference=metric.equal_opportunity_difference,
                average_odds_difference=metric.average_odds_difference,
                theil_index=metric.theil_index,
                overall_bias_score=metric.overall_bias_score,
                bias_type=metric.bias_type.value,
                protected_attribute=metric.protected_attribute,
                privileged_group=metric.privileged_group,
                unprivileged_group=metric.unprivileged_group
            ))
        
        return EthicalReportResponse(
            bias_metrics=metrics_responses,
            overall_ethical_score=report.overall_ethical_score,
            bias_detected=report.bias_detected,
            correction_applied=report.correction_applied,
            correction_method=report.correction_method.value if report.correction_method else None,
            recommendations=report.recommendations,
            compliance_status=report.compliance_status,
            risk_level=report.risk_level,
            generated_at=report.generated_at,
            should_stop_evolution=ethics_manager.should_stop_evolution(report.overall_ethical_score)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ethical report generation failed: {str(e)}"
        )

@router.get("/dashboard", response_model=EthicsDashboardResponse)
async def get_ethics_dashboard(
    db: Session = Depends(get_db)
):
    """
    Get ethics dashboard data with auto-fix statistics
    
    Args:
        db: Database session
        
    Returns:
        Dashboard data for ethics monitoring
    """
    try:
        dashboard_data = ethics_manager.get_ethical_dashboard_data()
        
        return EthicsDashboardResponse(
            overall_ethical_score=dashboard_data['overall_ethical_score'],
            bias_detection_rate=dashboard_data['bias_detection_rate'],
            correction_success_rate=dashboard_data['correction_success_rate'],
            avg_bias_reduction=dashboard_data['avg_bias_reduction'],
            compliance_rate=dashboard_data['compliance_rate'],
            risk_level_distribution=dashboard_data['risk_level_distribution'],
            bias_types_detected=dashboard_data['bias_types_detected'],
            correction_methods_used=dashboard_data['correction_methods_used'],
            total_corrections=dashboard_data['total_corrections'],
            total_reports=dashboard_data['total_reports'],
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard data: {str(e)}"
        )

@router.get("/bias-types")
async def get_bias_types():
    """
    Get available bias types
    
    Returns:
        List of available bias types
    """
    return {
        "bias_types": [
            {"value": bias_type.value, "label": bias_type.value.replace('_', ' ').title()}
            for bias_type in BiasType
        ]
    }

@router.get("/correction-methods")
async def get_correction_methods():
    """
    Get available correction methods
    
    Returns:
        List of available correction methods
    """
    return {
        "correction_methods": [
            {"value": method.value, "label": method.value.replace('_', ' ').title()}
            for method in CorrectionMethod
        ]
    }

@router.get("/compliance-status")
async def get_compliance_status(
    ethical_score: float = 0.8,
    db: Session = Depends(get_db)
):
    """
    Check compliance status based on ethical score
    
    Args:
        ethical_score: Current ethical score
        db: Database session
        
    Returns:
        Compliance status information
    """
    try:
        should_stop = ethics_manager.should_stop_evolution(ethical_score)
        should_revert = ethics_manager.should_revert_evolution(ethical_score)
        
        return {
            "ethical_score": ethical_score,
            "compliance_status": "compliant" if ethical_score >= 0.8 else "partial_compliance" if ethical_score >= 0.6 else "non_compliant",
            "risk_level": "low" if ethical_score >= 0.8 else "medium" if ethical_score >= 0.6 else "high",
            "should_stop_evolution": should_stop,
            "should_revert_evolution": should_revert,
            "threshold": ethics_manager.ethical_score_threshold,
            "revert_threshold": ethics_manager.revert_threshold,
            "recommendations": ethics_manager._generate_recommendations([], ethical_score, False, False, should_revert)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check compliance status: {str(e)}"
        )

@router.get("/auto-fix-status")
async def get_auto_fix_status():
    """
    Get auto-fix status and statistics
    
    Returns:
        Auto-fix status information
    """
    try:
        recent_auto_fixes = [
            fix for fix in ethics_manager.auto_fix_history
            if fix['timestamp'] > datetime.utcnow() - timedelta(days=30)
        ]
        
        recent_reverts = [
            revert for revert in ethics_manager.revert_history
            if revert['timestamp'] > datetime.utcnow() - timedelta(days=30)
        ]
        
        return {
            "auto_fix_enabled": True,
            "auto_fix_threshold": ethics_manager.auto_fix_threshold,
            "revert_threshold": ethics_manager.revert_threshold,
            "recent_auto_fixes": len(recent_auto_fixes),
            "recent_reverts": len(recent_reverts),
            "total_auto_fixes": len(ethics_manager.auto_fix_history),
            "total_reverts": len(ethics_manager.revert_history),
            "aif360_integration": True,
            "last_auto_fix": recent_auto_fixes[-1] if recent_auto_fixes else None,
            "last_revert": recent_reverts[-1] if recent_reverts else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get auto-fix status: {str(e)}"
        )

@router.get("/test-bias-correction")
async def test_bias_correction():
    """
    Test bias correction with sample biased data
    
    Returns:
        Test results for bias correction
    """
    try:
        # Create sample biased data
        np.random.seed(42)
        n_samples = 1000
        
        # Create biased dataset where gender affects outcome
        gender = np.random.choice([0, 1], n_samples, p=[0.6, 0.4])  # More females
        feature = np.random.normal(0, 1, n_samples)
        
        # Biased outcome: males more likely to get positive outcome
        outcome = np.where(
            (gender == 1) & (feature > -0.5) | (gender == 0) & (feature > 0.5),
            1, 0
        )
        
        data = pd.DataFrame({
            'gender': gender,
            'feature': feature,
            'outcome': outcome
        })
        
        # Test bias detection
        bias_metrics = ethics_manager.detect_bias(
            data=data,
            protected_attributes=['gender'],
            target_column='outcome',
            privileged_groups=[{'privileged_value': 1, 'unprivileged_value': 0}]
        )
        
        # Test auto-fix
        corrected_data, auto_fix_info = ethics_manager.auto_fix_bias(
            data=data,
            protected_attributes=['gender'],
            target_column='outcome',
            privileged_groups=[{'privileged_value': 1, 'unprivileged_value': 0}]
        )
        
        # Generate report
        report = ethics_manager.generate_ethical_report(
            data=data,
            protected_attributes=['gender'],
            target_column='outcome',
            privileged_groups=[{'privileged_value': 1, 'unprivileged_value': 0}]
        )
        
        return {
            "test_successful": True,
            "original_bias_detected": len([m for m in bias_metrics if m.overall_bias_score > 0.1]),
            "auto_fix_applied": auto_fix_info.get('auto_fix_applied', False),
            "bias_reduction": auto_fix_info.get('bias_reduction', 0.0),
            "ethical_score": report.overall_ethical_score,
            "should_stop_evolution": ethics_manager.should_stop_evolution(report.overall_ethical_score),
            "should_revert_evolution": ethics_manager.should_revert_evolution(report.overall_ethical_score),
            "sample_size": len(data),
            "bias_type": "gender",
            "aif360_method": "reweighing",
            "test_timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bias correction test failed: {str(e)}"
        ) 