"""
Security router for OWASP compliant security features
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from vault_service import get_vault_service
from security_scanner import get_security_scanner
from rate_limiter import get_enhanced_rate_limiter
from penetration_test import get_penetration_tester
from routers.auth import get_current_active_user

logger = structlog.get_logger()

router = APIRouter(prefix="/security", tags=["Security"])

# Pydantic models for security requests/responses
class SecurityScanRequest(BaseModel):
    """Security scan request"""
    scan_type: str = "baseline"  # baseline, full, api
    target_url: Optional[str] = None

class VaultSecretRequest(BaseModel):
    """Vault secret request"""
    path: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class RateLimitStatsResponse(BaseModel):
    """Rate limit statistics response"""
    total_events: int
    suspicious_events: int
    high_risk_events: int
    whitelisted_ips: int
    blacklisted_ips: int
    redis_connected: bool
    limits: Dict[str, Any]

class SecurityReportResponse(BaseModel):
    """Security report response"""
    scan_type: str
    target_url: str
    scan_timestamp: str
    status: str
    security_score: float
    total_vulnerabilities: int
    summary: Dict[str, Any]
    recommendations: List[str]

class PenetrationTestResponse(BaseModel):
    """Penetration test response"""
    test_timestamp: str
    duration_seconds: float
    target_url: str
    overall_security_score: float
    total_vulnerabilities: int
    test_results: Dict[str, Any]
    recommendations: List[str]
    risk_assessment: Dict[str, Any]

# Security endpoints
@router.get("/health")
async def security_health_check():
    """Check security services health"""
    try:
        vault_service = get_vault_service()
        security_scanner = get_security_scanner()
        rate_limiter = get_enhanced_rate_limiter()
        penetration_tester = get_penetration_tester()
        
        health_status = {
            "vault": vault_service.health_check(),
            "security_scanner": "healthy",
            "rate_limiter": rate_limiter.get_rate_limit_stats(),
            "penetration_tester": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {"status": "healthy", "services": health_status}
        
    except Exception as e:
        logger.error(f"❌ Security health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Security health check failed"
        )

@router.post("/scan", response_model=SecurityReportResponse)
async def run_security_scan(request: SecurityScanRequest):
    """Run security scan with ZAP"""
    try:
        security_scanner = get_security_scanner()
        
        # Set target URL if provided
        if request.target_url:
            security_scanner.target_url = request.target_url
        
        # Run scan
        scan_result = security_scanner.run_zap_scan(request.scan_type)
        
        if "error" in scan_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=scan_result["error"]
            )
        
        return SecurityReportResponse(
            scan_type=scan_result["scan_type"],
            target_url=scan_result["target_url"],
            scan_timestamp=scan_result["scan_timestamp"],
            status=scan_result["status"],
            security_score=scan_result["security_score"],
            total_vulnerabilities=scan_result["total_vulnerabilities"],
            summary=scan_result["summary"],
            recommendations=scan_result["recommendations"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Security scan failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Security scan failed"
        )

@router.post("/owasp-checklist")
async def run_owasp_checklist():
    """Run OWASP Top 10 checklist"""
    try:
        security_scanner = get_security_scanner()
        checklist_result = security_scanner.run_owasp_checklist()
        
        if "error" in checklist_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=checklist_result["error"]
            )
        
        return checklist_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ OWASP checklist failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OWASP checklist failed"
        )

@router.post("/penetration-test", response_model=PenetrationTestResponse)
async def run_penetration_test():
    """Run comprehensive penetration test"""
    try:
        penetration_tester = get_penetration_tester()
        test_result = penetration_tester.run_full_penetration_test()
        
        if "error" in test_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=test_result["error"]
            )
        
        return PenetrationTestResponse(
            test_timestamp=test_result["test_timestamp"],
            duration_seconds=test_result["duration_seconds"],
            target_url=test_result["target_url"],
            overall_security_score=test_result["overall_security_score"],
            total_vulnerabilities=test_result["total_vulnerabilities"],
            test_results=test_result["test_results"],
            recommendations=test_result["recommendations"],
            risk_assessment=test_result["risk_assessment"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Penetration test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Penetration test failed"
        )

# Vault endpoints
@router.post("/vault/store")
async def store_secret(request: VaultSecretRequest):
    """Store secret in Vault"""
    try:
        vault_service = get_vault_service()
        success = vault_service.store_secret(request.path, request.data, request.metadata)
        
        if success:
            return {"message": "Secret stored successfully", "path": request.path}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store secret"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to store secret: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store secret"
        )

@router.get("/vault/retrieve/{path:path}")
async def retrieve_secret(path: str):
    """Retrieve secret from Vault"""
    try:
        vault_service = get_vault_service()
        secret = vault_service.get_secret(path)
        
        if secret is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Secret not found"
            )
        
        return {"path": path, "data": secret}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to retrieve secret: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve secret"
        )

@router.delete("/vault/delete/{path:path}")
async def delete_secret(path: str):
    """Delete secret from Vault"""
    try:
        vault_service = get_vault_service()
        success = vault_service.delete_secret(path)
        
        if success:
            return {"message": "Secret deleted successfully", "path": path}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Secret not found or deletion failed"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete secret: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete secret"
        )

@router.get("/vault/list")
async def list_secrets(path: str = ""):
    """List secrets in Vault"""
    try:
        vault_service = get_vault_service()
        secrets = vault_service.list_secrets(path)
        
        return {"secrets": secrets, "path": path}
        
    except Exception as e:
        logger.error(f"❌ Failed to list secrets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list secrets"
        )

@router.post("/vault/rotate/{path:path}")
async def rotate_secret(path: str):
    """Rotate secret in Vault"""
    try:
        vault_service = get_vault_service()
        success = vault_service.rotate_secret(path)
        
        if success:
            return {"message": "Secret rotated successfully", "path": path}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Secret not found or rotation failed"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to rotate secret: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rotate secret"
        )

# Rate limiting endpoints
@router.get("/rate-limit/stats", response_model=RateLimitStatsResponse)
async def get_rate_limit_stats():
    """Get rate limiting statistics"""
    try:
        rate_limiter = get_enhanced_rate_limiter()
        stats = rate_limiter.get_rate_limit_stats()
        
        return RateLimitStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"❌ Failed to get rate limit stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rate limit stats"
        )

@router.post("/rate-limit/blacklist/{ip}")
async def add_to_blacklist(ip: str, reason: str = "Manual addition"):
    """Add IP to blacklist"""
    try:
        rate_limiter = get_enhanced_rate_limiter()
        rate_limiter.add_to_blacklist(ip, reason)
        
        return {"message": f"IP {ip} added to blacklist", "reason": reason}
        
    except Exception as e:
        logger.error(f"❌ Failed to add IP to blacklist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add IP to blacklist"
        )

@router.delete("/rate-limit/blacklist/{ip}")
async def remove_from_blacklist(ip: str):
    """Remove IP from blacklist"""
    try:
        rate_limiter = get_enhanced_rate_limiter()
        rate_limiter.remove_from_blacklist(ip)
        
        return {"message": f"IP {ip} removed from blacklist"}
        
    except Exception as e:
        logger.error(f"❌ Failed to remove IP from blacklist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove IP from blacklist"
        )

@router.post("/rate-limit/whitelist/{ip}")
async def add_to_whitelist(ip: str, reason: str = "Manual addition"):
    """Add IP to whitelist"""
    try:
        rate_limiter = get_enhanced_rate_limiter()
        rate_limiter.add_to_whitelist(ip, reason)
        
        return {"message": f"IP {ip} added to whitelist", "reason": reason}
        
    except Exception as e:
        logger.error(f"❌ Failed to add IP to whitelist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add IP to whitelist"
        )

@router.delete("/rate-limit/whitelist/{ip}")
async def remove_from_whitelist(ip: str):
    """Remove IP from whitelist"""
    try:
        rate_limiter = get_enhanced_rate_limiter()
        rate_limiter.remove_from_whitelist(ip)
        
        return {"message": f"IP {ip} removed from whitelist"}
        
    except Exception as e:
        logger.error(f"❌ Failed to remove IP from whitelist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove IP from whitelist"
        )

@router.get("/rate-limit/suspicious-activity")
async def get_suspicious_activity_report(hours: int = 24):
    """Get suspicious activity report"""
    try:
        rate_limiter = get_enhanced_rate_limiter()
        report = rate_limiter.get_suspicious_activity_report(hours)
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Failed to get suspicious activity report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get suspicious activity report"
        )

# Security testing endpoints
@router.get("/test/headers")
async def test_security_headers():
    """Test security headers"""
    try:
        security_scanner = get_security_scanner()
        headers_result = security_scanner._test_headers_security()
        
        return headers_result
        
    except Exception as e:
        logger.error(f"❌ Security headers test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Security headers test failed"
        )

@router.get("/test/api-security")
async def test_api_security():
    """Test API security"""
    try:
        security_scanner = get_security_scanner()
        api_result = security_scanner._test_api_security()
        
        return api_result
        
    except Exception as e:
        logger.error(f"❌ API security test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API security test failed"
        )

# Security configuration endpoints
@router.get("/config/limits")
async def get_rate_limit_config():
    """Get rate limiting configuration"""
    try:
        rate_limiter = get_enhanced_rate_limiter()
        return {"limits": rate_limiter.limits}
        
    except Exception as e:
        logger.error(f"❌ Failed to get rate limit config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rate limit config"
        )

@router.post("/config/limits")
async def update_rate_limit_config(limits: Dict[str, Dict[str, Any]]):
    """Update rate limiting configuration"""
    try:
        rate_limiter = get_enhanced_rate_limiter()
        rate_limiter.limits.update(limits)
        
        return {"message": "Rate limit configuration updated", "limits": rate_limiter.limits}
        
    except Exception as e:
        logger.error(f"❌ Failed to update rate limit config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update rate limit config"
        )

# Security reports
@router.get("/reports/security")
async def get_security_reports():
    """Get available security reports"""
    try:
        import os
        from pathlib import Path
        
        reports_dir = Path("security_reports")
        if not reports_dir.exists():
            return {"reports": []}
        
        reports = []
        for report_file in reports_dir.glob("*.json"):
            reports.append({
                "filename": report_file.name,
                "size": report_file.stat().st_size,
                "modified": datetime.fromtimestamp(report_file.stat().st_mtime).isoformat()
            })
        
        return {"reports": reports}
        
    except Exception as e:
        logger.error(f"❌ Failed to get security reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get security reports"
        )

@router.get("/reports/penetration")
async def get_penetration_reports():
    """Get available penetration test reports"""
    try:
        import os
        from pathlib import Path
        
        reports_dir = Path("penetration_reports")
        if not reports_dir.exists():
            return {"reports": []}
        
        reports = []
        for report_file in reports_dir.glob("*.json"):
            reports.append({
                "filename": report_file.name,
                "size": report_file.stat().st_size,
                "modified": datetime.fromtimestamp(report_file.stat().st_mtime).isoformat()
            })
        
        return {"reports": reports}
        
    except Exception as e:
        logger.error(f"❌ Failed to get penetration reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get penetration reports"
        ) 