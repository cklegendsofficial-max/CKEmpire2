"""
Penetration testing simulation module
OWASP compliant security testing automation
"""

import requests
import json
import time
import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = structlog.get_logger()

class PenetrationTester:
    """Penetration testing simulation with OWASP compliance"""
    
    def __init__(self, target_url: str = None):
        """Initialize penetration tester"""
        self.target_url = target_url or "http://localhost:8000"
        self.report_dir = Path("penetration_reports")
        self.report_dir.mkdir(exist_ok=True)
        
        # Test configurations
        self.test_configs = {
            "sql_injection": {
                "enabled": True,
                "payloads": [
                    "' OR '1'='1",
                    "'; DROP TABLE users; --",
                    "' UNION SELECT * FROM users --",
                    "admin'--",
                    "1' OR '1'='1'--"
                ]
            },
            "xss": {
                "enabled": True,
                "payloads": [
                    "<script>alert('XSS')</script>",
                    "<img src=x onerror=alert('XSS')>",
                    "javascript:alert('XSS')",
                    "<svg onload=alert('XSS')>",
                    "';alert('XSS');//"
                ]
            },
            "csrf": {
                "enabled": True,
                "test_endpoints": [
                    "/api/v1/projects",
                    "/api/v1/revenue",
                    "/api/v1/users"
                ]
            },
            "authentication": {
                "enabled": True,
                "test_users": [
                    {"username": "admin", "password": "admin"},
                    {"username": "test", "password": "test"},
                    {"username": "user", "password": "password"}
                ]
            },
            "authorization": {
                "enabled": True,
                "test_endpoints": [
                    "/api/v1/admin",
                    "/api/v1/config",
                    "/api/v1/users",
                    "/api/v1/system"
                ]
            },
            "information_disclosure": {
                "enabled": True,
                "sensitive_paths": [
                    "/.env",
                    "/config.php",
                    "/wp-config.php",
                    "/.git/config",
                    "/robots.txt",
                    "/sitemap.xml"
                ]
            },
            "directory_traversal": {
                "enabled": True,
                "payloads": [
                    "../../../etc/passwd",
                    "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
                    "....//....//....//etc/passwd",
                    "..%2F..%2F..%2Fetc%2Fpasswd"
                ]
            },
            "command_injection": {
                "enabled": True,
                "payloads": [
                    "; ls -la",
                    "| whoami",
                    "&& cat /etc/passwd",
                    "; ping -c 1 127.0.0.1",
                    "`id`"
                ]
            }
        }
        
        # Session for maintaining cookies/auth
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CKEmpire-PenTester/1.0'
        })
        
        # Test results
        self.test_results = []
        self.vulnerabilities_found = []
    
    def run_full_penetration_test(self) -> Dict[str, Any]:
        """Run comprehensive penetration test"""
        try:
            logger.info("🔍 Starting comprehensive penetration test...")
            
            start_time = datetime.utcnow()
            
            # Run all test categories
            test_results = {
                "sql_injection": self._test_sql_injection(),
                "xss": self._test_xss(),
                "csrf": self._test_csrf(),
                "authentication": self._test_authentication(),
                "authorization": self._test_authorization(),
                "information_disclosure": self._test_information_disclosure(),
                "directory_traversal": self._test_directory_traversal(),
                "command_injection": self._test_command_injection(),
                "api_security": self._test_api_security(),
                "headers_security": self._test_headers_security()
            }
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Calculate overall security score
            total_vulnerabilities = sum(len(result.get("vulnerabilities", [])) for result in test_results.values())
            security_score = max(0, 100 - (total_vulnerabilities * 10))
            
            # Generate comprehensive report
            report = {
                "test_timestamp": start_time.isoformat(),
                "duration_seconds": duration,
                "target_url": self.target_url,
                "overall_security_score": security_score,
                "total_vulnerabilities": total_vulnerabilities,
                "test_results": test_results,
                "recommendations": self._generate_security_recommendations(test_results),
                "risk_assessment": self._assess_overall_risk(test_results)
            }
            
            # Save report
            report_file = self.report_dir / f"penetration_test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"✅ Penetration test completed - Score: {security_score}, Vulnerabilities: {total_vulnerabilities}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Penetration test failed: {e}")
            return {"error": str(e)}
    
    def _test_sql_injection(self) -> Dict[str, Any]:
        """Test for SQL injection vulnerabilities"""
        try:
            logger.info("🔍 Testing SQL injection vulnerabilities...")
            
            vulnerabilities = []
            test_endpoints = [
                f"{self.target_url}/api/v1/projects",
                f"{self.target_url}/api/v1/users",
                f"{self.target_url}/api/v1/revenue"
            ]
            
            for endpoint in test_endpoints:
                for payload in self.test_configs["sql_injection"]["payloads"]:
                    try:
                        # Test GET parameters
                        response = self.session.get(f"{endpoint}?id={payload}", timeout=5)
                        
                        # Check for SQL error indicators
                        error_indicators = [
                            "sql syntax", "mysql", "oracle", "postgresql",
                            "sqlite", "microsoft", "syntax error", "mysql_fetch"
                        ]
                        
                        response_text = response.text.lower()
                        for indicator in error_indicators:
                            if indicator in response_text:
                                vulnerabilities.append({
                                    "type": "SQL Injection",
                                    "endpoint": endpoint,
                                    "payload": payload,
                                    "method": "GET",
                                    "severity": "HIGH",
                                    "evidence": f"SQL error indicator found: {indicator}"
                                })
                                break
                        
                        # Test POST parameters
                        response = self.session.post(endpoint, data={"id": payload}, timeout=5)
                        response_text = response.text.lower()
                        
                        for indicator in error_indicators:
                            if indicator in response_text:
                                vulnerabilities.append({
                                    "type": "SQL Injection",
                                    "endpoint": endpoint,
                                    "payload": payload,
                                    "method": "POST",
                                    "severity": "HIGH",
                                    "evidence": f"SQL error indicator found: {indicator}"
                                })
                                break
                        
                    except Exception as e:
                        logger.debug(f"SQL injection test failed for {endpoint}: {e}")
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": len(test_endpoints) * len(self.test_configs["sql_injection"]["payloads"]) * 2,
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ SQL injection test failed: {e}")
            return {"error": str(e)}
    
    def _test_xss(self) -> Dict[str, Any]:
        """Test for XSS vulnerabilities"""
        try:
            logger.info("🔍 Testing XSS vulnerabilities...")
            
            vulnerabilities = []
            test_endpoints = [
                f"{self.target_url}/api/v1/projects",
                f"{self.target_url}/api/v1/content"
            ]
            
            for endpoint in test_endpoints:
                for payload in self.test_configs["xss"]["payloads"]:
                    try:
                        # Test reflected XSS
                        response = self.session.get(f"{endpoint}?search={payload}", timeout=5)
                        
                        if payload in response.text:
                            vulnerabilities.append({
                                "type": "Reflected XSS",
                                "endpoint": endpoint,
                                "payload": payload,
                                "method": "GET",
                                "severity": "HIGH",
                                "evidence": "Payload reflected in response"
                            })
                        
                        # Test stored XSS
                        response = self.session.post(endpoint, data={"content": payload}, timeout=5)
                        
                        # Check if payload is stored
                        stored_response = self.session.get(endpoint, timeout=5)
                        if payload in stored_response.text:
                            vulnerabilities.append({
                                "type": "Stored XSS",
                                "endpoint": endpoint,
                                "payload": payload,
                                "method": "POST",
                                "severity": "HIGH",
                                "evidence": "Payload stored and reflected"
                            })
                        
                    except Exception as e:
                        logger.debug(f"XSS test failed for {endpoint}: {e}")
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": len(test_endpoints) * len(self.test_configs["xss"]["payloads"]) * 2,
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ XSS test failed: {e}")
            return {"error": str(e)}
    
    def _test_csrf(self) -> Dict[str, Any]:
        """Test for CSRF vulnerabilities"""
        try:
            logger.info("🔍 Testing CSRF vulnerabilities...")
            
            vulnerabilities = []
            
            for endpoint in self.test_configs["csrf"]["test_endpoints"]:
                try:
                    # Test if CSRF protection is missing
                    response = self.session.post(f"{self.target_url}{endpoint}", 
                                               data={"test": "data"}, timeout=5)
                    
                    # Check if request was accepted without CSRF token
                    if response.status_code in [200, 201]:
                        vulnerabilities.append({
                            "type": "CSRF",
                            "endpoint": endpoint,
                            "method": "POST",
                            "severity": "MEDIUM",
                            "evidence": "Request accepted without CSRF protection"
                        })
                    
                except Exception as e:
                    logger.debug(f"CSRF test failed for {endpoint}: {e}")
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": len(self.test_configs["csrf"]["test_endpoints"]),
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ CSRF test failed: {e}")
            return {"error": str(e)}
    
    def _test_authentication(self) -> Dict[str, Any]:
        """Test authentication vulnerabilities"""
        try:
            logger.info("🔍 Testing authentication vulnerabilities...")
            
            vulnerabilities = []
            
            for user in self.test_configs["authentication"]["test_users"]:
                try:
                    # Test weak credentials
                    response = self.session.post(f"{self.target_url}/api/v1/auth/login", 
                                               json=user, timeout=5)
                    
                    if response.status_code == 200:
                        vulnerabilities.append({
                            "type": "Weak Authentication",
                            "username": user["username"],
                            "password": user["password"],
                            "severity": "HIGH",
                            "evidence": "Weak credentials accepted"
                        })
                    
                except Exception as e:
                    logger.debug(f"Authentication test failed for {user['username']}: {e}")
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": len(self.test_configs["authentication"]["test_users"]),
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ Authentication test failed: {e}")
            return {"error": str(e)}
    
    def _test_authorization(self) -> Dict[str, Any]:
        """Test authorization vulnerabilities"""
        try:
            logger.info("🔍 Testing authorization vulnerabilities...")
            
            vulnerabilities = []
            
            for endpoint in self.test_configs["authorization"]["test_endpoints"]:
                try:
                    # Test unauthorized access
                    response = self.session.get(f"{self.target_url}{endpoint}", timeout=5)
                    
                    if response.status_code == 200:
                        vulnerabilities.append({
                            "type": "Authorization Bypass",
                            "endpoint": endpoint,
                            "method": "GET",
                            "severity": "HIGH",
                            "evidence": "Unauthorized access to protected endpoint"
                        })
                    
                except Exception as e:
                    logger.debug(f"Authorization test failed for {endpoint}: {e}")
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": len(self.test_configs["authorization"]["test_endpoints"]),
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ Authorization test failed: {e}")
            return {"error": str(e)}
    
    def _test_information_disclosure(self) -> Dict[str, Any]:
        """Test for information disclosure"""
        try:
            logger.info("🔍 Testing information disclosure...")
            
            vulnerabilities = []
            
            for path in self.test_configs["information_disclosure"]["sensitive_paths"]:
                try:
                    response = self.session.get(f"{self.target_url}{path}", timeout=5)
                    
                    if response.status_code == 200:
                        vulnerabilities.append({
                            "type": "Information Disclosure",
                            "path": path,
                            "severity": "MEDIUM",
                            "evidence": "Sensitive file accessible"
                        })
                    
                except Exception as e:
                    logger.debug(f"Information disclosure test failed for {path}: {e}")
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": len(self.test_configs["information_disclosure"]["sensitive_paths"]),
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ Information disclosure test failed: {e}")
            return {"error": str(e)}
    
    def _test_directory_traversal(self) -> Dict[str, Any]:
        """Test for directory traversal vulnerabilities"""
        try:
            logger.info("🔍 Testing directory traversal vulnerabilities...")
            
            vulnerabilities = []
            test_endpoints = [
                f"{self.target_url}/api/v1/files",
                f"{self.target_url}/api/v1/download"
            ]
            
            for endpoint in test_endpoints:
                for payload in self.test_configs["directory_traversal"]["payloads"]:
                    try:
                        response = self.session.get(f"{endpoint}?file={payload}", timeout=5)
                        
                        # Check for sensitive file content
                        sensitive_indicators = [
                            "root:", "bin:", "etc:", "passwd", "shadow",
                            "windows", "system32", "hosts"
                        ]
                        
                        response_text = response.text.lower()
                        for indicator in sensitive_indicators:
                            if indicator in response_text:
                                vulnerabilities.append({
                                    "type": "Directory Traversal",
                                    "endpoint": endpoint,
                                    "payload": payload,
                                    "severity": "HIGH",
                                    "evidence": f"Sensitive content found: {indicator}"
                                })
                                break
                        
                    except Exception as e:
                        logger.debug(f"Directory traversal test failed for {endpoint}: {e}")
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": len(test_endpoints) * len(self.test_configs["directory_traversal"]["payloads"]),
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ Directory traversal test failed: {e}")
            return {"error": str(e)}
    
    def _test_command_injection(self) -> Dict[str, Any]:
        """Test for command injection vulnerabilities"""
        try:
            logger.info("🔍 Testing command injection vulnerabilities...")
            
            vulnerabilities = []
            test_endpoints = [
                f"{self.target_url}/api/v1/system",
                f"{self.target_url}/api/v1/admin"
            ]
            
            for endpoint in test_endpoints:
                for payload in self.test_configs["command_injection"]["payloads"]:
                    try:
                        response = self.session.post(endpoint, data={"command": payload}, timeout=5)
                        
                        # Check for command execution indicators
                        execution_indicators = [
                            "uid=", "gid=", "root", "bin", "etc",
                            "total", "drwx", "-rwx", "windows"
                        ]
                        
                        response_text = response.text.lower()
                        for indicator in execution_indicators:
                            if indicator in response_text:
                                vulnerabilities.append({
                                    "type": "Command Injection",
                                    "endpoint": endpoint,
                                    "payload": payload,
                                    "severity": "CRITICAL",
                                    "evidence": f"Command execution indicator found: {indicator}"
                                })
                                break
                        
                    except Exception as e:
                        logger.debug(f"Command injection test failed for {endpoint}: {e}")
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": len(test_endpoints) * len(self.test_configs["command_injection"]["payloads"]),
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ Command injection test failed: {e}")
            return {"error": str(e)}
    
    def _test_api_security(self) -> Dict[str, Any]:
        """Test API security vulnerabilities"""
        try:
            logger.info("🔍 Testing API security...")
            
            vulnerabilities = []
            
            # Test for missing rate limiting
            for i in range(100):
                response = self.session.get(f"{self.target_url}/api/v1/projects", timeout=5)
                if response.status_code == 429:
                    break
            else:
                vulnerabilities.append({
                    "type": "Missing Rate Limiting",
                    "endpoint": "/api/v1/projects",
                    "severity": "MEDIUM",
                    "evidence": "No rate limiting detected"
                })
            
            # Test for missing input validation
            response = self.session.post(f"{self.target_url}/api/v1/projects", 
                                       json={"name": "a" * 1000}, timeout=5)
            if response.status_code == 200:
                vulnerabilities.append({
                    "type": "Missing Input Validation",
                    "endpoint": "/api/v1/projects",
                    "severity": "MEDIUM",
                    "evidence": "Large input accepted without validation"
                })
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": 2,
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ API security test failed: {e}")
            return {"error": str(e)}
    
    def _test_headers_security(self) -> Dict[str, Any]:
        """Test security headers"""
        try:
            logger.info("🔍 Testing security headers...")
            
            vulnerabilities = []
            response = self.session.get(self.target_url, timeout=5)
            headers = response.headers
            
            # Check for missing security headers
            security_headers = {
                "X-Frame-Options": "Missing clickjacking protection",
                "X-Content-Type-Options": "Missing MIME type protection",
                "X-XSS-Protection": "Missing XSS protection header",
                "Strict-Transport-Security": "Missing HSTS header",
                "Content-Security-Policy": "Missing CSP header"
            }
            
            for header, description in security_headers.items():
                if header not in headers:
                    vulnerabilities.append({
                        "type": "Missing Security Header",
                        "header": header,
                        "severity": "MEDIUM",
                        "evidence": description
                    })
            
            # Check for information disclosure headers
            info_headers = ["Server", "X-Powered-By", "X-AspNet-Version"]
            for header in info_headers:
                if header in headers:
                    vulnerabilities.append({
                        "type": "Information Disclosure",
                        "header": header,
                        "severity": "LOW",
                        "evidence": f"Server information disclosed: {headers[header]}"
                    })
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": len(security_headers) + len(info_headers),
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ Headers security test failed: {e}")
            return {"error": str(e)}
    
    def _generate_security_recommendations(self, test_results: Dict[str, Any]) -> List[str]:
        """Generate security recommendations based on test results"""
        recommendations = []
        
        # SQL Injection recommendations
        if any("SQL Injection" in str(result) for result in test_results.values()):
            recommendations.extend([
                "Use parameterized queries or ORM",
                "Implement input validation and sanitization",
                "Apply principle of least privilege to database users",
                "Use WAF (Web Application Firewall)"
            ])
        
        # XSS recommendations
        if any("XSS" in str(result) for result in test_results.values()):
            recommendations.extend([
                "Implement Content Security Policy (CSP)",
                "Validate and sanitize all user inputs",
                "Use output encoding for dynamic content",
                "Implement XSS protection headers"
            ])
        
        # CSRF recommendations
        if any("CSRF" in str(result) for result in test_results.values()):
            recommendations.extend([
                "Implement CSRF tokens on all forms",
                "Use SameSite cookie attribute",
                "Validate request origin headers",
                "Implement double-submit cookie pattern"
            ])
        
        # Authentication recommendations
        if any("Weak Authentication" in str(result) for result in test_results.values()):
            recommendations.extend([
                "Implement strong password policies",
                "Use multi-factor authentication",
                "Implement account lockout mechanisms",
                "Use secure session management"
            ])
        
        # Authorization recommendations
        if any("Authorization Bypass" in str(result) for result in test_results.values()):
            recommendations.extend([
                "Implement proper authorization checks",
                "Use role-based access control (RBAC)",
                "Validate user permissions on all endpoints",
                "Implement API authentication"
            ])
        
        # General recommendations
        recommendations.extend([
            "Keep all dependencies updated",
            "Implement proper error handling",
            "Use HTTPS for all communications",
            "Regular security audits and penetration testing",
            "Implement logging and monitoring",
            "Use security headers",
            "Implement rate limiting"
        ])
        
        return list(set(recommendations))  # Remove duplicates
    
    def _assess_overall_risk(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall security risk"""
        try:
            total_vulnerabilities = 0
            critical_vulnerabilities = 0
            high_vulnerabilities = 0
            medium_vulnerabilities = 0
            low_vulnerabilities = 0
            
            for result in test_results.values():
                if isinstance(result, dict) and "vulnerabilities" in result:
                    for vuln in result["vulnerabilities"]:
                        total_vulnerabilities += 1
                        severity = vuln.get("severity", "LOW")
                        
                        if severity == "CRITICAL":
                            critical_vulnerabilities += 1
                        elif severity == "HIGH":
                            high_vulnerabilities += 1
                        elif severity == "MEDIUM":
                            medium_vulnerabilities += 1
                        else:
                            low_vulnerabilities += 1
            
            # Calculate risk level
            if critical_vulnerabilities > 0:
                risk_level = "CRITICAL"
            elif high_vulnerabilities > 2:
                risk_level = "HIGH"
            elif high_vulnerabilities > 0 or medium_vulnerabilities > 5:
                risk_level = "MEDIUM"
            elif total_vulnerabilities > 10:
                risk_level = "LOW"
            else:
                risk_level = "MINIMAL"
            
            return {
                "risk_level": risk_level,
                "total_vulnerabilities": total_vulnerabilities,
                "critical": critical_vulnerabilities,
                "high": high_vulnerabilities,
                "medium": medium_vulnerabilities,
                "low": low_vulnerabilities,
                "recommendation": self._get_risk_recommendation(risk_level)
            }
            
        except Exception as e:
            logger.error(f"❌ Risk assessment failed: {e}")
            return {"error": str(e)}
    
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            "CRITICAL": "Immediate action required. Fix critical vulnerabilities before deployment.",
            "HIGH": "High priority fixes needed. Address high-severity vulnerabilities promptly.",
            "MEDIUM": "Moderate risk. Implement security improvements within 30 days.",
            "LOW": "Low risk. Monitor and improve security over time.",
            "MINIMAL": "Good security posture. Continue monitoring and regular testing."
        }
        return recommendations.get(risk_level, "Unknown risk level")

# Global penetration tester instance
penetration_tester = PenetrationTester()

def get_penetration_tester() -> PenetrationTester:
    """Get penetration tester instance"""
    return penetration_tester 