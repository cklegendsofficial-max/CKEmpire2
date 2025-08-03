"""
AWS Multi-Region Management
Handles AWS multi-region deployment, RDS Global replication, and region switching
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# AWS imports
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    from boto3.session import Session
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    logging.warning("AWS boto3 not available. Install with: pip install boto3")

from settings import settings

logger = logging.getLogger(__name__)

class RegionStatus(Enum):
    """Region status enum"""
    ACTIVE = "active"
    STANDBY = "standby"
    FAILED = "failed"
    MAINTENANCE = "maintenance"

class LoadBalancerType(Enum):
    """Load balancer type enum"""
    APPLICATION = "application"
    NETWORK = "network"
    GATEWAY = "gateway"

@dataclass
class RegionConfig:
    """Region configuration"""
    region_name: str
    endpoint: str
    weight: int
    status: RegionStatus
    rds_cluster_arn: Optional[str] = None
    elb_arn: Optional[str] = None
    vpc_id: Optional[str] = None
    subnet_ids: List[str] = None
    security_group_ids: List[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.subnet_ids is None:
            self.subnet_ids = []
        if self.security_group_ids is None:
            self.security_group_ids = []

@dataclass
class RDSGlobalCluster:
    """RDS Global Cluster configuration"""
    cluster_identifier: str
    engine: str
    engine_version: str
    database_name: str
    master_username: str
    storage_encrypted: bool
    deletion_protection: bool
    backup_retention_period: int
    preferred_backup_window: str
    preferred_maintenance_window: str
    regions: List[str]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class AWSMultiRegionManager:
    """AWS Multi-Region deployment and management"""
    
    def __init__(self):
        self.regions = {}
        self.current_primary_region = None
        self.rds_global_cluster = None
        self.load_balancer_config = {}
        
        if not AWS_AVAILABLE:
            logger.warning("AWS boto3 not available. Using mock responses.")
            return
        
        # Initialize AWS clients for different regions
        self.clients = {}
        self._initialize_aws_clients()
        
        # Load region configurations
        self._load_region_configs()
    
    def _initialize_aws_clients(self):
        """Initialize AWS clients for all regions"""
        try:
            # Get available regions
            ec2_client = boto3.client('ec2', region_name='us-east-1')
            regions_response = ec2_client.describe_regions()
            
            for region in regions_response['Regions']:
                region_name = region['RegionName']
                try:
                    # Initialize clients for each region
                    self.clients[region_name] = {
                        'ec2': boto3.client('ec2', region_name=region_name),
                        'rds': boto3.client('rds', region_name=region_name),
                        'elbv2': boto3.client('elbv2', region_name=region_name),
                        'route53': boto3.client('route53'),
                        'cloudwatch': boto3.client('cloudwatch', region_name=region_name),
                        'autoscaling': boto3.client('autoscaling', region_name=region_name)
                    }
                    logger.info(f"Initialized AWS clients for region: {region_name}")
                except Exception as e:
                    logger.warning(f"Failed to initialize clients for region {region_name}: {e}")
            
            logger.info(f"Initialized AWS clients for {len(self.clients)} regions")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {e}")
    
    def _load_region_configs(self):
        """Load region configurations from environment"""
        regions_config = os.getenv('AWS_REGIONS', 'us-east-1,eu-west-1,ap-southeast-1,us-west-2')
        region_list = regions_config.split(',')
        
        for region in region_list:
            region = region.strip()
            weight = self._get_region_weight(region)
            endpoint = f"https://ckempire-{region.replace('-', '-')}.ckempire.com"
            
            self.regions[region] = RegionConfig(
                region_name=region,
                endpoint=endpoint,
                weight=weight,
                status=RegionStatus.STANDBY
            )
        
        # Set primary region
        self.current_primary_region = os.getenv('AWS_PRIMARY_REGION', 'us-east-1')
        if self.current_primary_region in self.regions:
            self.regions[self.current_primary_region].status = RegionStatus.ACTIVE
        
        logger.info(f"Loaded {len(self.regions)} region configurations")
    
    def _get_region_weight(self, region: str) -> int:
        """Get weight for region based on priority"""
        weights = {
            'us-east-1': 40,
            'eu-west-1': 30,
            'ap-southeast-1': 20,
            'us-west-2': 10
        }
        return weights.get(region, 10)
    
    async def create_rds_global_cluster(self, cluster_config: RDSGlobalCluster) -> bool:
        """
        Create RDS Global Cluster for multi-region replication
        
        Args:
            cluster_config: RDS Global Cluster configuration
            
        Returns:
            bool: Success status
        """
        try:
            if not AWS_AVAILABLE:
                logger.warning("AWS not available. Using mock RDS Global Cluster creation.")
                return True
            
            # Create global cluster in primary region
            primary_region = self.current_primary_region
            rds_client = self.clients[primary_region]['rds']
            
            # Create global cluster
            response = rds_client.create_global_cluster(
                GlobalClusterIdentifier=cluster_config.cluster_identifier,
                Engine=cluster_config.engine,
                EngineVersion=cluster_config.engine_version,
                DatabaseName=cluster_config.database_name,
                MasterUsername=cluster_config.master_username,
                MasterUserPassword=os.getenv('RDS_MASTER_PASSWORD', ''),
                StorageEncrypted=cluster_config.storage_encrypted,
                DeletionProtection=cluster_config.deletion_protection,
                BackupRetentionPeriod=cluster_config.backup_retention_period,
                PreferredBackupWindow=cluster_config.preferred_backup_window,
                PreferredMaintenanceWindow=cluster_config.preferred_maintenance_window
            )
            
            self.rds_global_cluster = cluster_config
            logger.info(f"Created RDS Global Cluster: {cluster_config.cluster_identifier}")
            
            # Create regional clusters
            for region in cluster_config.regions:
                if region != primary_region:
                    await self._create_regional_cluster(region, cluster_config)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create RDS Global Cluster: {e}")
            return False
    
    async def _create_regional_cluster(self, region: str, cluster_config: RDSGlobalCluster):
        """Create regional RDS cluster"""
        try:
            rds_client = self.clients[region]['rds']
            
            # Create regional cluster
            response = rds_client.create_db_cluster(
                DBClusterIdentifier=f"{cluster_config.cluster_identifier}-{region}",
                GlobalClusterIdentifier=cluster_config.cluster_identifier,
                Engine=cluster_config.engine,
                EngineVersion=cluster_config.engine_version,
                DatabaseName=cluster_config.database_name,
                MasterUsername=cluster_config.master_username,
                MasterUserPassword=os.getenv('RDS_MASTER_PASSWORD', ''),
                StorageEncrypted=cluster_config.storage_encrypted,
                DeletionProtection=cluster_config.deletion_protection,
                BackupRetentionPeriod=cluster_config.backup_retention_period,
                PreferredBackupWindow=cluster_config.preferred_backup_window,
                PreferredMaintenanceWindow=cluster_config.preferred_maintenance_window
            )
            
            logger.info(f"Created regional cluster in {region}")
            
        except Exception as e:
            logger.error(f"Failed to create regional cluster in {region}: {e}")
    
    async def setup_load_balancer(self, region: str, lb_type: LoadBalancerType = LoadBalancerType.APPLICATION) -> bool:
        """
        Setup load balancer for region
        
        Args:
            region: AWS region
            lb_type: Load balancer type
            
        Returns:
            bool: Success status
        """
        try:
            if not AWS_AVAILABLE:
                logger.warning("AWS not available. Using mock load balancer setup.")
                return True
            
            elbv2_client = self.clients[region]['elbv2']
            
            # Get VPC and subnet information
            vpc_id = await self._get_vpc_id(region)
            subnet_ids = await self._get_subnet_ids(region)
            security_group_id = await self._create_security_group(region, vpc_id)
            
            # Create load balancer
            if lb_type == LoadBalancerType.APPLICATION:
                response = elbv2_client.create_load_balancer(
                    Name=f"ckempire-alb-{region}",
                    Subnets=subnet_ids,
                    SecurityGroups=[security_group_id],
                    Scheme='internet-facing',
                    Type='application',
                    IpAddressType='ipv4',
                    Tags=[
                        {'Key': 'Name', 'Value': f'ckempire-alb-{region}'},
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Project', 'Value': 'ckempire'}
                    ]
                )
            else:
                response = elbv2_client.create_load_balancer(
                    Name=f"ckempire-nlb-{region}",
                    Subnets=subnet_ids,
                    Scheme='internet-facing',
                    Type='network',
                    IpAddressType='ipv4',
                    Tags=[
                        {'Key': 'Name', 'Value': f'ckempire-nlb-{region}'},
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Project', 'Value': 'ckempire'}
                    ]
                )
            
            lb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
            self.regions[region].elb_arn = lb_arn
            self.regions[region].vpc_id = vpc_id
            self.regions[region].subnet_ids = subnet_ids
            self.regions[region].security_group_ids = [security_group_id]
            
            logger.info(f"Created load balancer in {region}: {lb_arn}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup load balancer in {region}: {e}")
            return False
    
    async def _get_vpc_id(self, region: str) -> str:
        """Get default VPC ID for region"""
        try:
            ec2_client = self.clients[region]['ec2']
            response = ec2_client.describe_vpcs(
                Filters=[
                    {'Name': 'is-default', 'Values': ['true']}
                ]
            )
            return response['Vpcs'][0]['VpcId']
        except Exception as e:
            logger.error(f"Failed to get VPC ID for {region}: {e}")
            return ""
    
    async def _get_subnet_ids(self, region: str) -> List[str]:
        """Get subnet IDs for region"""
        try:
            ec2_client = self.clients[region]['ec2']
            vpc_id = await self._get_vpc_id(region)
            
            response = ec2_client.describe_subnets(
                Filters=[
                    {'Name': 'vpc-id', 'Values': [vpc_id]},
                    {'Name': 'state', 'Values': ['available']}
                ]
            )
            
            return [subnet['SubnetId'] for subnet in response['Subnets'][:3]]  # Use first 3 subnets
        except Exception as e:
            logger.error(f"Failed to get subnet IDs for {region}: {e}")
            return []
    
    async def _create_security_group(self, region: str, vpc_id: str) -> str:
        """Create security group for load balancer"""
        try:
            ec2_client = self.clients[region]['ec2']
            
            # Create security group
            response = ec2_client.create_security_group(
                GroupName=f'ckempire-alb-sg-{region}',
                Description=f'Security group for CK Empire ALB in {region}',
                VpcId=vpc_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'security-group',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'ckempire-alb-sg-{region}'},
                            {'Key': 'Environment', 'Value': 'production'},
                            {'Key': 'Project', 'Value': 'ckempire'}
                        ]
                    }
                ]
            )
            
            security_group_id = response['GroupId']
            
            # Add ingress rules
            ec2_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 443,
                        'ToPort': 443,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )
            
            logger.info(f"Created security group in {region}: {security_group_id}")
            return security_group_id
            
        except Exception as e:
            logger.error(f"Failed to create security group in {region}: {e}")
            return ""
    
    async def switch_primary_region(self, new_primary_region: str) -> bool:
        """
        Switch primary region for failover
        
        Args:
            new_primary_region: New primary region
            
        Returns:
            bool: Success status
        """
        try:
            if new_primary_region not in self.regions:
                logger.error(f"Region {new_primary_region} not found in configuration")
                return False
            
            # Update region statuses
            if self.current_primary_region:
                self.regions[self.current_primary_region].status = RegionStatus.STANDBY
            
            self.regions[new_primary_region].status = RegionStatus.ACTIVE
            self.current_primary_region = new_primary_region
            
            # Update Route53 routing
            await self._update_route53_routing()
            
            # Update RDS Global Cluster primary
            if self.rds_global_cluster:
                await self._update_rds_global_cluster_primary(new_primary_region)
            
            logger.info(f"Switched primary region to {new_primary_region}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch primary region: {e}")
            return False
    
    async def _update_route53_routing(self):
        """Update Route53 routing for region switch"""
        try:
            if not AWS_AVAILABLE:
                return
            
            route53_client = self.clients['us-east-1']['route53']  # Route53 is global
            
            # Get hosted zone
            hosted_zones = route53_client.list_hosted_zones_by_name(DNSName='ckempire.com')
            if not hosted_zones['HostedZones']:
                logger.warning("No hosted zone found for ckempire.com")
                return
            
            hosted_zone_id = hosted_zones['HostedZones'][0]['Id']
            
            # Update A record to point to new primary region
            primary_region = self.current_primary_region
            primary_endpoint = self.regions[primary_region].endpoint
            
            route53_client.change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch={
                    'Changes': [
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': 'ckempire.com',
                                'Type': 'A',
                                'AliasTarget': {
                                    'HostedZoneId': 'Z35SXDOTRQ7X7K',  # ALB hosted zone ID
                                    'DNSName': primary_endpoint,
                                    'EvaluateTargetHealth': True
                                }
                            }
                        }
                    ]
                }
            )
            
            logger.info(f"Updated Route53 routing to {primary_region}")
            
        except Exception as e:
            logger.error(f"Failed to update Route53 routing: {e}")
    
    async def _update_rds_global_cluster_primary(self, new_primary_region: str):
        """Update RDS Global Cluster primary region"""
        try:
            if not AWS_AVAILABLE or not self.rds_global_cluster:
                return
            
            rds_client = self.clients[new_primary_region]['rds']
            
            # Promote regional cluster to primary
            rds_client.modify_db_cluster(
                DBClusterIdentifier=f"{self.rds_global_cluster.cluster_identifier}-{new_primary_region}",
                GlobalClusterIdentifier=self.rds_global_cluster.cluster_identifier,
                ApplyImmediately=True
            )
            
            logger.info(f"Updated RDS Global Cluster primary to {new_primary_region}")
            
        except Exception as e:
            logger.error(f"Failed to update RDS Global Cluster primary: {e}")
    
    async def get_region_health(self, region: str) -> Dict[str, Any]:
        """
        Get health status of region
        
        Args:
            region: AWS region
            
        Returns:
            Dict with health information
        """
        try:
            if not AWS_AVAILABLE:
                return {
                    'region': region,
                    'status': 'unknown',
                    'load_balancer_healthy': False,
                    'rds_healthy': False,
                    'last_check': datetime.utcnow().isoformat()
                }
            
            health_info = {
                'region': region,
                'status': self.regions[region].status.value,
                'load_balancer_healthy': False,
                'rds_healthy': False,
                'last_check': datetime.utcnow().isoformat()
            }
            
            # Check load balancer health
            if self.regions[region].elb_arn:
                elbv2_client = self.clients[region]['elbv2']
                try:
                    response = elbv2_client.describe_load_balancers(
                        LoadBalancerArns=[self.regions[region].elb_arn]
                    )
                    if response['LoadBalancers']:
                        health_info['load_balancer_healthy'] = True
                except Exception as e:
                    logger.warning(f"Failed to check load balancer health in {region}: {e}")
            
            # Check RDS health
            if self.rds_global_cluster:
                rds_client = self.clients[region]['rds']
                try:
                    cluster_id = f"{self.rds_global_cluster.cluster_identifier}-{region}"
                    response = rds_client.describe_db_clusters(
                        DBClusterIdentifier=cluster_id
                    )
                    if response['DBClusters']:
                        cluster = response['DBClusters'][0]
                        health_info['rds_healthy'] = cluster['Status'] == 'available'
                except Exception as e:
                    logger.warning(f"Failed to check RDS health in {region}: {e}")
            
            return health_info
            
        except Exception as e:
            logger.error(f"Failed to get region health for {region}: {e}")
            return {
                'region': region,
                'status': 'failed',
                'load_balancer_healthy': False,
                'rds_healthy': False,
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }
    
    async def get_all_regions_health(self) -> List[Dict[str, Any]]:
        """Get health status of all regions"""
        health_reports = []
        for region in self.regions:
            health_info = await self.get_region_health(region)
            health_reports.append(health_info)
        return health_reports
    
    def get_current_primary_region(self) -> Optional[str]:
        """Get current primary region"""
        return self.current_primary_region
    
    def get_region_config(self, region: str) -> Optional[RegionConfig]:
        """Get region configuration"""
        return self.regions.get(region)
    
    def get_all_regions(self) -> List[str]:
        """Get all configured regions"""
        return list(self.regions.keys())

# Global instance
aws_multi_region_manager = AWSMultiRegionManager() 