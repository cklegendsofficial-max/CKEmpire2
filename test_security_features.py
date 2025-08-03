"""
Comprehensive security features test script
Tests all OWASP compliant security implementations
"""

import requests
import json
import time
import structlog
from datetime import datetime
from typing import Dict, Any, List

logger = structlog.get_logger()

class SecurityTestSuite:
    """Comprehensive security features test suite"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize test suite"""
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {}
        
        # Test configurations
        self.auth_tests = [
            {"username": "testuser", "password": "testpass123", "email": "test@example.com"},
            {"username": "admin", "password": "admin123", "email": "admin@example.com"}
        ]
        
        self.security_endpoints = [
            "/api/v1/security/health",
            "/api/v1/security/scan",
            "/api/v1/security/owasp-checklist",
            "/api/v1/security/penetration-test",
            "/api/v1/security/rate-limit/stats",
            "/api/v1/security/vault/store",
            "/api/v1/security/vault/list"
        ]
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all security tests"""
        logger.info("🔒 Starting comprehensive security features test...")
        
        start_time = datetime.utcnow()
        
        # Run all test categories
        test_results = {
            "authentication": self.test_authentication(),
            "vault_integration": self.test_vault_integration(),
            "rate_limiting": self.test_rate_limiting(),
            "security_scanning": self.test_security_scanning(),
            "penetration_testing": self.test_penetration_testing(),
            "owasp_compliance": self.test_owasp_compliance(),
            "api_security": self.test_api_security()
        }
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Calculate overall security score
        total_tests = sum(len(result.get("tests", [])) for result in test_results.values())
        passed_tests = sum(len([t for t in result.get("tests", []) if t.get("status") == "PASS"]) 
                          for result in test_results.values())
        security_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate comprehensive report
        report = {
            "test_timestamp": start_time.isoformat(),
            "duration_seconds": duration,
            "overall_security_score": security_score,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "test_results": test_results,
            "recommendations": self._generate_recommendations(test_results)
        }
        
        # Save report
        with open(f"security_test_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Security test completed - Score: {security_score:.1f}%, Passed: {passed_tests}/{total_tests}")
        return report
    
    def test_authentication(self) -> Dict[str, Any]:
        """Test JWT + OAuth2 authentication"""
        logger.info("🔐 Testing authentication features...")
        
        tests = []
        
        # Test user registration
        for user in self.auth_tests:
            try:
                response = self.session.post(f"{self.base_url}/api/v1/auth/register", json=user)
                if response.status_code == 200:
                    tests.append({
                        "test": f"User registration: {user['username']}",
                        "status": "PASS",
                        "details": "User registered successfully"
                    })
                else:
                    tests.append({
                        "test": f"User registration: {user['username']}",
                        "status": "FAIL",
                        "details": f"Registration failed: {response.status_code}"
                    })
            except Exception as e:
                tests.append({
                    "test": f"User registration: {user['username']}",
                    "status": "ERROR",
                    "details": str(e)
                })
        
        # Test user login
        for user in self.auth_tests:
            try:
                login_data = {"username": user["username"], "password": user["password"]}
                response = self.session.post(f"{self.base_url}/api/v1/auth/login", json=login_data)
                
                if response.status_code == 200:
                    token_data = response.json()
                    if "access_token" in token_data:
                        tests.append({
                            "test": f"User login: {user['username']}",
                            "status": "PASS",
                            "details": "Login successful, JWT token received"
                        })
                        
                        # Test protected endpoint
                        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                        me_response = self.session.get(f"{self.base_url}/api/v1/auth/me", headers=headers)
                        
                        if me_response.status_code == 200:
                            tests.append({
                                "test": f"Protected endpoint access: {user['username']}",
                                "status": "PASS",
                                "details": "Successfully accessed protected endpoint"
                            })
                        else:
                            tests.append({
                                "test": f"Protected endpoint access: {user['username']}",
                                "status": "FAIL",
                                "details": f"Failed to access protected endpoint: {me_response.status_code}"
                            })
                    else:
                        tests.append({
                            "test": f"User login: {user['username']}",
                            "status": "FAIL",
                            "details": "Login successful but no JWT token received"
                        })
                else:
                    tests.append({
                        "test": f"User login: {user['username']}",
                        "status": "FAIL",
                        "details": f"Login failed: {response.status_code}"
                    })
            except Exception as e:
                tests.append({
                    "test": f"User login: {user['username']}",
                    "status": "ERROR",
                    "details": str(e)
                })
        
        # Test OAuth2 providers endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/v1/auth/providers")
            if response.status_code == 200:
                tests.append({
                    "test": "OAuth2 providers endpoint",
                    "status": "PASS",
                    "details": "OAuth2 providers endpoint accessible"
                })
            else:
                tests.append({
                    "test": "OAuth2 providers endpoint",
                    "status": "FAIL",
                    "details": f"OAuth2 providers endpoint failed: {response.status_code}"
                })
        except Exception as e:
            tests.append({
                "test": "OAuth2 providers endpoint",
                "status": "ERROR",
                "details": str(e)
            })
        
        return {
            "tests": tests,
            "total_tests": len(tests),
            "passed_tests": len([t for t in tests if t["status"] == "PASS"]),
            "failed_tests": len([t for t in tests if t["status"] == "FAIL"]),
            "error_tests": len([t for t in tests if t["status"] == "ERROR"])
        }
    
    def test_vault_integration(self) -> Dict[str, Any]:
        """Test Vault secrets management"""
        logger.info("🔐 Testing Vault integration...")
        
        tests = []
        
        # Test Vault health
        try:
            response = self.session.get(f"{self.base_url}/api/v1/security/health")
            if response.status_code == 200:
                health_data = response.json()
                if "vault" in health_data.get("services", {}):
                    tests.append({
                        "test": "Vault health check",
                        "status": "PASS",
                        "details": "Vault service is healthy"
                    })
                else:
                    tests.append({
                        "test": "Vault health check",
                        "status": "FAIL",
                        "details": "Vault service not found in health check"
                    })
            else:
                tests.append({
                    "test": "Vault health check",
                    "status": "FAIL",
                    "details": f"Health check failed: {response.status_code}"
                })
        except Exception as e:
            tests.append({
                "test": "Vault health check",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test secret storage
        try:
            secret_data = {
                "path": "test/secret",
                "data": {"api_key": "test_key_123", "password": "test_pass_456"},
                "metadata": {"created_by": "test_user", "environment": "test"}
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/security/vault/store", json=secret_data)
            if response.status_code == 200:
                tests.append({
                    "test": "Secret storage",
                    "status": "PASS",
                    "details": "Secret stored successfully"
                })
                
                # Test secret retrieval
                retrieve_response = self.session.get(f"{self.base_url}/api/v1/security/vault/retrieve/test/secret")
                if retrieve_response.status_code == 200:
                    tests.append({
                        "test": "Secret retrieval",
                        "status": "PASS",
                        "details": "Secret retrieved successfully"
                    })
                else:
                    tests.append({
                        "test": "Secret retrieval",
                        "status": "FAIL",
                        "details": f"Secret retrieval failed: {retrieve_response.status_code}"
                    })
            else:
                tests.append({
                    "test": "Secret storage",
                    "status": "FAIL",
                    "details": f"Secret storage failed: {response.status_code}"
                })
        except Exception as e:
            tests.append({
                "test": "Secret storage",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test secret listing
        try:
            response = self.session.get(f"{self.base_url}/api/v1/security/vault/list")
            if response.status_code == 200:
                tests.append({
                    "test": "Secret listing",
                    "status": "PASS",
                    "details": "Secret listing successful"
                })
            else:
                tests.append({
                    "test": "Secret listing",
                    "status": "FAIL",
                    "details": f"Secret listing failed: {response.status_code}"
                })
        except Exception as e:
            tests.append({
                "test": "Secret listing",
                "status": "ERROR",
                "details": str(e)
            })
        
        return {
            "tests": tests,
            "total_tests": len(tests),
            "passed_tests": len([t for t in tests if t["status"] == "PASS"]),
            "failed_tests": len([t for t in tests if t["status"] == "FAIL"]),
            "error_tests": len([t for t in tests if t["status"] == "ERROR"])
        }
    
    def test_rate_limiting(self) -> Dict[str, Any]:
        """Test enhanced rate limiting"""
        logger.info("🚦 Testing rate limiting features...")
        
        tests = []
        
        # Test rate limit stats
        try:
            response = self.session.get(f"{self.base_url}/api/v1/security/rate-limit/stats")
            if response.status_code == 200:
                stats = response.json()
                if "total_events" in stats:
                    tests.append({
                        "test": "Rate limit stats",
                        "status": "PASS",
                        "details": "Rate limit statistics accessible"
                    })
                else:
                    tests.append({
                        "test": "Rate limit stats",
                        "status": "FAIL",
                        "details": "Rate limit statistics incomplete"
                    })
            else:
                tests.append({
                    "test": "Rate limit stats",
                    "status": "FAIL",
                    "details": f"Rate limit stats failed: {response.status_code}"
                })
        except Exception as e:
            tests.append({
                "test": "Rate limit stats",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test IP blacklisting
        try:
            test_ip = "192.168.1.100"
            response = self.session.post(f"{self.base_url}/api/v1/security/rate-limit/blacklist/{test_ip}")
            if response.status_code == 200:
                tests.append({
                    "test": "IP blacklisting",
                    "status": "PASS",
                    "details": "IP added to blacklist successfully"
                })
                
                # Test IP removal
                remove_response = self.session.delete(f"{self.base_url}/api/v1/security/rate-limit/blacklist/{test_ip}")
                if remove_response.status_code == 200:
                    tests.append({
                        "test": "IP blacklist removal",
                        "status": "PASS",
                        "details": "IP removed from blacklist successfully"
                    })
                else:
                    tests.append({
                        "test": "IP blacklist removal",
                        "status": "FAIL",
                        "details": f"IP removal failed: {remove_response.status_code}"
                    })
            else:
                tests.append({
                    "test": "IP blacklisting",
                    "status": "FAIL",
                    "details": f"IP blacklisting failed: {response.status_code}"
                })
        except Exception as e:
            tests.append({
                "test": "IP blacklisting",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test suspicious activity report
        try:
            response = self.session.get(f"{self.base_url}/api/v1/security/rate-limit/suspicious-activity")
            if response.status_code == 200:
                tests.append({
                    "test": "Suspicious activity report",
                    "status": "PASS",
                    "details": "Suspicious activity report accessible"
                })
            else:
                tests.append({
                    "test": "Suspicious activity report",
                    "status": "FAIL",
                    "details": f"Suspicious activity report failed: {response.status_code}"
                })
        except Exception as e:
            tests.append({
                "test": "Suspicious activity report",
                "status": "ERROR",
                "details": str(e)
            })
        
        return {
            "tests": tests,
            "total_tests": len(tests),
            "passed_tests": len([t for t in tests if t["status"] == "PASS"]),
            "failed_tests": len([t for t in tests if t["status"] == "FAIL"]),
            "error_tests": len([t for t in tests if t["status"] == "ERROR"])
        }
    
    def test_security_scanning(self) -> Dict[str, Any]:
        """Test security scanning features"""
        logger.info("🔍 Testing security scanning...")
        
        tests = []
        
        # Test security scan
        try:
            scan_request = {"scan_type": "baseline", "target_url": self.base_url}
            response = self.session.post(f"{self.base_url}/api/v1/security/scan", json=scan_request)
            if response.status_code == 200:
                scan_result = response.json()
                if "security_score" in scan_result:
                    tests.append({
                        "test": "Security scan",
                        "status": "PASS",
                        "details": f"Security scan completed with score: {scan_result['security_score']}"
                    })
                else:
                    tests.append({
                        "test": "Security scan",
                        "status": "FAIL",
                        "details": "Security scan completed but no score returned"
                    })
            else:
                tests.append({
                    "test": "Security scan",
                    "status": "FAIL",
                    "details": f"Security scan failed: {response.status_code}"
                })
        except Exception as e:
            tests.append({
                "test": "Security scan",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test OWASP checklist
        try:
            response = self.session.post(f"{self.base_url}/api/v1/security/owasp-checklist")
            if response.status_code == 200:
                checklist_result = response.json()
                if "compliance_score" in checklist_result:
                    tests.append({
                        "test": "OWASP checklist",
                        "status": "PASS",
                        "details": f"OWASP checklist completed with compliance: {checklist_result['compliance_score']}%"
                    })
                else:
                    tests.append({
                        "test": "OWASP checklist",
                        "status": "FAIL",
                        "details": "OWASP checklist completed but no compliance score returned"
                    })
            else:
                tests.append({
                    "test": "OWASP checklist",
                    "status": "FAIL",
                    "details": f"OWASP checklist failed: {response.status_code}"
                })
        except Exception as e:
            tests.append({
                "test": "OWASP checklist",
                "status": "ERROR",
                "details": str(e)
            })
        
        return {
            "tests": tests,
            "total_tests": len(tests),
            "passed_tests": len([t for t in tests if t["status"] == "PASS"]),
            "failed_tests": len([t for t in tests if t["status"] == "FAIL"]),
            "error_tests": len([t for t in tests if t["status"] == "ERROR"])
        }
    
    def test_penetration_testing(self) -> Dict[str, Any]:
        """Test penetration testing features"""
        logger.info("🔍 Testing penetration testing...")
        
        tests = []
        
        # Test penetration test
        try:
            response = self.session.post(f"{self.base_url}/api/v1/security/penetration-test")
            if response.status_code == 200:
                test_result = response.json()
                if "overall_security_score" in test_result:
                    tests.append({
                        "test": "Penetration test",
                        "status": "PASS",
                        "details": f"Penetration test completed with score: {test_result['overall_security_score']}"
                    })
                else:
                    tests.append({
                        "test": "Penetration test",
                        "status": "FAIL",
                        "details": "Penetration test completed but no score returned"
                    })
            else:
                tests.append({
                    "test": "Penetration test",
                    "status": "FAIL",
                    "details": f"Penetration test failed: {response.status_code}"
                })
        except Exception as e:
            tests.append({
                "test": "Penetration test",
                "status": "ERROR",
                "details": str(e)
            })
        
        return {
            "tests": tests,
            "total_tests": len(tests),
            "passed_tests": len([t for t in tests if t["status"] == "PASS"]),
            "failed_tests": len([t for t in tests if t["status"] == "FAIL"]),
            "error_tests": len([t for t in tests if t["status"] == "ERROR"])
        }
    
    def test_owasp_compliance(self) -> Dict[str, Any]:
        """Test OWASP compliance features"""
        logger.info("🔒 Testing OWASP compliance...")
        
        tests = []
        
        # Test security headers
        try:
            response = self.session.get(f"{self.base_url}/api/v1/security/test/headers")
            if response.status_code == 200:
                headers_result = response.json()
                if "vulnerabilities" in headers_result:
                    vuln_count = len(headers_result["vulnerabilities"])
                    if vuln_count == 0:
                        tests.append({
                            "test": "Security headers",
                            "status": "PASS",
                            "details": "All security headers properly configured"
                        })
                    else:
                        tests.append({
                            "test": "Security headers",
                            "status": "FAIL",
                            "details": f"Found {vuln_count} security header vulnerabilities"
                        })
                else:
                    tests.append({
                        "test": "Security headers",
                        "status": "FAIL",
                        "details": "Security headers test incomplete"
                    })
            else:
                tests.append({
                    "test": "Security headers",
                    "status": "FAIL",
                    "details": f"Security headers test failed: {response.status_code}"
                })
        except Exception as e:
            tests.append({
                "test": "Security headers",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test API security
        try:
            response = self.session.get(f"{self.base_url}/api/v1/security/test/api-security")
            if response.status_code == 200:
                api_result = response.json()
                if "vulnerabilities" in api_result:
                    vuln_count = len(api_result["vulnerabilities"])
                    if vuln_count == 0:
                        tests.append({
                            "test": "API security",
                            "status": "PASS",
                            "details": "API security properly configured"
                        })
                    else:
                        tests.append({
                            "test": "API security",
                            "status": "FAIL",
                            "details": f"Found {vuln_count} API security vulnerabilities"
                        })
                else:
                    tests.append({
                        "test": "API security",
                        "status": "FAIL",
                        "details": "API security test incomplete"
                    })
            else:
                tests.append({
                    "test": "API security",
                    "status": "FAIL",
                    "details": f"API security test failed: {response.status_code}"
                })
        except Exception as e:
            tests.append({
                "test": "API security",
                "status": "ERROR",
                "details": str(e)
            })
        
        return {
            "tests": tests,
            "total_tests": len(tests),
            "passed_tests": len([t for t in tests if t["status"] == "PASS"]),
            "failed_tests": len([t for t in tests if t["status"] == "FAIL"]),
            "error_tests": len([t for t in tests if t["status"] == "ERROR"])
        }
    
    def test_api_security(self) -> Dict[str, Any]:
        """Test API security features"""
        logger.info("🔒 Testing API security...")
        
        tests = []
        
        # Test rate limiting
        try:
            # Make multiple requests to test rate limiting
            responses = []
            for i in range(105):  # Exceed default limit of 100
                response = self.session.get(f"{self.base_url}/api/v1/projects")
                responses.append(response.status_code)
                if response.status_code == 429:  # Too Many Requests
                    break
            
            if 429 in responses:
                tests.append({
                    "test": "Rate limiting",
                    "status": "PASS",
                    "details": "Rate limiting properly enforced"
                })
            else:
                tests.append({
                    "test": "Rate limiting",
                    "status": "FAIL",
                    "details": "Rate limiting not enforced"
                })
        except Exception as e:
            tests.append({
                "test": "Rate limiting",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test authentication required
        try:
            response = self.session.get(f"{self.base_url}/api/v1/auth/me")
            if response.status_code == 401:  # Unauthorized
                tests.append({
                    "test": "Authentication required",
                    "status": "PASS",
                    "details": "Authentication properly required for protected endpoints"
                })
            else:
                tests.append({
                    "test": "Authentication required",
                    "status": "FAIL",
                    "details": f"Authentication not properly enforced: {response.status_code}"
                })
        except Exception as e:
            tests.append({
                "test": "Authentication required",
                "status": "ERROR",
                "details": str(e)
            })
        
        return {
            "tests": tests,
            "total_tests": len(tests),
            "passed_tests": len([t for t in tests if t["status"] == "PASS"]),
            "failed_tests": len([t for t in tests if t["status"] == "FAIL"]),
            "error_tests": len([t for t in tests if t["status"] == "ERROR"])
        }
    
    def _generate_recommendations(self, test_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Authentication recommendations
        auth_result = test_results.get("authentication", {})
        auth_passed = auth_result.get("passed_tests", 0)
        auth_total = auth_result.get("total_tests", 0)
        
        if auth_passed < auth_total:
            recommendations.extend([
                "Review and fix authentication implementation",
                "Ensure JWT tokens are properly validated",
                "Implement proper OAuth2 flow",
                "Add multi-factor authentication"
            ])
        
        # Vault recommendations
        vault_result = test_results.get("vault_integration", {})
        vault_passed = vault_result.get("passed_tests", 0)
        vault_total = vault_result.get("total_tests", 0)
        
        if vault_passed < vault_total:
            recommendations.extend([
                "Ensure Vault service is properly configured",
                "Review secret management implementation",
                "Implement proper secret rotation",
                "Add audit logging for secret access"
            ])
        
        # Rate limiting recommendations
        rate_result = test_results.get("rate_limiting", {})
        rate_passed = rate_result.get("passed_tests", 0)
        rate_total = rate_result.get("total_tests", 0)
        
        if rate_passed < rate_total:
            recommendations.extend([
                "Review rate limiting configuration",
                "Implement proper IP blacklisting/whitelisting",
                "Add suspicious activity detection",
                "Configure appropriate rate limits for different endpoints"
            ])
        
        # Security scanning recommendations
        scan_result = test_results.get("security_scanning", {})
        scan_passed = scan_result.get("passed_tests", 0)
        scan_total = scan_result.get("total_tests", 0)
        
        if scan_passed < scan_total:
            recommendations.extend([
                "Review security scanning implementation",
                "Configure ZAP properly for automated scanning",
                "Implement regular security scans",
                "Add security scanning to CI/CD pipeline"
            ])
        
        # OWASP compliance recommendations
        owasp_result = test_results.get("owasp_compliance", {})
        owasp_passed = owasp_result.get("passed_tests", 0)
        owasp_total = owasp_result.get("total_tests", 0)
        
        if owasp_passed < owasp_total:
            recommendations.extend([
                "Implement missing security headers",
                "Review API security configuration",
                "Follow OWASP Top 10 guidelines",
                "Conduct regular security audits"
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

def main():
    """Main test execution"""
    try:
        # Initialize test suite
        test_suite = SecurityTestSuite()
        
        # Run all tests
        report = test_suite.run_all_tests()
        
        # Print summary
        print("\n" + "="*60)
        print("🔒 SECURITY FEATURES TEST SUMMARY")
        print("="*60)
        print(f"Overall Security Score: {report['overall_security_score']:.1f}%")
        print(f"Total Tests: {report['total_tests']}")
        print(f"Passed: {report['passed_tests']}")
        print(f"Failed: {report['failed_tests']}")
        print(f"Duration: {report['duration_seconds']:.2f} seconds")
        
        # Print detailed results
        print("\n📊 DETAILED RESULTS:")
        for category, result in report['test_results'].items():
            passed = result.get('passed_tests', 0)
            total = result.get('total_tests', 0)
            percentage = (passed / total * 100) if total > 0 else 0
            print(f"  {category.replace('_', ' ').title()}: {passed}/{total} ({percentage:.1f}%)")
        
        # Print recommendations
        if report['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(report['recommendations'][:5], 1):
                print(f"  {i}. {rec}")
            if len(report['recommendations']) > 5:
                print(f"  ... and {len(report['recommendations']) - 5} more recommendations")
        
        print("\n" + "="*60)
        
        # Return exit code based on results
        if report['overall_security_score'] >= 80:
            print("✅ Security features test PASSED")
            return 0
        elif report['overall_security_score'] >= 60:
            print("⚠️  Security features test PASSED with warnings")
            return 0
        else:
            print("❌ Security features test FAILED")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Security test suite failed: {e}")
        print(f"❌ Security test suite failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 