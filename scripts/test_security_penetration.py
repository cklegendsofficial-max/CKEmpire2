#!/usr/bin/env python3
"""
Comprehensive penetration testing script
Simulates various attack scenarios and tests security implementations
OWASP compliant security testing
"""

import requests
import json
import time
import structlog
from typing import Dict, Any, List
from datetime import datetime
import argparse
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from security_scanner import get_security_scanner
from penetration_test import get_penetration_tester
from vault_service import get_vault_service
from rate_limiter import get_enhanced_rate_limiter

logger = structlog.get_logger()

class SecurityPenetrationTester:
    """Comprehensive security penetration tester"""
    
    def __init__(self, target_url: str = "http://localhost:8000"):
        """Initialize penetration tester"""
        self.target_url = target_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CKEmpire-SecurityTester/1.0'
        })
        
        # Initialize security components
        self.security_scanner = get_security_scanner(target_url)
        self.penetration_tester = get_penetration_tester(target_url)
        self.vault_service = get_vault_service()
        self.rate_limiter = get_enhanced_rate_limiter()
        
        # Test results
        self.test_results = {}
        self.vulnerabilities_found = []
        
    def run_comprehensive_security_test(self) -> Dict[str, Any]:
        """Run comprehensive security testing"""
        try:
            logger.info("🔍 Starting comprehensive security penetration testing...")
            
            start_time = datetime.utcnow()
            
            # Run all security tests
            test_results = {
                "authentication_tests": self._test_authentication_security(),
                "authorization_tests": self._test_authorization_security(),
                "input_validation_tests": self._test_input_validation(),
                "session_management_tests": self._test_session_management(),
                "encryption_tests": self._test_encryption_security(),
                "rate_limiting_tests": self._test_rate_limiting(),
                "vault_security_tests": self._test_vault_security(),
                "api_security_tests": self._test_api_security(),
                "headers_security_tests": self._test_headers_security(),
                "owasp_top_10_tests": self._test_owasp_top_10(),
                "zap_scan": self._run_zap_scan(),
                "penetration_test": self._run_penetration_test()
            }
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Calculate overall security score
            total_vulnerabilities = sum(len(result.get("vulnerabilities", [])) for result in test_results.values())
            security_score = max(0, 100 - (total_vulnerabilities * 5))
            
            # Generate comprehensive report
            report = {
                "test_timestamp": start_time.isoformat(),
                "duration_seconds": duration,
                "target_url": self.target_url,
                "overall_security_score": security_score,
                "total_vulnerabilities": total_vulnerabilities,
                "test_results": test_results,
                "recommendations": self._generate_security_recommendations(test_results),
                "risk_assessment": self._assess_overall_risk(test_results),
                "compliance_status": self._check_compliance_status(test_results)
            }
            
            # Save report
            report_file = f"security_penetration_test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"✅ Comprehensive security test completed - Score: {security_score}, Vulnerabilities: {total_vulnerabilities}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Comprehensive security test failed: {e}")
            return {"error": str(e)}
    
    def _test_authentication_security(self) -> Dict[str, Any]:
        """Test authentication security"""
        try:
            logger.info("🔍 Testing authentication security...")
            
            vulnerabilities = []
            
            # Test weak password policies
            weak_passwords = ["password", "123456", "admin", "test", "qwerty"]
            for password in weak_passwords:
                try:
                    response = self.session.post(f"{self.target_url}/api/v1/auth/login", 
                                               json={"username": "test", "password": password}, timeout=5)
                    if response.status_code == 200:
                        vulnerabilities.append({
                            "type": "Weak Password Policy",
                            "password": password,
                            "severity": "HIGH",
                            "evidence": "Weak password accepted"
                        })
                except:
                    pass
            
            # Test brute force protection
            for i in range(20):
                try:
                    response = self.session.post(f"{self.target_url}/api/v1/auth/login", 
                                               json={"username": "test", "password": "wrong"}, timeout=5)
                    if response.status_code == 423:  # Locked
                        break
                except:
                    pass
            else:
                vulnerabilities.append({
                    "type": "Missing Brute Force Protection",
                    "severity": "HIGH",
                    "evidence": "No account lockout after multiple failed attempts"
                })
            
            # Test password complexity requirements
            try:
                response = self.session.post(f"{self.target_url}/api/v1/auth/register", 
                                           json={
                                               "username": "testuser",
                                               "email": "test@example.com",
                                               "password": "weak"
                                           }, timeout=5)
                if response.status_code == 200:
                    vulnerabilities.append({
                        "type": "Weak Password Complexity",
                        "severity": "MEDIUM",
                        "evidence": "Weak password accepted during registration"
                    })
            except:
                pass
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": 3,
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ Authentication security test failed: {e}")
            return {"error": str(e)}
    
    def _test_authorization_security(self) -> Dict[str, Any]:
        """Test authorization security"""
        try:
            logger.info("🔍 Testing authorization security...")
            
            vulnerabilities = []
            
            # Test unauthorized access to protected endpoints
            protected_endpoints = [
                "/api/v1/admin",
                "/api/v1/users",
                "/api/v1/config",
                "/api/v1/system"
            ]
            
            for endpoint in protected_endpoints:
                try:
                    response = self.session.get(f"{self.target_url}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        vulnerabilities.append({
                            "type": "Authorization Bypass",
                            "endpoint": endpoint,
                            "severity": "HIGH",
                            "evidence": "Unauthorized access to protected endpoint"
                        })
                except:
                    pass
            
            # Test privilege escalation
            try:
                response = self.session.post(f"{self.target_url}/api/v1/auth/register", 
                                           json={
                                               "username": "admin",
                                               "email": "admin@example.com",
                                               "password": "Admin123!",
                                               "role": "admin"
                                           }, timeout=5)
                if response.status_code == 200:
                    vulnerabilities.append({
                        "type": "Privilege Escalation",
                        "severity": "CRITICAL",
                        "evidence": "Able to register as admin user"
                    })
            except:
                pass
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": 2,
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ Authorization security test failed: {e}")
            return {"error": str(e)}
    
    def _test_input_validation(self) -> Dict[str, Any]:
        """Test input validation security"""
        try:
            logger.info("🔍 Testing input validation security...")
            
            vulnerabilities = []
            
            # Test SQL injection
            sql_payloads = [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "' UNION SELECT * FROM users --",
                "admin'--"
            ]
            
            for payload in sql_payloads:
                try:
                    response = self.session.get(f"{self.target_url}/api/v1/projects?search={payload}", timeout=5)
                    if "sql" in response.text.lower() or "mysql" in response.text.lower():
                        vulnerabilities.append({
                            "type": "SQL Injection",
                            "payload": payload,
                            "severity": "CRITICAL",
                            "evidence": "SQL error in response"
                        })
                except:
                    pass
            
            # Test XSS
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')"
            ]
            
            for payload in xss_payloads:
                try:
                    response = self.session.post(f"{self.target_url}/api/v1/projects", 
                                               json={"name": payload}, timeout=5)
                    if payload in response.text:
                        vulnerabilities.append({
                            "type": "Cross-Site Scripting (XSS)",
                            "payload": payload,
                            "severity": "HIGH",
                            "evidence": "XSS payload reflected in response"
                        })
                except:
                    pass
            
            # Test command injection
            cmd_payloads = [
                "; ls -la",
                "| whoami",
                "&& cat /etc/passwd"
            ]
            
            for payload in cmd_payloads:
                try:
                    response = self.session.post(f"{self.target_url}/api/v1/system", 
                                               json={"command": payload}, timeout=5)
                    if "uid=" in response.text or "root:" in response.text:
                        vulnerabilities.append({
                            "type": "Command Injection",
                            "payload": payload,
                            "severity": "CRITICAL",
                            "evidence": "Command execution detected"
                        })
                except:
                    pass
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": 3,
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ Input validation test failed: {e}")
            return {"error": str(e)}
    
    def _test_session_management(self) -> Dict[str, Any]:
        """Test session management security"""
        try:
            logger.info("🔍 Testing session management security...")
            
            vulnerabilities = []
            
            # Test session fixation
            try:
                # Get initial session
                response1 = self.session.get(f"{self.target_url}/api/v1/auth/login", timeout=5)
                session_id_1 = self.session.cookies.get("session_id")
                
                # Login and check if session changed
                response2 = self.session.post(f"{self.target_url}/api/v1/auth/login", 
                                            json={"username": "test", "password": "test"}, timeout=5)
                session_id_2 = self.session.cookies.get("session_id")
                
                if session_id_1 == session_id_2:
                    vulnerabilities.append({
                        "type": "Session Fixation",
                        "severity": "MEDIUM",
                        "evidence": "Session ID not changed after login"
                    })
            except:
                pass
            
            # Test session timeout
            try:
                response = self.session.get(f"{self.target_url}/api/v1/projects", timeout=5)
                if response.status_code == 200:
                    # Wait and check if session expires
                    time.sleep(2)
                    response2 = self.session.get(f"{self.target_url}/api/v1/projects", timeout=5)
                    if response2.status_code == 200:
                        vulnerabilities.append({
                            "type": "Missing Session Timeout",
                            "severity": "MEDIUM",
                            "evidence": "Session does not expire"
                        })
            except:
                pass
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": 2,
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ Session management test failed: {e}")
            return {"error": str(e)}
    
    def _test_encryption_security(self) -> Dict[str, Any]:
        """Test encryption security"""
        try:
            logger.info("🔍 Testing encryption security...")
            
            vulnerabilities = []
            
            # Test HTTPS enforcement
            if not self.target_url.startswith("https://"):
                vulnerabilities.append({
                    "type": "Missing HTTPS",
                    "severity": "HIGH",
                    "evidence": "Application not using HTTPS"
                })
            
            # Test security headers
            try:
                response = self.session.get(self.target_url, timeout=5)
                headers = response.headers
                
                security_headers = {
                    "Strict-Transport-Security": "Missing HSTS header",
                    "X-Frame-Options": "Missing clickjacking protection",
                    "X-Content-Type-Options": "Missing MIME type protection",
                    "X-XSS-Protection": "Missing XSS protection header",
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
            except:
                pass
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": 2,
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ Encryption security test failed: {e}")
            return {"error": str(e)}
    
    def _test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting security"""
        try:
            logger.info("🔍 Testing rate limiting security...")
            
            vulnerabilities = []
            
            # Test rate limiting effectiveness
            for i in range(150):  # Try to exceed rate limit
                try:
                    response = self.session.get(f"{self.target_url}/api/v1/projects", timeout=5)
                    if response.status_code == 429:  # Too Many Requests
                        break
                except:
                    pass
            else:
                vulnerabilities.append({
                    "type": "Missing Rate Limiting",
                    "severity": "MEDIUM",
                    "evidence": "No rate limiting detected"
                })
            
            # Test adaptive rate limiting
            try:
                # Simulate suspicious activity
                for i in range(100):
                    response = self.session.get(f"{self.target_url}/api/v1/projects?test=sqlmap", timeout=5)
                    if response.status_code == 429:
                        break
                else:
                    vulnerabilities.append({
                        "type": "Missing Adaptive Rate Limiting",
                        "severity": "LOW",
                        "evidence": "No adaptive rate limiting for suspicious activity"
                    })
            except:
                pass
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": 2,
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ Rate limiting test failed: {e}")
            return {"error": str(e)}
    
    def _test_vault_security(self) -> Dict[str, Any]:
        """Test vault security"""
        try:
            logger.info("🔍 Testing vault security...")
            
            vulnerabilities = []
            
            # Test vault health
            vault_health = self.vault_service.health_check()
            if vault_health.get("status") != "healthy":
                vulnerabilities.append({
                    "type": "Vault Health Issue",
                    "severity": "MEDIUM",
                    "evidence": f"Vault health check failed: {vault_health}"
                })
            
            # Test secret storage
            test_secret = {"test_key": "test_value"}
            success = self.vault_service.store_secret("test/security", test_secret)
            if not success:
                vulnerabilities.append({
                    "type": "Vault Storage Issue",
                    "severity": "HIGH",
                    "evidence": "Failed to store secret in vault"
                })
            
            # Test secret retrieval
            retrieved_secret = self.vault_service.get_secret("test/security")
            if not retrieved_secret:
                vulnerabilities.append({
                    "type": "Vault Retrieval Issue",
                    "severity": "HIGH",
                    "evidence": "Failed to retrieve secret from vault"
                })
            
            # Test secret rotation
            rotation_success = self.vault_service.rotate_secret("test/security")
            if not rotation_success:
                vulnerabilities.append({
                    "type": "Vault Rotation Issue",
                    "severity": "MEDIUM",
                    "evidence": "Failed to rotate secret"
                })
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": 4,
                "vulnerabilities_found": len(vulnerabilities)
            }
            
        except Exception as e:
            logger.error(f"❌ Vault security test failed: {e}")
            return {"error": str(e)}
    
    def _test_api_security(self) -> Dict[str, Any]:
        """Test API security"""
        try:
            logger.info("🔍 Testing API security...")
            
            vulnerabilities = []
            
            # Test API authentication
            try:
                response = self.session.get(f"{self.target_url}/api/v1/projects", timeout=5)
                if response.status_code == 200:
                    vulnerabilities.append({
                        "type": "Missing API Authentication",
                        "severity": "HIGH",
                        "evidence": "API endpoint accessible without authentication"
                    })
            except:
                pass
            
            # Test API input validation
            try:
                response = self.session.post(f"{self.target_url}/api/v1/projects", 
                                           json={"name": "a" * 1000}, timeout=5)
                if response.status_code == 200:
                    vulnerabilities.append({
                        "type": "Missing Input Validation",
                        "severity": "MEDIUM",
                        "evidence": "Large input accepted without validation"
                    })
            except:
                pass
            
            # Test API error handling
            try:
                response = self.session.get(f"{self.target_url}/api/v1/nonexistent", timeout=5)
                if "error" not in response.text.lower():
                    vulnerabilities.append({
                        "type": "Poor Error Handling",
                        "severity": "LOW",
                        "evidence": "Error response does not follow standard format"
                    })
            except:
                pass
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_tests": 3,
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
    
    def _test_owasp_top_10(self) -> Dict[str, Any]:
        """Test OWASP Top 10 vulnerabilities"""
        try:
            logger.info("🔍 Testing OWASP Top 10 vulnerabilities...")
            
            # Run OWASP checklist
            owasp_report = self.security_scanner.run_owasp_checklist()
            
            return {
                "owasp_report": owasp_report,
                "compliance_score": owasp_report.get("compliance_score", 0),
                "passed_checks": owasp_report.get("passed_checks", 0),
                "total_checks": owasp_report.get("total_checks", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ OWASP Top 10 test failed: {e}")
            return {"error": str(e)}
    
    def _run_zap_scan(self) -> Dict[str, Any]:
        """Run ZAP security scan"""
        try:
            logger.info("🔍 Running ZAP security scan...")
            
            # Run baseline scan
            zap_report = self.security_scanner.run_zap_scan("baseline")
            
            return {
                "zap_report": zap_report,
                "security_score": zap_report.get("security_score", 0),
                "total_alerts": zap_report.get("summary", {}).get("total_alerts", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ ZAP scan failed: {e}")
            return {"error": str(e)}
    
    def _run_penetration_test(self) -> Dict[str, Any]:
        """Run comprehensive penetration test"""
        try:
            logger.info("🔍 Running comprehensive penetration test...")
            
            # Run full penetration test
            pentest_report = self.penetration_tester.run_full_penetration_test()
            
            return {
                "pentest_report": pentest_report,
                "overall_security_score": pentest_report.get("overall_security_score", 0),
                "total_vulnerabilities": pentest_report.get("total_vulnerabilities", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Penetration test failed: {e}")
            return {"error": str(e)}
    
    def _generate_security_recommendations(self, test_results: Dict[str, Any]) -> List[str]:
        """Generate security recommendations based on test results"""
        recommendations = []
        
        # Authentication recommendations
        if any("Weak Password" in str(result) for result in test_results.values()):
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
        
        # Input validation recommendations
        if any("SQL Injection" in str(result) for result in test_results.values()):
            recommendations.extend([
                "Use parameterized queries or ORM",
                "Implement input validation and sanitization",
                "Apply principle of least privilege to database users",
                "Use WAF (Web Application Firewall)"
            ])
        
        if any("XSS" in str(result) for result in test_results.values()):
            recommendations.extend([
                "Implement Content Security Policy (CSP)",
                "Validate and sanitize all user inputs",
                "Use output encoding for dynamic content",
                "Implement XSS protection headers"
            ])
        
        # General recommendations
        recommendations.extend([
            "Keep all dependencies updated",
            "Implement proper error handling",
            "Use HTTPS for all communications",
            "Regular security audits and penetration testing",
            "Implement logging and monitoring",
            "Use security headers",
            "Implement rate limiting",
            "Use secure secrets management",
            "Implement data encryption at rest and in transit"
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
    
    def _check_compliance_status(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance status"""
        try:
            compliance_status = {
                "owasp_compliance": test_results.get("owasp_top_10_tests", {}).get("compliance_score", 0),
                "security_score": test_results.get("zap_scan", {}).get("security_score", 0),
                "penetration_score": test_results.get("penetration_test", {}).get("overall_security_score", 0),
                "overall_compliance": 0
            }
            
            # Calculate overall compliance
            scores = [compliance_status["owasp_compliance"], 
                     compliance_status["security_score"], 
                     compliance_status["penetration_score"]]
            compliance_status["overall_compliance"] = sum(scores) / len(scores)
            
            return compliance_status
            
        except Exception as e:
            logger.error(f"❌ Compliance check failed: {e}")
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

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Comprehensive Security Penetration Tester")
    parser.add_argument("--target", default="http://localhost:8000", help="Target URL")
    parser.add_argument("--output", default="security_report.json", help="Output file")
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = SecurityPenetrationTester(args.target)
    
    # Run comprehensive test
    report = tester.run_comprehensive_security_test()
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\n🔒 Security Test Summary:")
    print(f"Target: {args.target}")
    print(f"Security Score: {report.get('overall_security_score', 0)}/100")
    print(f"Vulnerabilities Found: {report.get('total_vulnerabilities', 0)}")
    print(f"Risk Level: {report.get('risk_assessment', {}).get('risk_level', 'UNKNOWN')}")
    print(f"Report saved to: {args.output}")
    
    # Exit with appropriate code
    if report.get('overall_security_score', 0) < 70:
        print("⚠️  Security score below threshold - Action required!")
        sys.exit(1)
    else:
        print("✅ Security tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main() 