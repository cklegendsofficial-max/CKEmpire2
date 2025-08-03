import boto3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError, NoCredentialsError
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BackupConfig:
    """
    Configuration class for AWS backup operations.
    
    This dataclass defines the configuration parameters for AWS backup operations,
    including bucket settings, retention policies, and encryption options.
    
    Attributes:
        bucket_name (str): The name of the S3 bucket for storing backups
        retention_days (int): Number of days to retain backups (default: 30)
        backup_prefix (str): Prefix for backup files in S3 (default: "ck-empire-backups")
        encryption (bool): Whether to enable encryption for backups (default: True)
        compression (bool): Whether to enable compression for backups (default: True)
    """
    bucket_name: str
    retention_days: int = 30
    backup_prefix: str = "ck-empire-backups"
    encryption: bool = True
    compression: bool = True


class AWSManager:
    """
    AWS service manager for CK Empire Builder.
    
    This class provides comprehensive AWS service management capabilities including:
    - S3 bucket operations for backup storage
    - RDS instance management and snapshots
    - CloudWatch metrics and monitoring
    - EC2 instance management
    - Security and encryption features
    
    The manager handles authentication, error handling, and provides a unified
    interface for all AWS operations used by the CK Empire Builder platform.
    
    Attributes:
        region_name (str): AWS region for all operations
        session (boto3.Session): Boto3 session for AWS authentication
        s3_client (boto3.client): S3 client for bucket operations
        rds_client (boto3.client): RDS client for database operations
        ec2_client (boto3.client): EC2 client for instance operations
        cloudwatch_client (boto3.client): CloudWatch client for metrics
        backup_config (BackupConfig): Configuration for backup operations
    """
    
    def __init__(self, region_name: str = None):
        """
        Initialize the AWS Manager with configuration and clients.
        
        Args:
            region_name (str, optional): AWS region name. Defaults to environment
                variable AWS_REGION or 'us-west-2'.
        
        Raises:
            NoCredentialsError: If AWS credentials are not configured
            Exception: If initialization fails
        """
        self.region_name = region_name or os.getenv('AWS_REGION', 'us-west-2')
        self.session = boto3.Session(region_name=self.region_name)
        
        # Initialize AWS clients
        self.s3_client = self.session.client('s3')
        self.rds_client = self.session.client('rds')
        self.ec2_client = self.session.client('ec2')
        self.cloudwatch_client = self.session.client('cloudwatch')
        
        # Backup configuration
        self.backup_config = BackupConfig(
            bucket_name=os.getenv('S3_BACKUP_BUCKET', 'ck-empire-backups'),
            retention_days=int(os.getenv('BACKUP_RETENTION_DAYS', '30')),
            backup_prefix=os.getenv('BACKUP_PREFIX', 'ck-empire-backups'),
            encryption=os.getenv('BACKUP_ENCRYPTION', 'true').lower() == 'true',
            compression=os.getenv('BACKUP_COMPRESSION', 'true').lower() == 'true'
        )
    
    def create_s3_bucket(self, bucket_name: str) -> bool:
        """
        Create an S3 bucket for storing backups with security features.
        
        This method creates a new S3 bucket with the following security features:
        - Server-side encryption enabled
        - Versioning enabled for backup protection
        - Proper access controls and policies
        
        Args:
            bucket_name (str): The name of the bucket to create
            
        Returns:
            bool: True if bucket creation was successful, False otherwise
            
        Raises:
            ClientError: If bucket creation fails due to AWS API errors
            Exception: For other unexpected errors during bucket creation
        """
        try:
            # Create the bucket with proper configuration
            self.s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': self.region_name
                }
            )
            
            # Enable versioning for backup protection
            self.s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            # Enable server-side encryption
            self.s3_client.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }
                    ]
                }
            )
            
            logger.info(f"Successfully created S3 bucket: {bucket_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to create S3 bucket {bucket_name}: {e}")
            return False
    
    def upload_backup_to_s3(self, backup_data: bytes, backup_name: str) -> bool:
        """
        Upload backup data to S3 with compression and encryption.
        
        This method uploads backup data to S3 with the following features:
        - Optional compression using gzip
        - Server-side encryption
        - Metadata tracking for backup management
        - Proper error handling and logging
        
        Args:
            backup_data (bytes): The backup data to upload
            backup_name (str): The name for the backup file
            
        Returns:
            bool: True if upload was successful, False otherwise
            
        Raises:
            Exception: If upload fails due to network or AWS API errors
        """
        try:
            import gzip
            
            # Compress data if enabled in configuration
            if self.backup_config.compression:
                backup_data = gzip.compress(backup_data)
                backup_name += '.gz'
            
            # Upload to S3 with encryption and metadata
            self.s3_client.put_object(
                Bucket=self.backup_config.bucket_name,
                Key=f"{self.backup_config.backup_prefix}/{backup_name}",
                Body=backup_data,
                ServerSideEncryption='AES256' if self.backup_config.encryption else None,
                Metadata={
                    'backup-date': datetime.utcnow().isoformat(),
                    'compressed': str(self.backup_config.compression),
                    'encrypted': str(self.backup_config.encryption)
                }
            )
            
            logger.info(f"Successfully uploaded backup: {backup_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload backup {backup_name}: {e}")
            return False
    
    def download_backup_from_s3(self, backup_name: str) -> Optional[bytes]:
        """
        Download backup data from S3 with automatic decompression.
        
        This method downloads backup data from S3 and handles:
        - Automatic decompression of gzipped files
        - Error handling for missing files
        - Proper logging of download operations
        
        Args:
            backup_name (str): The name of the backup file to download
            
        Returns:
            Optional[bytes]: The downloaded backup data, or None if download fails
            
        Raises:
            Exception: If download fails due to network or AWS API errors
        """
        try:
            # Download the backup file from S3
            response = self.s3_client.get_object(
                Bucket=self.backup_config.bucket_name,
                Key=f"{self.backup_config.backup_prefix}/{backup_name}"
            )
            
            backup_data = response['Body'].read()
            
            # Decompress if the file is gzipped
            if backup_name.endswith('.gz'):
                import gzip
                backup_data = gzip.decompress(backup_data)
            
            logger.info(f"Successfully downloaded backup: {backup_name}")
            return backup_data
            
        except Exception as e:
            logger.error(f"Failed to download backup {backup_name}: {e}")
            return None
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups in S3 with metadata.
        
        This method retrieves a list of all backup files stored in S3 with
        their metadata including size, modification date, and ETag for
        integrity verification.
        
        Returns:
            List[Dict[str, Any]]: List of backup information dictionaries
                Each dictionary contains:
                - name (str): Backup file name
                - size (int): File size in bytes
                - last_modified (datetime): Last modification time
                - etag (str): ETag for integrity verification
                
        Raises:
            Exception: If listing fails due to network or AWS API errors
        """
        try:
            # List all objects in the backup prefix
            response = self.s3_client.list_objects_v2(
                Bucket=self.backup_config.bucket_name,
                Prefix=self.backup_config.backup_prefix
            )
            
            backups = []
            for obj in response.get('Contents', []):
                backup_info = {
                    'name': obj['Key'].split('/')[-1],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag']
                }
                backups.append(backup_info)
            
            # Sort by modification date, newest first
            return sorted(backups, key=lambda x: x['last_modified'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def cleanup_old_backups(self) -> int:
        """
        Clean up old backups based on retention policy.
        
        This method removes backup files that are older than the configured
        retention period. It helps manage storage costs and maintain a clean
        backup repository.
        
        Returns:
            int: Number of backups that were deleted
            
        Raises:
            Exception: If cleanup fails due to network or AWS API errors
        """
        try:
            backups = self.list_backups()
            cutoff_date = datetime.utcnow() - timedelta(days=self.backup_config.retention_days)
            
            deleted_count = 0
            for backup in backups:
                if backup['last_modified'].replace(tzinfo=None) < cutoff_date:
                    self.s3_client.delete_object(
                        Bucket=self.backup_config.bucket_name,
                        Key=f"{self.backup_config.backup_prefix}/{backup['name']}"
                    )
                    deleted_count += 1
                    logger.info(f"Deleted old backup: {backup['name']}")
            
            logger.info(f"Cleaned up {deleted_count} old backups")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
            return 0
    
    def create_rds_snapshot(self, db_instance_id: str, snapshot_name: str) -> bool:
        """
        Create an RDS snapshot for database backup.
        
        This method creates a point-in-time snapshot of an RDS database instance.
        Snapshots are useful for backup and disaster recovery purposes.
        
        Args:
            db_instance_id (str): The RDS instance identifier
            snapshot_name (str): The name for the snapshot
            
        Returns:
            bool: True if snapshot creation was initiated successfully, False otherwise
            
        Raises:
            ClientError: If snapshot creation fails due to AWS API errors
        """
        try:
            response = self.rds_client.create_db_snapshot(
                DBSnapshotIdentifier=snapshot_name,
                DBInstanceIdentifier=db_instance_id
            )
            
            logger.info(f"Created RDS snapshot: {snapshot_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to create RDS snapshot {snapshot_name}: {e}")
            return False
    
    def list_rds_snapshots(self, db_instance_id: str) -> List[Dict[str, Any]]:
        """
        List all RDS snapshots for a specific database instance.
        
        This method retrieves all snapshots associated with an RDS instance,
        including their status, creation time, and other metadata.
        
        Args:
            db_instance_id (str): The RDS instance identifier
            
        Returns:
            List[Dict[str, Any]]: List of snapshot information dictionaries
                Each dictionary contains:
                - snapshot_id (str): Snapshot identifier
                - instance_id (str): Associated instance identifier
                - status (str): Snapshot status
                - created_at (datetime): Creation time
                - engine (str): Database engine
                - allocated_storage (int): Storage size in GB
                
        Raises:
            ClientError: If listing fails due to AWS API errors
        """
        try:
            response = self.rds_client.describe_db_snapshots(
                DBInstanceIdentifier=db_instance_id
            )
            
            snapshots = []
            for snapshot in response.get('DBSnapshots', []):
                snapshot_info = {
                    'snapshot_id': snapshot['DBSnapshotIdentifier'],
                    'instance_id': snapshot['DBInstanceIdentifier'],
                    'status': snapshot['Status'],
                    'created_at': snapshot['SnapshotCreateTime'],
                    'engine': snapshot['Engine'],
                    'allocated_storage': snapshot['AllocatedStorage']
                }
                snapshots.append(snapshot_info)
            
            # Sort by creation date, newest first
            return sorted(snapshots, key=lambda x: x['created_at'], reverse=True)
            
        except ClientError as e:
            logger.error(f"Failed to list RDS snapshots: {e}")
            return []
    
    def restore_from_rds_snapshot(self, snapshot_id: str, new_instance_id: str) -> bool:
        """
        Restore an RDS instance from a snapshot.
        
        This method creates a new RDS instance from an existing snapshot.
        The new instance will have the same configuration as the original
        instance at the time the snapshot was taken.
        
        Args:
            snapshot_id (str): The snapshot identifier to restore from
            new_instance_id (str): The identifier for the new instance
            
        Returns:
            bool: True if restore was initiated successfully, False otherwise
            
        Raises:
            ClientError: If restore fails due to AWS API errors
        """
        try:
            # Get snapshot details to ensure it exists
            snapshot_response = self.rds_client.describe_db_snapshots(
                DBSnapshotIdentifier=snapshot_id
            )
            
            if not snapshot_response['DBSnapshots']:
                logger.error(f"Snapshot {snapshot_id} not found")
                return False
            
            snapshot = snapshot_response['DBSnapshots'][0]
            
            # Restore from snapshot with original configuration
            self.rds_client.restore_db_instance_from_db_snapshot(
                DBInstanceIdentifier=new_instance_id,
                DBSnapshotIdentifier=snapshot_id,
                DBInstanceClass=snapshot['DBInstanceClass'],
                AvailabilityZone=snapshot['AvailabilityZone'],
                MultiAZ=False,  # Start with single AZ for cost optimization
                PubliclyAccessible=False,
                AutoMinorVersionUpgrade=True,
                BackupRetentionPeriod=7,
                DeletionProtection=False
            )
            
            logger.info(f"Started restore from snapshot {snapshot_id} to {new_instance_id}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to restore from snapshot {snapshot_id}: {e}")
            return False
    
    def get_rds_metrics(self, db_instance_id: str, metric_name: str, period: int = 300) -> List[Dict[str, Any]]:
        """
        Get CloudWatch metrics for an RDS instance.
        
        This method retrieves performance metrics for an RDS instance from
        CloudWatch. Common metrics include CPU utilization, memory usage,
        and database connections.
        
        Args:
            db_instance_id (str): The RDS instance identifier
            metric_name (str): The CloudWatch metric name (e.g., 'CPUUtilization')
            period (int, optional): The metric period in seconds. Defaults to 300.
            
        Returns:
            List[Dict[str, Any]]: List of metric data points
                Each dictionary contains:
                - Timestamp (datetime): When the metric was recorded
                - Average (float): Average value for the period
                - Maximum (float): Maximum value for the period
                - Minimum (float): Minimum value for the period
                
        Raises:
            ClientError: If metric retrieval fails due to AWS API errors
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)
            
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName=metric_name,
                Dimensions=[
                    {
                        'Name': 'DBInstanceIdentifier',
                        'Value': db_instance_id
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=['Average', 'Maximum', 'Minimum']
            )
            
            return response.get('Datapoints', [])
            
        except ClientError as e:
            logger.error(f"Failed to get RDS metrics for {db_instance_id}: {e}")
            return []
    
    def create_cloudwatch_alarm(self, alarm_name: str, metric_name: str, 
                               db_instance_id: str, threshold: float) -> bool:
        """
        Create a CloudWatch alarm for RDS metrics.
        
        This method creates a CloudWatch alarm that monitors RDS metrics and
        can trigger notifications or actions when thresholds are exceeded.
        
        Args:
            alarm_name (str): The name for the CloudWatch alarm
            metric_name (str): The CloudWatch metric name to monitor
            db_instance_id (str): The RDS instance identifier
            threshold (float): The threshold value that triggers the alarm
            
        Returns:
            bool: True if alarm creation was successful, False otherwise
            
        Raises:
            ClientError: If alarm creation fails due to AWS API errors
        """
        try:
            self.cloudwatch_client.put_metric_alarm(
                AlarmName=alarm_name,
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=2,
                MetricName=metric_name,
                Namespace='AWS/RDS',
                Period=300,
                Statistic='Average',
                Threshold=threshold,
                ActionsEnabled=True,
                AlarmDescription=f'Alarm for {metric_name} on {db_instance_id}',
                Dimensions=[
                    {
                        'Name': 'DBInstanceIdentifier',
                        'Value': db_instance_id
                    }
                ]
            )
            
            logger.info(f"Created CloudWatch alarm: {alarm_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to create CloudWatch alarm {alarm_name}: {e}")
            return False
    
    def get_s3_bucket_size(self) -> Dict[str, Any]:
        """
        Get S3 bucket size and object count for backup storage.
        
        This method calculates the total size and object count of all backup
        files stored in the configured S3 bucket. This information is useful
        for monitoring storage usage and costs.
        
        Returns:
            Dict[str, Any]: Dictionary containing bucket statistics
                Keys include:
                - bucket_name (str): The S3 bucket name
                - total_size_bytes (int): Total size in bytes
                - total_size_mb (float): Total size in megabytes
                - object_count (int): Number of objects in the bucket
                
        Raises:
            Exception: If bucket size calculation fails
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.backup_config.bucket_name,
                Prefix=self.backup_config.backup_prefix
            )
            
            total_size = 0
            object_count = 0
            
            for obj in response.get('Contents', []):
                total_size += obj['Size']
                object_count += 1
            
            return {
                'bucket_name': self.backup_config.bucket_name,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'object_count': object_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get S3 bucket size: {e}")
            return {}
    
    def test_aws_connectivity(self) -> Dict[str, bool]:
        """
        Test connectivity to AWS services.
        
        This method tests the connectivity and authentication for various
        AWS services used by the CK Empire Builder platform. It helps
        diagnose connectivity issues and verify AWS credentials.
        
        Returns:
            Dict[str, bool]: Dictionary with connectivity test results
                Keys include:
                - s3 (bool): S3 connectivity status
                - rds (bool): RDS connectivity status
                - cloudwatch (bool): CloudWatch connectivity status
                
        Note:
            This method performs minimal API calls to test connectivity
            without affecting existing resources or incurring significant costs.
        """
        results = {
            's3': False,
            'rds': False,
            'cloudwatch': False
        }
        
        try:
            # Test S3 connectivity
            self.s3_client.head_bucket(Bucket=self.backup_config.bucket_name)
            results['s3'] = True
        except Exception:
            pass
        
        try:
            # Test RDS connectivity
            self.rds_client.describe_db_instances(MaxRecords=1)
            results['rds'] = True
        except Exception:
            pass
        
        try:
            # Test CloudWatch connectivity
            self.cloudwatch_client.list_metrics(Namespace='AWS/RDS', MaxResults=1)
            results['cloudwatch'] = True
        except Exception:
            pass
        
        return results 