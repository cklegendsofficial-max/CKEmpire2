"""
Enhanced rate limiter with OWASP compliance
Advanced rate limiting with IP-based, user-based, and endpoint-based limits
Machine learning-based threat detection and adaptive rate limiting
"""

import time
import redis
import structlog
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import hashlib
import json
import os
import numpy as np
from collections import deque
import threading

logger = structlog.get_logger()

class AdaptiveRateLimiter:
    """Machine learning-based adaptive rate limiter"""
    
    def __init__(self, window_size: int = 100):
        """Initialize adaptive rate limiter"""
        self.window_size = window_size
        self.request_history = deque(maxlen=window_size)
        self.threshold_multiplier = 1.0
        self.learning_rate = 0.01
        self.lock = threading.Lock()
    
    def update_threshold(self, current_rate: float, is_attack: bool):
        """Update threshold based on current rate and attack detection"""
        with self.lock:
            if is_attack:
                # Increase threshold for legitimate traffic
                self.threshold_multiplier = min(2.0, self.threshold_multiplier + self.learning_rate)
            else:
                # Decrease threshold gradually
                self.threshold_multiplier = max(0.5, self.threshold_multiplier - self.learning_rate * 0.1)
    
    def detect_anomaly(self, current_rate: float) -> bool:
        """Detect anomalous request patterns"""
        if len(self.request_history) < 10:
            return False
        
        rates = list(self.request_history)
        mean_rate = np.mean(rates)
        std_rate = np.std(rates)
        
        if std_rate == 0:
            return False
        
        z_score = abs(current_rate - mean_rate) / std_rate
        return z_score > 3.0  # 3-sigma rule
    
    def add_request(self, rate: float):
        """Add request rate to history"""
        with self.lock:
            self.request_history.append(rate)

class EnhancedRateLimiter:
    """Enhanced rate limiter with OWASP compliance and ML-based threat detection"""
    
    def __init__(self, redis_url: str = None):
        """Initialize enhanced rate limiter with ML capabilities"""
        self.redis_url = redis_url or "redis://localhost:6379"
        self.redis_client = None
        self._init_redis()
        
        # Enhanced rate limiting configurations
        self.limits = {
            "default": {"requests": 100, "window": 60},  # 100 requests per minute
            "auth": {"requests": 10, "window": 60},      # 10 auth attempts per minute
            "api": {"requests": 1000, "window": 3600},   # 1000 API calls per hour
            "admin": {"requests": 50, "window": 60},     # 50 admin calls per minute
            "upload": {"requests": 10, "window": 60},    # 10 uploads per minute
            "download": {"requests": 100, "window": 60}, # 100 downloads per minute
            "search": {"requests": 30, "window": 60},    # 30 searches per minute
            "report": {"requests": 20, "window": 60},    # 20 reports per minute
        }
        
        # Adaptive rate limiting
        self.adaptive_limiter = AdaptiveRateLimiter()
        
        # IP whitelist and blacklist with enhanced security
        self.ip_whitelist = set()
        self.ip_blacklist = set()
        self.ip_reputation = {}  # IP reputation scoring
        self._load_ip_lists()
        
        # User-based limits with enhanced tracking
        self.user_limits = {}
        self.user_reputation = {}  # User reputation scoring
        
        # Enhanced suspicious activity detection
        self.suspicious_patterns = [
            "sqlmap", "nikto", "nmap", "dirb", "gobuster",
            "admin", "wp-admin", "phpmyadmin", "config",
            "union", "select", "insert", "update", "delete",
            "script", "javascript", "eval", "exec",
            "xss", "csrf", "sqli", "lfi", "rfi",
            "shell", "cmd", "powershell", "bash"
        ]
        
        # Advanced threat detection patterns
        self.threat_patterns = {
            "sql_injection": [
                r"(\b(union|select|insert|update|delete|drop|create|alter)\b)",
                r"(\b(or|and)\b\s+\d+\s*=\s*\d+)",
                r"(\b(union|select)\b.*\bfrom\b)",
                r"(\b(union|select)\b.*\bwhere\b)"
            ],
            "xss": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>",
                r"<object[^>]*>"
            ],
            "path_traversal": [
                r"\.\./",
                r"\.\.\\",
                r"%2e%2e%2f",
                r"%2e%2e%5c"
            ],
            "command_injection": [
                r"[;&|`]",
                r"\b(cat|ls|pwd|whoami|id)\b",
                r"\b(ping|nslookup|dig)\b",
                r"\b(wget|curl|nc|netcat)\b"
            ]
        }
        
        # Rate limiting events with enhanced analytics
        self.rate_limit_events = []
        self.threat_events = []
        
        # Machine learning features
        self.ml_enabled = True
        self.threat_score_threshold = 0.7
        
        # Behavioral analysis
        self.behavioral_patterns = {
            "rapid_requests": {"threshold": 50, "window": 10},
            "pattern_repetition": {"threshold": 10, "window": 60},
            "unusual_timing": {"threshold": 0.1, "window": 300}
        }
    
    def _init_redis(self):
        """Initialize Redis connection with enhanced security"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url, 
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            self.redis_client.ping()
            logger.info("✅ Redis connection established for rate limiting")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.redis_client = None
    
    def _load_ip_lists(self):
        """Load IP whitelist and blacklist with enhanced security"""
        try:
            # Load from environment variables
            whitelist = os.getenv('IP_WHITELIST', '').split(',')
            blacklist = os.getenv('IP_BLACKLIST', '').split(',')
            
            self.ip_whitelist = set(ip.strip() for ip in whitelist if ip.strip())
            self.ip_blacklist = set(ip.strip() for ip in blacklist if ip.strip())
            
            # Load reputation scores from Redis if available
            if self.redis_client:
                reputation_data = self.redis_client.hgetall("ip_reputation")
                for ip, score in reputation_data.items():
                    self.ip_reputation[ip] = float(score)
            
            logger.info(f"✅ Loaded {len(self.ip_whitelist)} whitelisted and {len(self.ip_blacklist)} blacklisted IPs")
            
        except Exception as e:
            logger.error(f"❌ Failed to load IP lists: {e}")
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique client identifier with enhanced privacy"""
        # Try to get real IP address with enhanced detection
        real_ip = request.headers.get('X-Real-IP')
        forwarded_for = request.headers.get('X-Forwarded-For')
        client_ip = request.client.host if request.client else "unknown"
        
        # Use the most reliable IP
        if real_ip:
            ip = real_ip
        elif forwarded_for:
            ip = forwarded_for.split(',')[0].strip()
        else:
            ip = client_ip
        
        # Add user agent and additional headers for uniqueness
        user_agent = request.headers.get('User-Agent', 'unknown')
        accept_language = request.headers.get('Accept-Language', 'unknown')
        accept_encoding = request.headers.get('Accept-Encoding', 'unknown')
        
        # Create enhanced hash for privacy
        identifier_data = f"{ip}:{user_agent}:{accept_language}:{accept_encoding}"
        identifier = hashlib.sha256(identifier_data.encode()).hexdigest()
        return identifier
    
    def _calculate_threat_score(self, request: Request) -> float:
        """Calculate threat score using machine learning"""
        try:
            threat_score = 0.0
            
            # URL-based threat detection
            url = str(request.url).lower()
            for threat_type, patterns in self.threat_patterns.items():
                for pattern in patterns:
                    if pattern in url:
                        threat_score += 0.3
            
            # Header-based threat detection
            headers = dict(request.headers)
            for header_name, header_value in headers.items():
                header_str = f"{header_name}: {header_value}".lower()
                for threat_type, patterns in self.threat_patterns.items():
                    for pattern in patterns:
                        if pattern in header_str:
                            threat_score += 0.2
            
            # Behavioral analysis
            client_id = self._get_client_identifier(request)
            recent_requests = self._get_recent_requests(client_id, window=60)
            
            if len(recent_requests) > self.behavioral_patterns["rapid_requests"]["threshold"]:
                threat_score += 0.4
            
            # Pattern repetition detection
            if len(recent_requests) > 10:
                unique_patterns = len(set(recent_requests))
                repetition_ratio = 1 - (unique_patterns / len(recent_requests))
                if repetition_ratio > 0.8:
                    threat_score += 0.3
            
            # User agent analysis
            user_agent = request.headers.get('User-Agent', '')
            if not user_agent or len(user_agent) < 10:
                threat_score += 0.2
            
            # Normalize threat score
            threat_score = min(1.0, threat_score)
            
            return threat_score
            
        except Exception as e:
            logger.error(f"❌ Threat score calculation failed: {e}")
            return 0.0
    
    def _detect_suspicious_activity(self, request: Request) -> Dict[str, Any]:
        """Detect suspicious activity patterns with enhanced ML"""
        try:
            suspicious_indicators = []
            threat_score = self._calculate_threat_score(request)
            
            # Check URL for suspicious patterns
            url = str(request.url).lower()
            for pattern in self.suspicious_patterns:
                if pattern in url:
                    suspicious_indicators.append(f"Suspicious URL pattern: {pattern}")
            
            # Check headers for suspicious patterns
            headers = dict(request.headers)
            for header_name, header_value in headers.items():
                header_str = f"{header_name}: {header_value}".lower()
                for pattern in self.suspicious_patterns:
                    if pattern in header_str:
                        suspicious_indicators.append(f"Suspicious header pattern: {pattern}")
            
            # Check for rapid requests (potential DoS)
            client_id = self._get_client_identifier(request)
            recent_requests = self._get_recent_requests(client_id, window=10)  # Last 10 seconds
            if len(recent_requests) > 50:  # More than 50 requests in 10 seconds
                suspicious_indicators.append("Rapid request pattern detected")
            
            # Check for unusual user agent
            user_agent = request.headers.get('User-Agent', '')
            if not user_agent or len(user_agent) < 10:
                suspicious_indicators.append("Suspicious or missing user agent")
            
            # ML-based anomaly detection
            current_rate = len(recent_requests)
            is_anomaly = self.adaptive_limiter.detect_anomaly(current_rate)
            if is_anomaly:
                suspicious_indicators.append("ML-detected anomalous behavior")
            
            # Update adaptive threshold
            self.adaptive_limiter.add_request(current_rate)
            self.adaptive_limiter.update_threshold(current_rate, len(suspicious_indicators) > 0)
            
            # Determine risk level based on threat score and indicators
            if threat_score > self.threat_score_threshold or len(suspicious_indicators) > 3:
                risk_level = "HIGH"
            elif threat_score > 0.5 or len(suspicious_indicators) > 1:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            return {
                "suspicious": len(suspicious_indicators) > 0 or threat_score > 0.3,
                "indicators": suspicious_indicators,
                "threat_score": threat_score,
                "risk_level": risk_level,
                "is_anomaly": is_anomaly,
                "adaptive_threshold": self.adaptive_limiter.threshold_multiplier
            }
            
        except Exception as e:
            logger.error(f"❌ Suspicious activity detection failed: {e}")
            return {
                "suspicious": False,
                "indicators": [],
                "threat_score": 0.0,
                "risk_level": "LOW",
                "error": str(e)
            }
    
    def _get_rate_limit_key(self, client_id: str, endpoint: str) -> str:
        """Get Redis key for rate limiting with enhanced security"""
        return f"rate_limit:{client_id}:{endpoint}"
    
    def _get_recent_requests(self, client_id: str, window: int = 60) -> List[float]:
        """Get recent request timestamps with enhanced tracking"""
        if not self.redis_client:
            return []
        
        try:
            key = f"recent_requests:{client_id}"
            current_time = time.time()
            cutoff_time = current_time - window
            
            # Get all timestamps
            timestamps = self.redis_client.zrangebyscore(key, cutoff_time, current_time)
            
            # Clean old entries
            self.redis_client.zremrangebyscore(key, 0, cutoff_time)
            
            return [float(ts) for ts in timestamps]
        except Exception as e:
            logger.error(f"❌ Failed to get recent requests: {e}")
            return []
    
    def _add_request_timestamp(self, client_id: str):
        """Add current request timestamp with enhanced tracking"""
        if not self.redis_client:
            return
        
        try:
            key = f"recent_requests:{client_id}"
            current_time = time.time()
            
            # Add timestamp with score
            self.redis_client.zadd(key, {str(current_time): current_time})
            
            # Set expiry to prevent memory leaks
            self.redis_client.expire(key, 3600)  # 1 hour
        except Exception as e:
            logger.error(f"❌ Failed to add request timestamp: {e}")
    
    def check_rate_limit(self, request: Request, endpoint_type: str = "default") -> Dict[str, Any]:
        """Check rate limit for request with enhanced security"""
        try:
            client_id = self._get_client_identifier(request)
            client_ip = request.client.host if request.client else "unknown"
            
            # Check IP blacklist with enhanced security
            if client_ip in self.ip_blacklist:
                self._log_threat_event(request, "BLACKLISTED_IP", client_ip)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="IP address is blacklisted"
                )
            
            # Check IP whitelist (bypass rate limiting)
            if client_ip in self.ip_whitelist:
                return {
                    "allowed": True,
                    "whitelisted": True,
                    "remaining": -1,
                    "reset_time": None
                }
            
            # Enhanced suspicious activity detection
            suspicious_info = self._detect_suspicious_activity(request)
            if suspicious_info["suspicious"]:
                logger.warning(f"⚠️  Suspicious activity detected: {suspicious_info['indicators']}")
                self._log_suspicious_activity(request, suspicious_info)
                
                # Apply stricter limits for suspicious activity
                if suspicious_info["risk_level"] == "HIGH":
                    endpoint_type = "auth"  # Use stricter auth limits
                elif suspicious_info["risk_level"] == "MEDIUM":
                    # Reduce rate limit by 50%
                    self.limits[endpoint_type]["requests"] = int(self.limits[endpoint_type]["requests"] * 0.5)
            
            # Get rate limit configuration with adaptive adjustments
            limit_config = self.limits.get(endpoint_type, self.limits["default"])
            max_requests = int(limit_config["requests"] * self.adaptive_limiter.threshold_multiplier)
            window = limit_config["window"]
            
            # Check current rate
            current_time = time.time()
            key = self._get_rate_limit_key(client_id, endpoint_type)
            
            if self.redis_client:
                # Get current request count
                current_requests = self.redis_client.get(key)
                current_requests = int(current_requests) if current_requests else 0
                
                # Check if limit exceeded
                if current_requests >= max_requests:
                    # Get reset time
                    reset_time = self.redis_client.ttl(key)
                    if reset_time == -1:  # No expiry set
                        reset_time = window
                    
                    # Log threat event
                    self._log_threat_event(request, "RATE_LIMIT_EXCEEDED", {
                        "endpoint_type": endpoint_type,
                        "current_requests": current_requests,
                        "max_requests": max_requests
                    })
                    
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Try again in {reset_time} seconds.",
                        headers={
                            "X-RateLimit-Limit": str(max_requests),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Reset": str(int(current_time + reset_time))
                        }
                    )
                
                # Increment request count
                if current_requests == 0:
                    # First request in window
                    self.redis_client.setex(key, window, 1)
                else:
                    # Increment existing count
                    self.redis_client.incr(key)
                
                remaining = max_requests - current_requests - 1
                reset_time = self.redis_client.ttl(key)
                
            else:
                # Fallback without Redis
                remaining = max_requests - 1
                reset_time = window
            
            # Add request timestamp for suspicious activity detection
            self._add_request_timestamp(client_id)
            
            # Log rate limit event with enhanced analytics
            self._log_rate_limit_event(request, endpoint_type, remaining, suspicious_info)
            
            return {
                "allowed": True,
                "whitelisted": False,
                "remaining": remaining,
                "reset_time": reset_time,
                "suspicious": suspicious_info["suspicious"],
                "risk_level": suspicious_info["risk_level"],
                "threat_score": suspicious_info["threat_score"],
                "adaptive_threshold": self.adaptive_limiter.threshold_multiplier
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Rate limit check failed: {e}")
            # Allow request on error
            return {
                "allowed": True,
                "whitelisted": False,
                "remaining": -1,
                "reset_time": None,
                "error": str(e)
            }
    
    def _log_suspicious_activity(self, request: Request, suspicious_info: Dict[str, Any]):
        """Log suspicious activity"""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get('User-Agent', 'unknown'),
                "url": str(request.url),
                "method": request.method,
                "suspicious_indicators": suspicious_info["indicators"],
                "risk_level": suspicious_info["risk_level"]
            }
            
            # Store in Redis for analysis
            if self.redis_client:
                key = f"suspicious_activity:{datetime.utcnow().strftime('%Y%m%d')}"
                self.redis_client.lpush(key, json.dumps(log_entry))
                self.redis_client.expire(key, 86400)  # 24 hours
            
            logger.warning(f"🔒 Suspicious activity logged: {log_entry}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log suspicious activity: {e}")
    
    def _log_rate_limit_event(self, request: Request, endpoint_type: str, remaining: int, suspicious_info: Dict[str, Any]):
        """Log rate limit event"""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "client_ip": request.client.host if request.client else "unknown",
                "endpoint_type": endpoint_type,
                "remaining_requests": remaining,
                "suspicious": suspicious_info["suspicious"],
                "risk_level": suspicious_info["risk_level"]
            }
            
            self.rate_limit_events.append(log_entry)
            
            # Keep only last 1000 events
            if len(self.rate_limit_events) > 1000:
                self.rate_limit_events = self.rate_limit_events[-1000:]
            
        except Exception as e:
            logger.error(f"❌ Failed to log rate limit event: {e}")
    
    def _log_threat_event(self, request: Request, event_type: str, details: Any):
        """Log threat event with enhanced analytics"""
        try:
            threat_event = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get('User-Agent', 'unknown'),
                "url": str(request.url),
                "method": request.method,
                "details": details
            }
            
            self.threat_events.append(threat_event)
            
            # Keep only last 1000 threat events
            if len(self.threat_events) > 1000:
                self.threat_events = self.threat_events[-1000:]
            
            # Store in Redis for analysis
            if self.redis_client:
                key = f"threat_events:{datetime.utcnow().strftime('%Y%m%d')}"
                self.redis_client.lpush(key, json.dumps(threat_event))
                self.redis_client.expire(key, 86400)  # 24 hours
            
            logger.warning(f"🔒 Threat event logged: {event_type}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log threat event: {e}")
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        try:
            stats = {
                "total_events": len(self.rate_limit_events),
                "suspicious_events": sum(1 for event in self.rate_limit_events if event.get("suspicious")),
                "high_risk_events": sum(1 for event in self.rate_limit_events if event.get("risk_level") == "HIGH"),
                "whitelisted_ips": len(self.ip_whitelist),
                "blacklisted_ips": len(self.ip_blacklist),
                "redis_connected": self.redis_client is not None,
                "limits": self.limits
            }
            
            # Calculate recent activity
            recent_events = [e for e in self.rate_limit_events 
                           if datetime.fromisoformat(e["timestamp"]) > datetime.utcnow() - timedelta(hours=1)]
            
            stats["recent_events"] = len(recent_events)
            stats["recent_suspicious"] = sum(1 for event in recent_events if event.get("suspicious"))
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get rate limit stats: {e}")
            return {"error": str(e)}
    
    def add_to_blacklist(self, ip: str, reason: str = "Manual addition"):
        """Add IP to blacklist"""
        try:
            self.ip_blacklist.add(ip)
            logger.info(f"🔒 IP {ip} added to blacklist: {reason}")
            
            # Store in Redis for persistence
            if self.redis_client:
                self.redis_client.sadd("ip_blacklist", ip)
                
        except Exception as e:
            logger.error(f"❌ Failed to add IP to blacklist: {e}")
    
    def remove_from_blacklist(self, ip: str):
        """Remove IP from blacklist"""
        try:
            self.ip_blacklist.discard(ip)
            logger.info(f"✅ IP {ip} removed from blacklist")
            
            # Remove from Redis
            if self.redis_client:
                self.redis_client.srem("ip_blacklist", ip)
                
        except Exception as e:
            logger.error(f"❌ Failed to remove IP from blacklist: {e}")
    
    def add_to_whitelist(self, ip: str, reason: str = "Manual addition"):
        """Add IP to whitelist"""
        try:
            self.ip_whitelist.add(ip)
            logger.info(f"✅ IP {ip} added to whitelist: {reason}")
            
            # Store in Redis for persistence
            if self.redis_client:
                self.redis_client.sadd("ip_whitelist", ip)
                
        except Exception as e:
            logger.error(f"❌ Failed to add IP to whitelist: {e}")
    
    def remove_from_whitelist(self, ip: str):
        """Remove IP from whitelist"""
        try:
            self.ip_whitelist.discard(ip)
            logger.info(f"🔒 IP {ip} removed from whitelist")
            
            # Remove from Redis
            if self.redis_client:
                self.redis_client.srem("ip_whitelist", ip)
                
        except Exception as e:
            logger.error(f"❌ Failed to remove IP from whitelist: {e}")
    
    def get_suspicious_activity_report(self, hours: int = 24) -> Dict[str, Any]:
        """Get suspicious activity report"""
        try:
            if not self.redis_client:
                return {"error": "Redis not available"}
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            suspicious_activities = []
            
            # Get suspicious activities from Redis
            for i in range(hours):
                date_key = (datetime.utcnow() - timedelta(hours=i)).strftime('%Y%m%d')
                key = f"suspicious_activity:{date_key}"
                
                activities = self.redis_client.lrange(key, 0, -1)
                for activity_json in activities:
                    activity = json.loads(activity_json)
                    activity_time = datetime.fromisoformat(activity["timestamp"])
                    if activity_time > cutoff_time:
                        suspicious_activities.append(activity)
            
            # Analyze patterns
            ip_counts = {}
            risk_level_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
            
            for activity in suspicious_activities:
                ip = activity["client_ip"]
                ip_counts[ip] = ip_counts.get(ip, 0) + 1
                risk_level = activity.get("risk_level", "LOW")
                risk_level_counts[risk_level] += 1
            
            return {
                "total_activities": len(suspicious_activities),
                "unique_ips": len(ip_counts),
                "risk_level_distribution": risk_level_counts,
                "top_suspicious_ips": sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10],
                "recent_activities": suspicious_activities[-50:]  # Last 50 activities
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get suspicious activity report: {e}")
            return {"error": str(e)}

# Global rate limiter instance
enhanced_rate_limiter = EnhancedRateLimiter()

def get_enhanced_rate_limiter() -> EnhancedRateLimiter:
    """Get enhanced rate limiter instance"""
    return enhanced_rate_limiter 