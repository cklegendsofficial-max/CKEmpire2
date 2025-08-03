"""
Comprehensive monitoring and observability module for CK Empire Builder.
Includes Prometheus metrics, Sentry error tracking, and ELK stack integration.
"""

import os
import time
import structlog
from typing import Dict, Any, Optional
from contextlib import contextmanager
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, 
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, multiprocess
)
from prometheus_client.exposition import start_http_server
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json
from datetime import datetime
import threading
import queue

# Configure structured logging for ELK stack
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class MonitoringManager:
    """Central monitoring manager for CK Empire Builder"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self.metrics = {}
        self.es_client = None
        self.log_queue = queue.Queue()
        self.log_thread = None
        self._setup_prometheus_metrics()
        self._setup_sentry()
        self._setup_elasticsearch()
        self._start_log_worker()
    
    def _setup_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        # HTTP request metrics
        self.metrics['http_requests_total'] = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.metrics['http_request_duration_seconds'] = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Business metrics
        self.metrics['projects_total'] = Gauge(
            'projects_total',
            'Total number of projects',
            registry=self.registry
        )
        
        self.metrics['revenue_total'] = Gauge(
            'revenue_total',
            'Total revenue in USD',
            registry=self.registry
        )
        
        self.metrics['ai_requests_total'] = Counter(
            'ai_requests_total',
            'Total AI requests',
            ['model', 'endpoint'],
            registry=self.registry
        )
        
        self.metrics['ethics_checks_total'] = Counter(
            'ethics_checks_total',
            'Total ethics checks',
            ['result'],
            registry=self.registry
        )
        
        # System metrics
        self.metrics['database_connections'] = Gauge(
            'database_connections',
            'Number of active database connections',
            registry=self.registry
        )
        
        self.metrics['cloud_backups_total'] = Counter(
            'cloud_backups_total',
            'Total cloud backups',
            ['provider', 'status'],
            registry=self.registry
        )
        
        # Error metrics
        self.metrics['errors_total'] = Counter(
            'errors_total',
            'Total errors',
            ['type', 'endpoint'],
            registry=self.registry
        )
        
        # Performance metrics
        self.metrics['response_time_summary'] = Summary(
            'response_time_summary',
            'Response time summary',
            ['endpoint'],
            registry=self.registry
        )
        
        logger.info("Prometheus metrics initialized")
    
    def _setup_sentry(self):
        """Initialize Sentry for error tracking"""
        sentry_dsn = os.getenv('SENTRY_DSN')
        if sentry_dsn:
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[
                    FastApiIntegration(),
                    SqlalchemyIntegration(),
                    RedisIntegration(),
                ],
                traces_sample_rate=0.1,
                profiles_sample_rate=0.1,
                environment=os.getenv('ENVIRONMENT', 'development'),
                release=os.getenv('APP_VERSION', '1.0.0'),
            )
            logger.info("Sentry initialized successfully")
        else:
            logger.warning("SENTRY_DSN not found, Sentry disabled")
    
    def _setup_elasticsearch(self):
        """Initialize Elasticsearch for log aggregation"""
        es_host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
        es_port = int(os.getenv('ELASTICSEARCH_PORT', '9200'))
        
        try:
            self.es_client = Elasticsearch([f'http://{es_host}:{es_port}'])
            if self.es_client.ping():
                logger.info("Elasticsearch connection established")
            else:
                logger.warning("Elasticsearch connection failed")
                self.es_client = None
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            self.es_client = None
    
    def _start_log_worker(self):
        """Start background worker for sending logs to Elasticsearch"""
        if self.es_client:
            self.log_thread = threading.Thread(target=self._log_worker, daemon=True)
            self.log_thread.start()
            logger.info("Log worker started")
    
    def _log_worker(self):
        """Background worker for sending logs to Elasticsearch"""
        while True:
            try:
                log_entry = self.log_queue.get(timeout=1)
                if log_entry:
                    self._send_to_elasticsearch(log_entry)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Log worker error: {e}")
    
    def _send_to_elasticsearch(self, log_entry: Dict[str, Any]):
        """Send log entry to Elasticsearch"""
        if not self.es_client:
            return
        
        try:
            index_name = f"ckempire-logs-{datetime.now().strftime('%Y.%m.%d')}"
            self.es_client.index(
                index=index_name,
                body=log_entry
            )
        except Exception as e:
            logger.error(f"Failed to send log to Elasticsearch: {e}")
    
    def log_event(self, event_type: str, **kwargs):
        """Log an event to Elasticsearch"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'service': 'ckempire-backend',
            'environment': os.getenv('ENVIRONMENT', 'development'),
            **kwargs
        }
        
        if self.es_client:
            self.log_queue.put(log_entry)
        
        # Also log to structlog
        logger.info(f"Event: {event_type}", **kwargs)
    
    def record_http_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics"""
        self.metrics['http_requests_total'].labels(method=method, endpoint=endpoint, status=status).inc()
        self.metrics['http_request_duration_seconds'].labels(method=method, endpoint=endpoint).observe(duration)
        
        # Log to Elasticsearch
        self.log_event('http_request', 
                      method=method, 
                      endpoint=endpoint, 
                      status=status, 
                      duration=duration)
    
    def record_error(self, error_type: str, endpoint: str, error_message: str):
        """Record error metrics"""
        self.metrics['errors_total'].labels(type=error_type, endpoint=endpoint).inc()
        
        # Log to Elasticsearch
        self.log_event('error', 
                      error_type=error_type, 
                      endpoint=endpoint, 
                      error_message=error_message)
    
    def record_ai_request(self, model: str, endpoint: str):
        """Record AI request metrics"""
        self.metrics['ai_requests_total'].labels(model=model, endpoint=endpoint).inc()
        
        # Log to Elasticsearch
        self.log_event('ai_request', model=model, endpoint=endpoint)
    
    def record_ethics_check(self, result: str):
        """Record ethics check metrics"""
        self.metrics['ethics_checks_total'].labels(result=result).inc()
        
        # Log to Elasticsearch
        self.log_event('ethics_check', result=result)
    
    def update_business_metrics(self, projects_count: int, revenue: float):
        """Update business metrics"""
        self.metrics['projects_total'].set(projects_count)
        self.metrics['revenue_total'].set(revenue)
        
        # Log to Elasticsearch
        self.log_event('business_metrics', 
                      projects_count=projects_count, 
                      revenue=revenue)
    
    def record_cloud_backup(self, provider: str, status: str):
        """Record cloud backup metrics"""
        self.metrics['cloud_backups_total'].labels(provider=provider, status=status).inc()
        
        # Log to Elasticsearch
        self.log_event('cloud_backup', provider=provider, status=status)
    
    @contextmanager
    def measure_time(self, operation: str):
        """Context manager to measure operation time"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.log_event('operation_timing', operation=operation, duration=duration)
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics"""
        return generate_latest(self.registry)
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for monitoring components"""
        health_status = {
            'status': 'healthy',
            'components': {
                'prometheus': 'healthy',
                'sentry': 'healthy' if sentry_sdk.Hub.current.client else 'disabled',
                'elasticsearch': 'healthy' if self.es_client and self.es_client.ping() else 'unhealthy'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return health_status

# Global monitoring instance
monitoring = MonitoringManager()

def get_monitoring() -> MonitoringManager:
    """Get the global monitoring instance"""
    return monitoring 