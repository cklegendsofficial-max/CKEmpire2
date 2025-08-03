import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class CloudProvider(Enum):
    """Cloud provider enumeration"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    LOCAL = "local"


@dataclass
class AWSConfig:
    """AWS configuration settings"""
    region: str
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    s3_bucket: str = "ck-empire-backups"
    rds_instance_id: Optional[str] = None
    elasticache_endpoint: Optional[str] = None
    backup_retention_days: int = 30
    backup_encryption: bool = True
    backup_compression: bool = True


@dataclass
class GCPConfig:
    """Google Cloud Platform configuration settings"""
    project_id: str
    region: str
    zone: str
    bucket_name: str = "ck-empire-backups"
    sql_instance_name: Optional[str] = None
    redis_instance_name: Optional[str] = None
    backup_retention_days: int = 30


@dataclass
class CloudConfig:
    """Main cloud configuration"""
    provider: CloudProvider
    aws: Optional[AWSConfig] = None
    gcp: Optional[GCPConfig] = None
    enabled: bool = True
    auto_backup: bool = True
    auto_scaling: bool = True
    monitoring: bool = True


class CloudConfigManager:
    """Cloud configuration manager"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> CloudConfig:
        """Load cloud configuration from environment variables"""
        
        # Determine cloud provider
        provider_str = os.getenv('CLOUD_PROVIDER', 'local').lower()
        provider = CloudProvider(provider_str)
        
        config = CloudConfig(
            provider=provider,
            enabled=os.getenv('CLOUD_ENABLED', 'true').lower() == 'true',
            auto_backup=os.getenv('AUTO_BACKUP', 'true').lower() == 'true',
            auto_scaling=os.getenv('AUTO_SCALING', 'true').lower() == 'true',
            monitoring=os.getenv('CLOUD_MONITORING', 'true').lower() == 'true'
        )
        
        if provider == CloudProvider.AWS:
            config.aws = AWSConfig(
                region=os.getenv('AWS_REGION', 'us-west-2'),
                access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                s3_bucket=os.getenv('S3_BACKUP_BUCKET', 'ck-empire-backups'),
                rds_instance_id=os.getenv('RDS_INSTANCE_ID'),
                elasticache_endpoint=os.getenv('ELASTICACHE_ENDPOINT'),
                backup_retention_days=int(os.getenv('BACKUP_RETENTION_DAYS', '30')),
                backup_encryption=os.getenv('BACKUP_ENCRYPTION', 'true').lower() == 'true',
                backup_compression=os.getenv('BACKUP_COMPRESSION', 'true').lower() == 'true'
            )
        
        elif provider == CloudProvider.GCP:
            config.gcp = GCPConfig(
                project_id=os.getenv('GCP_PROJECT_ID', ''),
                region=os.getenv('GCP_REGION', 'us-west1'),
                zone=os.getenv('GCP_ZONE', 'us-west1-a'),
                bucket_name=os.getenv('GCS_BUCKET_NAME', 'ck-empire-backups'),
                sql_instance_name=os.getenv('GCP_SQL_INSTANCE_NAME'),
                redis_instance_name=os.getenv('GCP_REDIS_INSTANCE_NAME'),
                backup_retention_days=int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
            )
        
        return config
    
    def get_database_url(self) -> str:
        """Get database URL based on cloud configuration"""
        if self.config.provider == CloudProvider.AWS and self.config.aws:
            if self.config.aws.rds_instance_id:
                # Use RDS endpoint
                return f"postgresql://ckempire:{os.getenv('POSTGRES_PASSWORD')}@{self.config.aws.rds_instance_id}.{self.config.aws.region}.rds.amazonaws.com:5432/ckempire"
        
        elif self.config.provider == CloudProvider.GCP and self.config.gcp:
            if self.config.gcp.sql_instance_name:
                # Use Cloud SQL endpoint
                return f"postgresql://ckempire:{os.getenv('POSTGRES_PASSWORD')}@{self.config.gcp.sql_instance_name}.{self.config.gcp.region}.cloudsql.googleapis.com:5432/ckempire"
        
        # Fallback to local database
        return os.getenv('DATABASE_URL', 'sqlite:///./ckempire.db')
    
    def get_redis_url(self) -> str:
        """Get Redis URL based on cloud configuration"""
        if self.config.provider == CloudProvider.AWS and self.config.aws:
            if self.config.aws.elasticache_endpoint:
                return f"redis://:{os.getenv('REDIS_PASSWORD')}@{self.config.aws.elasticache_endpoint}:6379"
        
        elif self.config.provider == CloudProvider.GCP and self.config.gcp:
            if self.config.gcp.redis_instance_name:
                return f"redis://:{os.getenv('REDIS_PASSWORD')}@{self.config.gcp.redis_instance_name}.{self.config.gcp.region}.redis.googleapis.com:6379"
        
        # Fallback to local Redis
        return os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    def get_backup_config(self) -> Dict[str, Any]:
        """Get backup configuration"""
        if self.config.provider == CloudProvider.AWS and self.config.aws:
            return {
                'provider': 'aws',
                'bucket_name': self.config.aws.s3_bucket,
                'region': self.config.aws.region,
                'retention_days': self.config.aws.backup_retention_days,
                'encryption': self.config.aws.backup_encryption,
                'compression': self.config.aws.backup_compression
            }
        
        elif self.config.provider == CloudProvider.GCP and self.config.gcp:
            return {
                'provider': 'gcp',
                'bucket_name': self.config.gcp.bucket_name,
                'project_id': self.config.gcp.project_id,
                'region': self.config.gcp.region,
                'retention_days': self.config.gcp.backup_retention_days
            }
        
        return {
            'provider': 'local',
            'backup_dir': os.getenv('BACKUP_DIR', './backups'),
            'retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return {
            'enabled': self.config.monitoring,
            'provider': self.config.provider.value,
            'metrics_interval': int(os.getenv('METRICS_INTERVAL', '60')),
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'alerting': os.getenv('ALERTING_ENABLED', 'true').lower() == 'true'
        }
    
    def get_scaling_config(self) -> Dict[str, Any]:
        """Get auto-scaling configuration"""
        return {
            'enabled': self.config.auto_scaling,
            'min_replicas': int(os.getenv('MIN_REPLICAS', '2')),
            'max_replicas': int(os.getenv('MAX_REPLICAS', '10')),
            'cpu_threshold': int(os.getenv('CPU_THRESHOLD', '70')),
            'memory_threshold': int(os.getenv('MEMORY_THRESHOLD', '80')),
            'scale_up_cooldown': int(os.getenv('SCALE_UP_COOLDOWN', '60')),
            'scale_down_cooldown': int(os.getenv('SCALE_DOWN_COOLDOWN', '300'))
        }
    
    def is_cloud_enabled(self) -> bool:
        """Check if cloud features are enabled"""
        return self.config.enabled and self.config.provider != CloudProvider.LOCAL
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Get environment variables for cloud configuration"""
        env_vars = {
            'CLOUD_PROVIDER': self.config.provider.value,
            'CLOUD_ENABLED': str(self.config.enabled).lower(),
            'AUTO_BACKUP': str(self.config.auto_backup).lower(),
            'AUTO_SCALING': str(self.config.auto_scaling).lower(),
            'CLOUD_MONITORING': str(self.config.monitoring).lower(),
            'DATABASE_URL': self.get_database_url(),
            'REDIS_URL': self.get_redis_url()
        }
        
        if self.config.provider == CloudProvider.AWS and self.config.aws:
            env_vars.update({
                'AWS_REGION': self.config.aws.region,
                'S3_BACKUP_BUCKET': self.config.aws.s3_bucket,
                'BACKUP_RETENTION_DAYS': str(self.config.aws.backup_retention_days),
                'BACKUP_ENCRYPTION': str(self.config.aws.backup_encryption).lower(),
                'BACKUP_COMPRESSION': str(self.config.aws.backup_compression).lower()
            })
            
            if self.config.aws.rds_instance_id:
                env_vars['RDS_INSTANCE_ID'] = self.config.aws.rds_instance_id
            
            if self.config.aws.elasticache_endpoint:
                env_vars['ELASTICACHE_ENDPOINT'] = self.config.aws.elasticache_endpoint
        
        elif self.config.provider == CloudProvider.GCP and self.config.gcp:
            env_vars.update({
                'GCP_PROJECT_ID': self.config.gcp.project_id,
                'GCP_REGION': self.config.gcp.region,
                'GCP_ZONE': self.config.gcp.zone,
                'GCS_BUCKET_NAME': self.config.gcp.bucket_name,
                'BACKUP_RETENTION_DAYS': str(self.config.gcp.backup_retention_days)
            })
            
            if self.config.gcp.sql_instance_name:
                env_vars['GCP_SQL_INSTANCE_NAME'] = self.config.gcp.sql_instance_name
            
            if self.config.gcp.redis_instance_name:
                env_vars['GCP_REDIS_INSTANCE_NAME'] = self.config.gcp.redis_instance_name
        
        return env_vars
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate cloud configuration"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        if not self.config.enabled:
            validation_result['warnings'].append("Cloud features are disabled")
            return validation_result
        
        if self.config.provider == CloudProvider.AWS:
            if not self.config.aws:
                validation_result['errors'].append("AWS configuration is missing")
                validation_result['valid'] = False
            else:
                if not self.config.aws.region:
                    validation_result['errors'].append("AWS region is not configured")
                    validation_result['valid'] = False
                
                if not self.config.aws.s3_bucket:
                    validation_result['errors'].append("S3 bucket is not configured")
                    validation_result['valid'] = False
        
        elif self.config.provider == CloudProvider.GCP:
            if not self.config.gcp:
                validation_result['errors'].append("GCP configuration is missing")
                validation_result['valid'] = False
            else:
                if not self.config.gcp.project_id:
                    validation_result['errors'].append("GCP project ID is not configured")
                    validation_result['valid'] = False
                
                if not self.config.gcp.region:
                    validation_result['errors'].append("GCP region is not configured")
                    validation_result['valid'] = False
        
        return validation_result


# Global cloud configuration instance
cloud_config = CloudConfigManager() 