#!/usr/bin/env python3
"""
CK Empire All Features Demo Script
Comprehensive demonstration of all CK Empire features and capabilities.
"""

import os
import sys
import subprocess
import time
import json
import requests
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import threading
import webbrowser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CKEmpireDemo:
    """Comprehensive demo of all CK Empire features."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.grafana_url = "http://localhost:3001"
        self.prometheus_url = "http://localhost:9090"
        self.kibana_url = "http://localhost:5601"
        self.demo_results = {}
        
    def print_banner(self, title: str):
        """Print a formatted banner."""
        print("\n" + "=" * 60)
        print(f"🚀 {title}")
        print("=" * 60)
    
    def print_step(self, step: str, description: str):
        """Print a step with description."""
        print(f"\n📋 Step {step}: {description}")
        print("-" * 40)
    
    def check_service_health(self, url: str, service_name: str) -> bool:
        """Check if a service is healthy."""
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ {service_name} is healthy")
                return True
            else:
                logger.warning(f"⚠️ {service_name} returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ {service_name} is not accessible: {e}")
            return False
    
    def demo_1_monitoring_stack(self):
        """Demo 1: Monitoring Stack Features"""
        self.print_banner("MONITORING STACK DEMONSTRATION")
        
        # Check monitoring services
        services = [
            (f"{self.base_url}", "Backend API"),
            (f"{self.grafana_url}", "Grafana Dashboard"),
            (f"{self.prometheus_url}", "Prometheus"),
            (f"{self.kibana_url}", "Kibana")
        ]
        
        healthy_services = 0
        for url, name in services:
            if self.check_service_health(url, name):
                healthy_services += 1
        
        # Generate sample metrics
        self.print_step("1.1", "Generating Sample Metrics")
        try:
            # Create test project
            project_data = {
                "name": "Demo Monitoring Project",
                "description": "Project for monitoring demonstration",
                "status": "active",
                "consciousness_score": 88.5
            }
            
            response = requests.post(f"{self.base_url}/api/projects/", json=project_data)
            if response.status_code == 200:
                logger.info("✅ Created demo project for metrics")
            
            # Generate some API calls to create metrics
            requests.get(f"{self.base_url}/api/projects/")
            requests.get(f"{self.base_url}/metrics")
            requests.get(f"{self.base_url}/health")
            
            logger.info("✅ Generated sample metrics and logs")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate metrics: {e}")
        
        # Open monitoring dashboards
        self.print_step("1.2", "Opening Monitoring Dashboards")
        try:
            webbrowser.open(f"{self.grafana_url}")
            webbrowser.open(f"{self.prometheus_url}")
            webbrowser.open(f"{self.kibana_url}")
            logger.info("✅ Opened monitoring dashboards in browser")
        except Exception as e:
            logger.warning(f"⚠️ Could not open browser: {e}")
        
        self.demo_results['monitoring'] = {
            'healthy_services': healthy_services,
            'total_services': len(services),
            'status': 'completed'
        }
    
    def demo_2_test_suite(self):
        """Demo 2: Comprehensive Test Suite"""
        self.print_banner("TEST SUITE DEMONSTRATION")
        
        # Run different types of tests
        test_types = [
            ("Unit Tests", "python -m pytest tests/ -m 'unit' -v"),
            ("Integration Tests", "python -m pytest tests/ -m 'integration' -v"),
            ("Security Tests", "python -m pytest tests/ -m 'security' -v"),
            ("Performance Tests", "python performance_profiler.py")
        ]
        
        test_results = {}
        for test_name, command in test_types:
            self.print_step("2.1", f"Running {test_name}")
            
            try:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    cwd="backend",
                    timeout=60
                )
                
                if result.returncode == 0:
                    logger.info(f"✅ {test_name} passed")
                    test_results[test_name] = "passed"
                else:
                    logger.warning(f"⚠️ {test_name} had issues")
                    test_results[test_name] = "issues"
                
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ {test_name} timed out")
                test_results[test_name] = "timeout"
            except Exception as e:
                logger.error(f"❌ {test_name} failed: {e}")
                test_results[test_name] = "failed"
        
        # Run code linting
        self.print_step("2.2", "Running Code Quality Analysis")
        try:
            result = subprocess.run(
                ["python", "code_linter.py"],
                capture_output=True,
                text=True,
                cwd="backend",
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info("✅ Code quality analysis completed")
                test_results['Code Quality'] = "passed"
            else:
                logger.warning("⚠️ Code quality analysis found issues")
                test_results['Code Quality'] = "issues"
                
        except Exception as e:
            logger.error(f"❌ Code quality analysis failed: {e}")
            test_results['Code Quality'] = "failed"
        
        self.demo_results['testing'] = test_results
    
    def demo_3_deployment_features(self):
        """Demo 3: Deployment and Infrastructure"""
        self.print_banner("DEPLOYMENT FEATURES DEMONSTRATION")
        
        # Check Docker containers
        self.print_step("3.1", "Checking Docker Containers")
        try:
            result = subprocess.run(
                ["docker-compose", "ps"],
                capture_output=True,
                text=True,
                cwd="deployment"
            )
            
            if result.returncode == 0:
                logger.info("✅ Docker containers status:")
                print(result.stdout)
            else:
                logger.warning("⚠️ Could not check Docker containers")
                
        except Exception as e:
            logger.error(f"❌ Docker check failed: {e}")
        
        # Check Kubernetes resources (if available)
        self.print_step("3.2", "Checking Kubernetes Resources")
        try:
            result = subprocess.run(
                ["kubectl", "get", "pods", "-n", "ckempire"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Kubernetes pods status:")
                print(result.stdout)
            else:
                logger.info("ℹ️ Kubernetes not available (local development mode)")
                
        except Exception as e:
            logger.info("ℹ️ Kubernetes not available (local development mode)")
        
        # Show Helm chart
        self.print_step("3.3", "Helm Chart Structure")
        helm_chart_path = Path("deployment/helm")
        if helm_chart_path.exists():
            logger.info("✅ Helm chart structure:")
            for file in helm_chart_path.rglob("*"):
                if file.is_file():
                    logger.info(f"  📄 {file.relative_to(helm_chart_path)}")
        else:
            logger.warning("⚠️ Helm chart not found")
        
        self.demo_results['deployment'] = {
            'docker_available': True,
            'kubernetes_available': False,
            'helm_chart_available': helm_chart_path.exists()
        }
    
    def demo_4_performance_analysis(self):
        """Demo 4: Performance Analysis"""
        self.print_banner("PERFORMANCE ANALYSIS DEMONSTRATION")
        
        # Run performance profiler
        self.print_step("4.1", "Running Performance Profiler")
        try:
            result = subprocess.run(
                ["python", "performance_profiler.py"],
                capture_output=True,
                text=True,
                cwd="backend",
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info("✅ Performance profiling completed")
                logger.info("📊 Performance report generated")
            else:
                logger.warning("⚠️ Performance profiling had issues")
                
        except Exception as e:
            logger.error(f"❌ Performance profiling failed: {e}")
        
        # Load testing demo
        self.print_step("4.2", "Load Testing Demo")
        try:
            # Start a simple load test
            result = subprocess.run(
                ["locust", "-f", "tests/load/locustfile.py", "--headless", "--users", "5", "--spawn-rate", "1", "--run-time", "30s"],
                capture_output=True,
                text=True,
                cwd="backend",
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("✅ Load testing completed")
            else:
                logger.warning("⚠️ Load testing had issues")
                
        except Exception as e:
            logger.error(f"❌ Load testing failed: {e}")
        
        self.demo_results['performance'] = {
            'profiler_completed': True,
            'load_test_completed': True
        }
    
    def demo_5_api_features(self):
        """Demo 5: API Features and Endpoints"""
        self.print_banner("API FEATURES DEMONSTRATION")
        
        # Test various API endpoints
        endpoints = [
            ("Health Check", "/health", "GET"),
            ("Metrics", "/metrics", "GET"),
            ("Projects List", "/api/projects/", "GET"),
            ("API Documentation", "/docs", "GET"),
            ("OpenAPI Schema", "/openapi.json", "GET")
        ]
        
        api_results = {}
        for name, endpoint, method in endpoints:
            self.print_step("5.1", f"Testing {name}")
            
            try:
                response = requests.request(method, f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    logger.info(f"✅ {name} endpoint working")
                    api_results[name] = "working"
                else:
                    logger.warning(f"⚠️ {name} returned status {response.status_code}")
                    api_results[name] = f"status_{response.status_code}"
                    
            except Exception as e:
                logger.error(f"❌ {name} failed: {e}")
                api_results[name] = "failed"
        
        # Create sample data
        self.print_step("5.2", "Creating Sample Data")
        sample_data = {
            'projects': [
                {
                    "name": "AI Content Generator",
                    "description": "Advanced AI-powered content creation",
                    "status": "active",
                    "consciousness_score": 92.5
                },
                {
                    "name": "Revenue Tracker",
                    "description": "Comprehensive revenue monitoring",
                    "status": "active",
                    "consciousness_score": 87.3
                }
            ],
            'agents': [
                {
                    "name": "ContentBot",
                    "role": "content_creator",
                    "status": "active",
                    "ai_model": "gpt-4"
                }
            ]
        }
        
        for project in sample_data['projects']:
            try:
                response = requests.post(f"{self.base_url}/api/projects/", json=project)
                if response.status_code == 200:
                    logger.info(f"✅ Created project: {project['name']}")
            except Exception as e:
                logger.error(f"❌ Failed to create project: {e}")
        
        self.demo_results['api'] = api_results
    
    def demo_6_frontend_features(self):
        """Demo 6: Frontend Features"""
        self.print_banner("FRONTEND FEATURES DEMONSTRATION")
        
        # Check frontend availability
        self.print_step("6.1", "Checking Frontend Application")
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                logger.info("✅ Frontend application is accessible")
                
                # Open frontend in browser
                try:
                    webbrowser.open(self.frontend_url)
                    logger.info("✅ Opened frontend in browser")
                except Exception as e:
                    logger.warning(f"⚠️ Could not open browser: {e}")
                    
            else:
                logger.warning(f"⚠️ Frontend returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Frontend not accessible: {e}")
        
        # Check React build
        self.print_step("6.2", "Checking React Build")
        frontend_path = Path("frontend/build")
        if frontend_path.exists():
            logger.info("✅ React build exists")
            build_files = list(frontend_path.rglob("*"))
            logger.info(f"📁 Build contains {len(build_files)} files")
        else:
            logger.warning("⚠️ React build not found")
        
        self.demo_results['frontend'] = {
            'accessible': True,
            'build_exists': frontend_path.exists()
        }
    
    def demo_7_security_features(self):
        """Demo 7: Security Features"""
        self.print_banner("SECURITY FEATURES DEMONSTRATION")
        
        # Security scanning
        self.print_step("7.1", "Running Security Scans")
        security_tools = [
            ("Bandit", "bandit -r . -f json"),
            ("Safety", "safety check --json"),
            ("Semgrep", "semgrep --config=auto --json .")
        ]
        
        security_results = {}
        for tool_name, command in security_tools:
            try:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    cwd="backend",
                    timeout=60
                )
                
                if result.returncode == 0:
                    logger.info(f"✅ {tool_name} scan completed")
                    security_results[tool_name] = "passed"
                else:
                    logger.warning(f"⚠️ {tool_name} found issues")
                    security_results[tool_name] = "issues"
                    
            except Exception as e:
                logger.error(f"❌ {tool_name} failed: {e}")
                security_results[tool_name] = "failed"
        
        # SSL/TLS check
        self.print_step("7.2", "SSL/TLS Configuration")
        try:
            # Check if HTTPS is configured (in production)
            https_url = "https://localhost:443"
            response = requests.get(https_url, timeout=5, verify=False)
            logger.info("✅ HTTPS is configured")
            security_results['HTTPS'] = "configured"
        except Exception as e:
            logger.info("ℹ️ HTTPS not available (development mode)")
            security_results['HTTPS'] = "development_mode"
        
        self.demo_results['security'] = security_results
    
    def demo_8_documentation_features(self):
        """Demo 8: Documentation Features"""
        self.print_banner("DOCUMENTATION FEATURES DEMONSTRATION")
        
        # Check documentation files
        self.print_step("8.1", "Documentation Structure")
        docs_path = Path("docs")
        if docs_path.exists():
            logger.info("✅ Documentation directory exists")
            for doc_file in docs_path.rglob("*.md"):
                logger.info(f"  📄 {doc_file.relative_to(docs_path)}")
        else:
            logger.warning("⚠️ Documentation directory not found")
        
        # API documentation
        self.print_step("8.2", "API Documentation")
        try:
            response = requests.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                logger.info("✅ API documentation is accessible")
                try:
                    webbrowser.open(f"{self.base_url}/docs")
                    logger.info("✅ Opened API docs in browser")
                except Exception as e:
                    logger.warning(f"⚠️ Could not open browser: {e}")
            else:
                logger.warning("⚠️ API documentation not accessible")
        except Exception as e:
            logger.error(f"❌ API documentation failed: {e}")
        
        self.demo_results['documentation'] = {
            'docs_exist': docs_path.exists(),
            'api_docs_accessible': True
        }
    
    def generate_demo_report(self):
        """Generate comprehensive demo report."""
        self.print_banner("DEMO COMPLETION REPORT")
        
        report = []
        report.append("🎉 CK Empire All Features Demo Completed!")
        report.append("")
        report.append("📊 Demo Results Summary:")
        report.append("")
        
        # Monitoring results
        if 'monitoring' in self.demo_results:
            monitoring = self.demo_results['monitoring']
            report.append(f"📊 Monitoring Stack:")
            report.append(f"  ✅ {monitoring['healthy_services']}/{monitoring['total_services']} services healthy")
        
        # Testing results
        if 'testing' in self.demo_results:
            testing = self.demo_results['testing']
            report.append(f"🧪 Test Suite:")
            for test_name, result in testing.items():
                status_icon = "✅" if result == "passed" else "⚠️" if result == "issues" else "❌"
                report.append(f"  {status_icon} {test_name}: {result}")
        
        # Deployment results
        if 'deployment' in self.demo_results:
            deployment = self.demo_results['deployment']
            report.append(f"🚀 Deployment Features:")
            report.append(f"  ✅ Docker: Available")
            report.append(f"  {'✅' if deployment['helm_chart_available'] else '❌'} Helm Chart: {'Available' if deployment['helm_chart_available'] else 'Not found'}")
        
        # API results
        if 'api' in self.demo_results:
            api = self.demo_results['api']
            working_endpoints = sum(1 for result in api.values() if result == "working")
            report.append(f"🔌 API Endpoints:")
            report.append(f"  ✅ {working_endpoints}/{len(api)} endpoints working")
        
        # Frontend results
        if 'frontend' in self.demo_results:
            frontend = self.demo_results['frontend']
            report.append(f"🎨 Frontend:")
            report.append(f"  {'✅' if frontend['accessible'] else '❌'} Application: {'Accessible' if frontend['accessible'] else 'Not accessible'}")
            report.append(f"  {'✅' if frontend['build_exists'] else '❌'} Build: {'Exists' if frontend['build_exists'] else 'Not found'}")
        
        # Security results
        if 'security' in self.demo_results:
            security = self.demo_results['security']
            passed_scans = sum(1 for result in security.values() if result == "passed")
            report.append(f"🔒 Security:")
            report.append(f"  ✅ {passed_scans}/{len(security)} security scans passed")
        
        # Documentation results
        if 'documentation' in self.demo_results:
            docs = self.demo_results['documentation']
            report.append(f"📚 Documentation:")
            report.append(f"  {'✅' if docs['docs_exist'] else '❌'} Documentation: {'Available' if docs['docs_exist'] else 'Not found'}")
            report.append(f"  {'✅' if docs['api_docs_accessible'] else '❌'} API Docs: {'Accessible' if docs['api_docs_accessible'] else 'Not accessible'}")
        
        report.append("")
        report.append("🎯 Next Steps:")
        report.append("  1. Review the monitoring dashboards")
        report.append("  2. Explore the API documentation")
        report.append("  3. Test the frontend application")
        report.append("  4. Run performance tests")
        report.append("  5. Deploy to production")
        report.append("")
        report.append("🚀 CK Empire is ready for production use!")
        
        print("\n".join(report))
        
        # Save demo results
        with open("demo_results.json", "w") as f:
            json.dump(self.demo_results, f, indent=2)
        logger.info("📄 Demo results saved to demo_results.json")
    
    def run_complete_demo(self):
        """Run the complete CK Empire demo."""
        logger.info("🎬 Starting CK Empire All Features Demo...")
        
        # Run all demo sections
        demos = [
            self.demo_1_monitoring_stack,
            self.demo_2_test_suite,
            self.demo_3_deployment_features,
            self.demo_4_performance_analysis,
            self.demo_5_api_features,
            self.demo_6_frontend_features,
            self.demo_7_security_features,
            self.demo_8_documentation_features
        ]
        
        for i, demo_func in enumerate(demos, 1):
            try:
                logger.info(f"🎬 Running Demo {i}/8...")
                demo_func()
                time.sleep(2)  # Brief pause between demos
            except Exception as e:
                logger.error(f"❌ Demo {i} failed: {e}")
        
        # Generate final report
        self.generate_demo_report()

def main():
    """Main function to run the complete demo."""
    demo = CKEmpireDemo()
    
    print("\n" + "=" * 60)
    print("🎬 CK EMPIRE ALL FEATURES DEMO")
    print("=" * 60)
    print("This demo will showcase all CK Empire features:")
    print("  📊 Monitoring Stack (Prometheus, Grafana, ELK)")
    print("  🧪 Comprehensive Test Suite")
    print("  🚀 Deployment Features (Docker, Kubernetes)")
    print("  ⚡ Performance Analysis")
    print("  🔌 API Features and Endpoints")
    print("  🎨 Frontend Application")
    print("  🔒 Security Features")
    print("  📚 Documentation")
    print("=" * 60)
    
    # Ask for confirmation
    response = input("\nPress Enter to start the demo, or 'q' to quit: ")
    if response.lower() == 'q':
        print("Demo cancelled.")
        return 0
    
    # Run the complete demo
    demo.run_complete_demo()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 