"""
Logging configuration for CK Empire Builder
"""

import logging
import logging.config
import os
from datetime import datetime
from pathlib import Path
import structlog
from structlog.stdlib import LoggerFactory
from structlog.processors import JSONRenderer, TimeStamper, add_log_level

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Structured logging configuration
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        JSONRenderer()
    ],
    context_class=dict,
    logger_factory=LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Standard logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "structlog.stdlib.ProcessorFormatter",
            "processor": JSONRenderer(),
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "detailed",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "json",
            "filename": "logs/ckempire.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "json",
            "filename": "logs/errors.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "performance_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "logs/performance.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 3,
        },
        "security_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "WARNING",
            "formatter": "json",
            "filename": "logs/security.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "backend": {  # Application logger
            "handlers": ["console", "file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "backend.performance": {  # Performance logger
            "handlers": ["console", "performance_file"],
            "level": "INFO",
            "propagate": False,
        },
        "backend.security": {  # Security logger
            "handlers": ["console", "security_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "uvicorn": {  # Uvicorn logger
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "sqlalchemy": {  # SQLAlchemy logger
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": False,
        },
        "redis": {  # Redis logger
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

def setup_logging():
    """Setup logging configuration"""
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Create structured logger
    logger = structlog.get_logger()
    logger.info("Logging system initialized", 
                log_level="INFO",
                log_files=["ckempire.log", "errors.log", "performance.log", "security.log"])

def get_logger(name: str = None):
    """Get a structured logger"""
    return structlog.get_logger(name)

def log_performance_event(event_type: str, **kwargs):
    """Log performance events"""
    logger = get_logger("backend.performance")
    logger.info("Performance event", 
                event_type=event_type,
                timestamp=datetime.utcnow().isoformat(),
                **kwargs)

def log_security_event(event_type: str, severity: str = "INFO", **kwargs):
    """Log security events"""
    logger = get_logger("backend.security")
    log_method = getattr(logger, severity.lower(), logger.info)
    log_method("Security event",
               event_type=event_type,
               severity=severity,
               timestamp=datetime.utcnow().isoformat(),
               **kwargs)

def log_database_event(event_type: str, query: str = None, duration: float = None, **kwargs):
    """Log database events"""
    logger = get_logger("backend.database")
    logger.info("Database event",
                event_type=event_type,
                query=query,
                duration=duration,
                timestamp=datetime.utcnow().isoformat(),
                **kwargs)

def log_api_event(method: str, path: str, status_code: int, duration: float, **kwargs):
    """Log API events"""
    logger = get_logger("backend.api")
    logger.info("API request",
                method=method,
                path=path,
                status_code=status_code,
                duration=duration,
                timestamp=datetime.utcnow().isoformat(),
                **kwargs)

def log_cache_event(event_type: str, key: str = None, hit: bool = None, **kwargs):
    """Log cache events"""
    logger = get_logger("backend.cache")
    logger.info("Cache event",
                event_type=event_type,
                key=key,
                hit=hit,
                timestamp=datetime.utcnow().isoformat(),
                **kwargs)

# ELK Stack preparation functions
def format_for_elasticsearch(log_entry: dict) -> dict:
    """Format log entry for Elasticsearch"""
    return {
        "@timestamp": log_entry.get("timestamp", datetime.utcnow().isoformat()),
        "level": log_entry.get("level", "INFO"),
        "logger": log_entry.get("logger", "backend"),
        "message": log_entry.get("message", ""),
        "event_type": log_entry.get("event_type"),
        "duration": log_entry.get("duration"),
        "method": log_entry.get("method"),
        "path": log_entry.get("path"),
        "status_code": log_entry.get("status_code"),
        "query": log_entry.get("query"),
        "cache_key": log_entry.get("key"),
        "cache_hit": log_entry.get("hit"),
        "severity": log_entry.get("severity"),
        "client_ip": log_entry.get("client_ip"),
        "user_agent": log_entry.get("user_agent"),
        "user_id": log_entry.get("user_id"),
        "session_id": log_entry.get("session_id"),
        "correlation_id": log_entry.get("correlation_id"),
        "service_name": "ckempire-backend",
        "service_version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }

def create_logstash_config():
    """Create Logstash configuration for ELK stack"""
    logstash_config = """
input {
  file {
    path => "/path/to/ckempire/logs/*.log"
    type => "ckempire-logs"
    codec => json
  }
}

filter {
  if [type] == "ckempire-logs" {
    date {
      match => [ "@timestamp", "ISO8601" ]
    }
    
    if [event_type] == "api_request" {
      mutate {
        add_tag => [ "api" ]
      }
    }
    
    if [event_type] == "database_query" {
      mutate {
        add_tag => [ "database" ]
      }
    }
    
    if [event_type] == "cache_event" {
      mutate {
        add_tag => [ "cache" ]
      }
    }
    
    if [event_type] == "security_event" {
      mutate {
        add_tag => [ "security" ]
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "ckempire-logs-%{+YYYY.MM.dd}"
  }
}
"""
    return logstash_config

# Initialize logging when module is imported
setup_logging() 