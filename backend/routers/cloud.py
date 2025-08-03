from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

try:
    from ..cloud.backup_service import backup_service
    from ..cloud.aws_manager import AWSManager
except ImportError:
    # Fallback for when cloud modules are not available
    backup_service = None
    AWSManager = None

try:
    from ..config.cloud_config import cloud_config
except ImportError:
    # Fallback for when cloud config is not available
    cloud_config = None

try:
    from ..database import get_db
except ImportError:
    # Fallback for when database module is not available
    get_db = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cloud", tags=["cloud"])


class BackupRequest(BaseModel):
    backup_name: Optional[str] = None
    description: Optional[str] = None


class RestoreRequest(BaseModel):
    backup_name: str
    confirm: bool = False


class CloudConfigResponse(BaseModel):
    provider: str
    enabled: bool
    auto_backup: bool
    auto_scaling: bool
    monitoring: bool
    database_url: str
    redis_url: str


class BackupInfo(BaseModel):
    name: str
    size: int
    created_at: str
    uploaded: bool
    database_type: str


class CloudMetricsResponse(BaseModel):
    s3_bucket_size: Dict[str, Any]
    rds_metrics: List[Dict[str, Any]]
    connectivity: Dict[str, bool]


@router.get("/config", response_model=CloudConfigResponse)
async def get_cloud_config():
    """Get current cloud configuration"""
    try:
        config = cloud_config.config
        return CloudConfigResponse(
            provider=config.provider.value,
            enabled=config.enabled,
            auto_backup=config.auto_backup,
            auto_scaling=config.auto_scaling,
            monitoring=config.monitoring,
            database_url=cloud_config.get_database_url(),
            redis_url=cloud_config.get_redis_url()
        )
    except Exception as e:
        logger.error(f"Failed to get cloud config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cloud configuration")


@router.post("/backup", response_model=BackupInfo)
async def create_backup(request: BackupRequest, background_tasks: BackgroundTasks):
    """Create a new database backup"""
    try:
        backup_info = await backup_service.create_database_backup(request.backup_name)
        
        if 'error' in backup_info:
            raise HTTPException(status_code=500, detail=backup_info['error'])
        
        return BackupInfo(**backup_info)
        
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")


@router.get("/backups", response_model=List[Dict[str, Any]])
async def list_backups():
    """List all available backups"""
    try:
        backups = await backup_service.list_backups()
        return backups
    except Exception as e:
        logger.error(f"Failed to list backups: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list backups: {str(e)}")


@router.post("/restore")
async def restore_backup(request: RestoreRequest):
    """Restore database from backup"""
    try:
        if not request.confirm:
            raise HTTPException(status_code=400, detail="Restore requires confirmation")
        
        restore_info = await backup_service.restore_database_backup(request.backup_name)
        
        if 'error' in restore_info:
            raise HTTPException(status_code=500, detail=restore_info['error'])
        
        return restore_info
        
    except Exception as e:
        logger.error(f"Failed to restore backup: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restore backup: {str(e)}")


@router.delete("/backups/cleanup")
async def cleanup_old_backups():
    """Clean up old backups based on retention policy"""
    try:
        deleted_count = await backup_service.cleanup_old_backups()
        return {"deleted_count": deleted_count, "message": f"Cleaned up {deleted_count} old backups"}
    except Exception as e:
        logger.error(f"Failed to cleanup old backups: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup old backups: {str(e)}")


@router.get("/metrics", response_model=CloudMetricsResponse)
async def get_cloud_metrics():
    """Get cloud infrastructure metrics"""
    try:
        metrics = CloudMetricsResponse(
            s3_bucket_size={},
            rds_metrics=[],
            connectivity={}
        )
        
        # Get AWS metrics if configured
        if cloud_config.config.provider.value == 'aws' and cloud_config.config.aws:
            aws_manager = AWSManager()
            
            # Get S3 bucket size
            metrics.s3_bucket_size = aws_manager.get_s3_bucket_size()
            
            # Get RDS metrics if instance is configured
            if cloud_config.config.aws.rds_instance_id:
                cpu_metrics = aws_manager.get_rds_metrics(
                    cloud_config.config.aws.rds_instance_id, 
                    'CPUUtilization'
                )
                memory_metrics = aws_manager.get_rds_metrics(
                    cloud_config.config.aws.rds_instance_id, 
                    'FreeableMemory'
                )
                metrics.rds_metrics = cpu_metrics + memory_metrics
            
            # Test connectivity
            metrics.connectivity = aws_manager.test_aws_connectivity()
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get cloud metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cloud metrics: {str(e)}")


@router.post("/validate")
async def validate_cloud_config():
    """Validate cloud configuration"""
    try:
        validation_result = cloud_config.validate_config()
        return validation_result
    except Exception as e:
        logger.error(f"Failed to validate cloud config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate cloud config: {str(e)}")


@router.get("/health")
async def cloud_health_check():
    """Check cloud services health"""
    try:
        health_status = {
            "cloud_enabled": cloud_config.is_cloud_enabled(),
            "provider": cloud_config.config.provider.value,
            "database_connected": False,
            "redis_connected": False,
            "backup_service_available": False
        }
        
        # Test database connection
        try:
            db = get_db()
            # Simple query to test connection
            result = db.execute("SELECT 1")
            health_status["database_connected"] = True
        except Exception:
            pass
        
        # Test Redis connection
        try:
            import redis
            redis_url = cloud_config.get_redis_url()
            r = redis.from_url(redis_url)
            r.ping()
            health_status["redis_connected"] = True
        except Exception:
            pass
        
        # Test backup service
        try:
            backups = await backup_service.list_backups()
            health_status["backup_service_available"] = True
        except Exception:
            pass
        
        return health_status
        
    except Exception as e:
        logger.error(f"Failed to check cloud health: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check cloud health: {str(e)}")


@router.post("/backup/schedule")
async def schedule_backup(background_tasks: BackgroundTasks):
    """Schedule a background backup task"""
    try:
        background_tasks.add_task(backup_service.create_database_backup)
        return {"message": "Backup scheduled successfully"}
    except Exception as e:
        logger.error(f"Failed to schedule backup: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule backup: {str(e)}")


@router.get("/environment")
async def get_environment_vars():
    """Get cloud environment variables (without sensitive data)"""
    try:
        env_vars = cloud_config.get_environment_vars()
        
        # Remove sensitive information
        safe_env_vars = {}
        for key, value in env_vars.items():
            if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key']):
                safe_env_vars[key] = '***HIDDEN***'
            else:
                safe_env_vars[key] = value
        
        return safe_env_vars
        
    except Exception as e:
        logger.error(f"Failed to get environment variables: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get environment variables: {str(e)}")


@router.post("/backup/test")
async def test_backup_creation():
    """Test backup creation without actually creating a backup"""
    try:
        # Test configuration
        validation = cloud_config.validate_config()
        if not validation['valid']:
            return {
                "success": False,
                "errors": validation['errors'],
                "warnings": validation['warnings']
            }
        
        # Test connectivity
        health = await cloud_health_check()
        
        return {
            "success": True,
            "health": health,
            "config_valid": validation['valid'],
            "warnings": validation['warnings']
        }
        
    except Exception as e:
        logger.error(f"Failed to test backup creation: {e}")
        return {
            "success": False,
            "error": str(e)
        } 