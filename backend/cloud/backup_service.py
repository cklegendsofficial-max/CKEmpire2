import asyncio
import logging
import os
import tempfile
import gzip
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import subprocess

from .aws_manager import AWSManager
from config.cloud_config import cloud_config

logger = logging.getLogger(__name__)


class BackupService:
    """Cloud backup service for CK Empire Builder"""
    
    def __init__(self):
        self.cloud_config = cloud_config
        self.aws_manager = AWSManager() if self.cloud_config.config.provider.value == 'aws' else None
        
    async def create_database_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Create database backup and upload to cloud storage"""
        try:
            if not backup_name:
                backup_name = f"db-backup-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
            
            # Get database configuration
            db_url = self.cloud_config.get_database_url()
            
            # Create backup based on database type
            if 'postgresql' in db_url or 'postgres' in db_url:
                backup_data = await self._create_postgres_backup(db_url)
            elif 'sqlite' in db_url:
                backup_data = await self._create_sqlite_backup(db_url)
            else:
                raise ValueError(f"Unsupported database type: {db_url}")
            
            # Upload to cloud storage
            upload_success = await self._upload_backup(backup_data, f"{backup_name}.sql")
            
            backup_info = {
                'name': backup_name,
                'size': len(backup_data),
                'created_at': datetime.utcnow().isoformat(),
                'uploaded': upload_success,
                'database_type': 'postgresql' if 'postgresql' in db_url else 'sqlite'
            }
            
            logger.info(f"Created database backup: {backup_name}")
            return backup_info
            
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            return {
                'name': backup_name,
                'error': str(e),
                'created_at': datetime.utcnow().isoformat()
            }
    
    async def _create_postgres_backup(self, db_url: str) -> bytes:
        """Create PostgreSQL backup using pg_dump"""
        try:
            # Parse database URL
            from urllib.parse import urlparse
            parsed = urlparse(db_url)
            
            # Extract connection details
            host = parsed.hostname
            port = parsed.port or 5432
            database = parsed.path.lstrip('/')
            username = parsed.username
            password = parsed.password
            
            # Create pg_dump command
            cmd = [
                'pg_dump',
                f'--host={host}',
                f'--port={port}',
                f'--username={username}',
                f'--dbname={database}',
                '--format=custom',
                '--verbose'
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            # Execute pg_dump
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"pg_dump failed: {stderr.decode()}")
            
            return stdout
            
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL backup: {e}")
            raise
    
    async def _create_sqlite_backup(self, db_url: str) -> bytes:
        """Create SQLite backup"""
        try:
            # Extract database file path
            db_path = db_url.replace('sqlite:///', '').replace('sqlite://', '')
            
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"Database file not found: {db_path}")
            
            # Read database file
            with open(db_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Failed to create SQLite backup: {e}")
            raise
    
    async def _upload_backup(self, backup_data: bytes, filename: str) -> bool:
        """Upload backup to cloud storage"""
        try:
            if self.cloud_config.config.provider.value == 'aws':
                return self.aws_manager.upload_backup_to_s3(backup_data, filename)
            
            elif self.cloud_config.config.provider.value == 'gcp':
                return await self._upload_to_gcs(backup_data, filename)
            
            else:
                # Local backup
                return await self._save_local_backup(backup_data, filename)
                
        except Exception as e:
            logger.error(f"Failed to upload backup: {e}")
            return False
    
    async def _upload_to_gcs(self, backup_data: bytes, filename: str) -> bool:
        """Upload backup to Google Cloud Storage"""
        try:
            import google.cloud.storage as storage
            
            # Get GCP configuration
            gcp_config = self.cloud_config.config.gcp
            if not gcp_config:
                raise ValueError("GCP configuration not found")
            
            # Create storage client
            client = storage.Client(project=gcp_config.project_id)
            bucket = client.bucket(gcp_config.bucket_name)
            
            # Create blob and upload
            blob = bucket.blob(f"backups/{filename}")
            blob.upload_from_string(backup_data, content_type='application/octet-stream')
            
            logger.info(f"Uploaded backup to GCS: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload to GCS: {e}")
            return False
    
    async def _save_local_backup(self, backup_data: bytes, filename: str) -> bool:
        """Save backup to local storage"""
        try:
            backup_dir = os.getenv('BACKUP_DIR', './backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_path = os.path.join(backup_dir, filename)
            with open(backup_path, 'wb') as f:
                f.write(backup_data)
            
            logger.info(f"Saved local backup: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save local backup: {e}")
            return False
    
    async def restore_database_backup(self, backup_name: str) -> Dict[str, Any]:
        """Restore database from backup"""
        try:
            # Download backup
            backup_data = await self._download_backup(backup_name)
            if not backup_data:
                raise Exception(f"Failed to download backup: {backup_name}")
            
            # Get database configuration
            db_url = self.cloud_config.get_database_url()
            
            # Restore based on database type
            if 'postgresql' in db_url or 'postgres' in db_url:
                success = await self._restore_postgres_backup(backup_data, db_url)
            elif 'sqlite' in db_url:
                success = await self._restore_sqlite_backup(backup_data, db_url)
            else:
                raise ValueError(f"Unsupported database type: {db_url}")
            
            return {
                'backup_name': backup_name,
                'restored': success,
                'restored_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to restore database backup: {e}")
            return {
                'backup_name': backup_name,
                'error': str(e),
                'restored_at': datetime.utcnow().isoformat()
            }
    
    async def _download_backup(self, backup_name: str) -> Optional[bytes]:
        """Download backup from cloud storage"""
        try:
            if self.cloud_config.config.provider.value == 'aws':
                return self.aws_manager.download_backup_from_s3(backup_name)
            
            elif self.cloud_config.config.provider.value == 'gcp':
                return await self._download_from_gcs(backup_name)
            
            else:
                return await self._load_local_backup(backup_name)
                
        except Exception as e:
            logger.error(f"Failed to download backup: {e}")
            return None
    
    async def _download_from_gcs(self, backup_name: str) -> Optional[bytes]:
        """Download backup from Google Cloud Storage"""
        try:
            import google.cloud.storage as storage
            
            # Get GCP configuration
            gcp_config = self.cloud_config.config.gcp
            if not gcp_config:
                raise ValueError("GCP configuration not found")
            
            # Create storage client
            client = storage.Client(project=gcp_config.project_id)
            bucket = client.bucket(gcp_config.bucket_name)
            
            # Download blob
            blob = bucket.blob(f"backups/{backup_name}")
            return blob.download_as_bytes()
            
        except Exception as e:
            logger.error(f"Failed to download from GCS: {e}")
            return None
    
    async def _load_local_backup(self, backup_name: str) -> Optional[bytes]:
        """Load backup from local storage"""
        try:
            backup_dir = os.getenv('BACKUP_DIR', './backups')
            backup_path = os.path.join(backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            with open(backup_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Failed to load local backup: {e}")
            return None
    
    async def _restore_postgres_backup(self, backup_data: bytes, db_url: str) -> bool:
        """Restore PostgreSQL backup using pg_restore"""
        try:
            # Parse database URL
            from urllib.parse import urlparse
            parsed = urlparse(db_url)
            
            # Extract connection details
            host = parsed.hostname
            port = parsed.port or 5432
            database = parsed.path.lstrip('/')
            username = parsed.username
            password = parsed.password
            
            # Create pg_restore command
            cmd = [
                'pg_restore',
                f'--host={host}',
                f'--port={port}',
                f'--username={username}',
                f'--dbname={database}',
                '--clean',
                '--if-exists',
                '--verbose'
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            # Execute pg_restore
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            _, stderr = await process.communicate(input=backup_data)
            
            if process.returncode != 0:
                raise Exception(f"pg_restore failed: {stderr.decode()}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore PostgreSQL backup: {e}")
            return False
    
    async def _restore_sqlite_backup(self, backup_data: bytes, db_url: str) -> bool:
        """Restore SQLite backup"""
        try:
            # Extract database file path
            db_path = db_url.replace('sqlite:///', '').replace('sqlite://', '')
            
            # Create backup of existing database
            if os.path.exists(db_path):
                backup_path = f"{db_path}.backup.{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
                os.rename(db_path, backup_path)
            
            # Write new database file
            with open(db_path, 'wb') as f:
                f.write(backup_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore SQLite backup: {e}")
            return False
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        try:
            if self.cloud_config.config.provider.value == 'aws':
                return self.aws_manager.list_backups()
            
            elif self.cloud_config.config.provider.value == 'gcp':
                return await self._list_gcs_backups()
            
            else:
                return await self._list_local_backups()
                
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    async def _list_gcs_backups(self) -> List[Dict[str, Any]]:
        """List backups from Google Cloud Storage"""
        try:
            import google.cloud.storage as storage
            
            # Get GCP configuration
            gcp_config = self.cloud_config.config.gcp
            if not gcp_config:
                return []
            
            # Create storage client
            client = storage.Client(project=gcp_config.project_id)
            bucket = client.bucket(gcp_config.bucket_name)
            
            backups = []
            for blob in bucket.list_blobs(prefix='backups/'):
                backup_info = {
                    'name': blob.name.split('/')[-1],
                    'size': blob.size,
                    'last_modified': blob.updated,
                    'etag': blob.etag
                }
                backups.append(backup_info)
            
            return sorted(backups, key=lambda x: x['last_modified'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list GCS backups: {e}")
            return []
    
    async def _list_local_backups(self) -> List[Dict[str, Any]]:
        """List local backups"""
        try:
            backup_dir = os.getenv('BACKUP_DIR', './backups')
            
            if not os.path.exists(backup_dir):
                return []
            
            backups = []
            for filename in os.listdir(backup_dir):
                if filename.endswith('.sql'):
                    file_path = os.path.join(backup_dir, filename)
                    stat = os.stat(file_path)
                    
                    backup_info = {
                        'name': filename,
                        'size': stat.st_size,
                        'last_modified': datetime.fromtimestamp(stat.st_mtime),
                        'etag': str(stat.st_mtime)
                    }
                    backups.append(backup_info)
            
            return sorted(backups, key=lambda x: x['last_modified'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list local backups: {e}")
            return []
    
    async def cleanup_old_backups(self) -> int:
        """Clean up old backups based on retention policy"""
        try:
            if self.cloud_config.config.provider.value == 'aws':
                return self.aws_manager.cleanup_old_backups()
            
            elif self.cloud_config.config.provider.value == 'gcp':
                return await self._cleanup_gcs_backups()
            
            else:
                return await self._cleanup_local_backups()
                
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
            return 0
    
    async def _cleanup_gcs_backups(self) -> int:
        """Clean up old backups from Google Cloud Storage"""
        try:
            import google.cloud.storage as storage
            
            # Get GCP configuration
            gcp_config = self.cloud_config.config.gcp
            if not gcp_config:
                return 0
            
            # Create storage client
            client = storage.Client(project=gcp_config.project_id)
            bucket = client.bucket(gcp_config.bucket_name)
            
            retention_days = gcp_config.backup_retention_days
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            deleted_count = 0
            for blob in bucket.list_blobs(prefix='backups/'):
                if blob.updated.replace(tzinfo=None) < cutoff_date:
                    blob.delete()
                    deleted_count += 1
                    logger.info(f"Deleted old GCS backup: {blob.name}")
            
            logger.info(f"Cleaned up {deleted_count} old GCS backups")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup GCS backups: {e}")
            return 0
    
    async def _cleanup_local_backups(self) -> int:
        """Clean up old local backups"""
        try:
            backup_dir = os.getenv('BACKUP_DIR', './backups')
            retention_days = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            if not os.path.exists(backup_dir):
                return 0
            
            deleted_count = 0
            for filename in os.listdir(backup_dir):
                if filename.endswith('.sql'):
                    file_path = os.path.join(backup_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"Deleted old local backup: {filename}")
            
            logger.info(f"Cleaned up {deleted_count} old local backups")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup local backups: {e}")
            return 0


# Global backup service instance
backup_service = BackupService() 