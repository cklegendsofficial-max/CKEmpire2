#!/usr/bin/env python3
"""
Sentry Configuration for CK Empire
Handles error tracking, performance monitoring, and release tracking
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Sentry SDK import
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logging.warning("Sentry SDK not available. Error tracking will be disabled.")

class SentryConfig:
    """Sentry configuration manager"""
    
    def __init__(self):
        self.dsn = os.getenv("SENTRY_DSN")
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.release = os.getenv("RELEASE_VERSION", "1.0.0")
        self.traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
        self.profiles_sample_rate = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1"))
        
    def initialize_sentry(self) -> bool:
        """Initialize Sentry SDK"""
        if not SENTRY_AVAILABLE:
            logging.warning("Sentry SDK not available")
            return False
            
        if not self.dsn:
            logging.warning("SENTRY_DSN not set, Sentry disabled")
            return False
            
        try:
            # Configure Sentry SDK
            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                release=self.release,
                traces_sample_rate=self.traces_sample_rate,
                profiles_sample_rate=self.profiles_sample_rate,
                
                # Integrations
                integrations=[
                    FastApiIntegration(),
                    SqlalchemyIntegration(),
                    RedisIntegration(),
                    CeleryIntegration(),
                    LoggingIntegration(
                        level=logging.INFO,
                        event_level=logging.ERROR
                    ),
                ],
                
                # Before send callback
                before_send=self._before_send,
                
                # Before breadcrumb callback
                before_breadcrumb=self._before_breadcrumb,
                
                # Performance monitoring
                enable_tracing=True,
                
                # Debug mode for development
                debug=self.environment == "development",
                
                # Send default PII
                send_default_pii=False,
                
                # Auto session tracking
                auto_session_tracking=True,
                
                # Server name
                server_name=os.getenv("SERVER_NAME", "ckempire-backend"),
                
                # Max breadcrumbs
                max_breadcrumbs=50,
            )
            
            logging.info(f"Sentry initialized successfully for environment: {self.environment}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize Sentry: {e}")
            return False
    
    def _before_send(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Filter events before sending to Sentry"""
        try:
            # Filter out certain error types
            if "exception" in event:
                exception = event["exception"]
                if exception and "values" in exception:
                    for value in exception["values"]:
                        if "type" in value:
                            error_type = value["type"]
                            
                            # Filter out common noise
                            if any(noise in error_type.lower() for noise in [
                                "connectionrefused",
                                "timeout",
                                "brokenpipe",
                                "connectionreset"
                            ]):
                                return None
            
            # Add custom tags
            event.setdefault("tags", {}).update({
                "service": "ckempire-backend",
                "component": "api",
                "deployment": self.environment,
            })
            
            # Add custom context
            event.setdefault("contexts", {}).update({
                "app": {
                    "name": "CK Empire",
                    "version": self.release,
                    "environment": self.environment,
                },
                "runtime": {
                    "name": "python",
                    "version": os.getenv("PYTHON_VERSION", "3.11"),
                }
            })
            
            return event
            
        except Exception as e:
            logging.error(f"Error in before_send: {e}")
            return event
    
    def _before_breadcrumb(self, breadcrumb: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Filter breadcrumbs before sending to Sentry"""
        try:
            # Filter out sensitive data
            if "data" in breadcrumb:
                data = breadcrumb["data"]
                
                # Remove sensitive fields
                sensitive_fields = [
                    "password", "token", "secret", "key", "authorization",
                    "cookie", "session", "csrf", "api_key"
                ]
                
                for field in sensitive_fields:
                    if field in data:
                        data[field] = "[REDACTED]"
            
            # Add custom breadcrumb data
            breadcrumb.setdefault("data", {}).update({
                "service": "ckempire-backend",
                "timestamp": datetime.now().isoformat(),
            })
            
            return breadcrumb
            
        except Exception as e:
            logging.error(f"Error in before_breadcrumb: {e}")
            return breadcrumb
    
    def capture_exception(self, exc_info: Optional[tuple] = None, **kwargs) -> None:
        """Capture an exception"""
        if SENTRY_AVAILABLE and self.dsn:
            sentry_sdk.capture_exception(exc_info, **kwargs)
    
    def capture_message(self, message: str, level: str = "info", **kwargs) -> None:
        """Capture a message"""
        if SENTRY_AVAILABLE and self.dsn:
            sentry_sdk.capture_message(message, level, **kwargs)
    
    def set_user(self, user_id: str, email: Optional[str] = None, **kwargs) -> None:
        """Set user context"""
        if SENTRY_AVAILABLE and self.dsn:
            sentry_sdk.set_user({
                "id": user_id,
                "email": email,
                **kwargs
            })
    
    def set_tag(self, key: str, value: str) -> None:
        """Set a tag"""
        if SENTRY_AVAILABLE and self.dsn:
            sentry_sdk.set_tag(key, value)
    
    def set_context(self, name: str, data: Dict[str, Any]) -> None:
        """Set context data"""
        if SENTRY_AVAILABLE and self.dsn:
            sentry_sdk.set_context(name, data)
    
    def add_breadcrumb(self, message: str, category: str = "info", **kwargs) -> None:
        """Add a breadcrumb"""
        if SENTRY_AVAILABLE and self.dsn:
            sentry_sdk.add_breadcrumb(
                message=message,
                category=category,
                **kwargs
            )
    
    def start_transaction(self, name: str, op: str = "http.server") -> Any:
        """Start a performance transaction"""
        if SENTRY_AVAILABLE and self.dsn:
            return sentry_sdk.start_transaction(name=name, op=op)
        return None
    
    def set_extra(self, key: str, value: Any) -> None:
        """Set extra data"""
        if SENTRY_AVAILABLE and self.dsn:
            sentry_sdk.set_extra(key, value)
    
    def flush(self, timeout: float = 2.0) -> None:
        """Flush pending events"""
        if SENTRY_AVAILABLE and self.dsn:
            sentry_sdk.flush(timeout)
    
    def get_status(self) -> Dict[str, Any]:
        """Get Sentry status"""
        return {
            "enabled": SENTRY_AVAILABLE and bool(self.dsn),
            "environment": self.environment,
            "release": self.release,
            "traces_sample_rate": self.traces_sample_rate,
            "profiles_sample_rate": self.profiles_sample_rate,
            "dsn_configured": bool(self.dsn),
            "sdk_available": SENTRY_AVAILABLE,
        }

# Global Sentry configuration instance
sentry_config = SentryConfig() 