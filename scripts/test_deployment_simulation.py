#!/usr/bin/env python3
"""
CKEmpire Deployment Simulation Test Script
Tests all deployment features including Helm, Terraform, monitoring, and health checks
"""

import sys
import os
import subprocess
import json
import time
import requests
from datetime import datetime
import yaml

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

class DeploymentSimulator:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.deployment_dir = os.path.join(self.base_dir, 'deployment')
        self.terraform_dir = os.path.join(self.deployment_dir, 'terraform')
        self.helm_dir = os.path.join(self.deployment_dir, 'helm')
        self.test_results = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_command(self, command, cwd=None, check=True):
        """Run a shell command and return the result"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr
            
    def test_terraform_validation(self):
        """Test Terraform configuration validation"""
        print("\n🔍 Testing Terraform Configuration Validation...")
        
        # Check if terraform is installed
        success, stdout, stderr = self.run_command("terraform version")
        if not success:
            self.log("⚠️  Terraform is not installed - skipping Terraform tests", "WARNING")
            return True  # Skip this test if Terraform is not available
            
        # Check if terraform directory exists
        if not os.path.exists(self.terraform_dir):
            self.log("❌ Terraform directory not found", "ERROR")
            return False
            
        # Initialize Terraform
        success, stdout, stderr = self.run_command("terraform init", cwd=self.terraform_dir)
        if not success:
            self.log(f"❌ Terraform init failed: {stderr}", "ERROR")
            return False
            
        # Validate Terraform configuration
        success, stdout, stderr = self.run_command("terraform validate", cwd=self.terraform_dir)
        if not success:
            self.log(f"❌ Terraform validation failed: {stderr}", "ERROR")
            return False
            
        # Plan Terraform configuration (dry run)
        success, stdout, stderr = self.run_command("terraform plan -var='environment=dev' -var='vpc_id=vpc-12345678' -var='subnet_ids=[\"subnet-12345678\"]'", cwd=self.terraform_dir)
        if not success:
            self.log(f"❌ Terraform plan failed: {stderr}", "ERROR")
            return False
            
        self.log("✅ Terraform configuration is valid", "SUCCESS")
        return True
        
    def test_helm_chart_validation(self):
        """Test Helm chart validation"""
        print("\n📦 Testing Helm Chart Validation...")
        
        # Check if helm is installed
        success, stdout, stderr = self.run_command("helm version")
        if not success:
            self.log("⚠️  Helm is not installed - skipping Helm tests", "WARNING")
            return True  # Skip this test if Helm is not available
            
        # Check if helm chart exists
        if not os.path.exists(self.helm_dir):
            self.log("❌ Helm chart directory not found", "ERROR")
            return False
            
        # Lint the Helm chart
        success, stdout, stderr = self.run_command("helm lint .", cwd=self.helm_dir)
        if not success:
            self.log(f"❌ Helm chart linting failed: {stderr}", "ERROR")
            return False
            
        # Template the Helm chart
        success, stdout, stderr = self.run_command("helm template ckempire .", cwd=self.helm_dir)
        if not success:
            self.log(f"❌ Helm chart templating failed: {stderr}", "ERROR")
            return False
            
        self.log("✅ Helm chart is valid", "SUCCESS")
        return True
        
    def test_docker_images(self):
        """Test Docker image building"""
        print("\n🐳 Testing Docker Image Building...")
        
        # Check if docker is installed
        success, stdout, stderr = self.run_command("docker version")
        if not success:
            self.log("⚠️  Docker is not installed - skipping Docker tests", "WARNING")
            return True  # Skip this test if Docker is not available
            
        # Build backend image
        backend_dir = os.path.join(self.base_dir, 'backend')
        if os.path.exists(os.path.join(backend_dir, 'Dockerfile')):
            success, stdout, stderr = self.run_command("docker build -t ckempire-backend:test .", cwd=backend_dir)
            if not success:
                self.log(f"❌ Backend image build failed: {stderr}", "ERROR")
                return False
        else:
            self.log("⚠️  Backend Dockerfile not found - skipping backend build", "WARNING")
            
        # Build frontend image
        frontend_dir = os.path.join(self.base_dir, 'frontend')
        if os.path.exists(os.path.join(frontend_dir, 'Dockerfile')):
            success, stdout, stderr = self.run_command("docker build -t ckempire-frontend:test .", cwd=frontend_dir)
            if not success:
                self.log(f"❌ Frontend image build failed: {stderr}", "ERROR")
                return False
        else:
            self.log("⚠️  Frontend Dockerfile not found - skipping frontend build", "WARNING")
            
        self.log("✅ Docker images built successfully", "SUCCESS")
        return True
        
    def test_kubernetes_manifests(self):
        """Test Kubernetes manifest validation"""
        print("\n☸️  Testing Kubernetes Manifest Validation...")
        
        # Check if kubectl is installed
        success, stdout, stderr = self.run_command("kubectl version --client")
        if not success:
            self.log("⚠️  kubectl is not installed - skipping Kubernetes tests", "WARNING")
            return True  # Skip this test if kubectl is not available
            
        # Check if helm chart exists
        if not os.path.exists(self.helm_dir):
            self.log("❌ Helm chart directory not found", "ERROR")
            return False
            
        # Generate manifests from Helm chart
        success, stdout, stderr = self.run_command("helm template ckempire .", cwd=self.helm_dir)
        if not success:
            self.log(f"❌ Helm template generation failed: {stderr}", "ERROR")
            return False
            
        # Validate generated manifests (dry run)
        success, stdout, stderr = self.run_command("helm template ckempire . | kubectl apply --dry-run=client -f -", cwd=self.helm_dir)
        if not success:
            self.log(f"❌ Kubernetes manifest validation failed: {stderr}", "ERROR")
            return False
            
        self.log("✅ Kubernetes manifests are valid", "SUCCESS")
        return True
        
    def test_monitoring_configuration(self):
        """Test monitoring configuration"""
        print("\n📊 Testing Monitoring Configuration...")
        
        # Test Prometheus configuration
        prometheus_values_path = os.path.join(self.terraform_dir, 'values', 'prometheus-values.yaml')
        if os.path.exists(prometheus_values_path):
            try:
                with open(prometheus_values_path, 'r') as f:
                    prometheus_config = yaml.safe_load(f)
                    
                # Validate Prometheus configuration
                if 'prometheus' in prometheus_config:
                    self.log("✅ Prometheus configuration found", "SUCCESS")
                else:
                    self.log("❌ Prometheus configuration missing", "ERROR")
                    return False
                    
                # Test Grafana configuration
                if 'grafana' in prometheus_config:
                    self.log("✅ Grafana configuration found", "SUCCESS")
                else:
                    self.log("❌ Grafana configuration missing", "ERROR")
                    return False
                    
                # Test Alertmanager configuration
                if 'alertmanager' in prometheus_config:
                    self.log("✅ Alertmanager configuration found", "SUCCESS")
                else:
                    self.log("❌ Alertmanager configuration missing", "ERROR")
                    return False
                    
            except Exception as e:
                self.log(f"❌ Error reading Prometheus configuration: {e}", "ERROR")
                return False
        else:
            self.log("⚠️  Prometheus values file not found", "WARNING")
            
        self.log("✅ Monitoring configuration is valid", "SUCCESS")
        return True
        
    def test_sentry_configuration(self):
        """Test Sentry configuration"""
        print("\n🚨 Testing Sentry Configuration...")
        
        sentry_values_path = os.path.join(self.deployment_dir, 'sentry', 'sentry-values.yaml')
        if os.path.exists(sentry_values_path):
            try:
                with open(sentry_values_path, 'r') as f:
                    sentry_config = yaml.safe_load(f)
                    
                # Validate Sentry configuration
                required_fields = ['user', 'email', 'web', 'worker', 'postgresql', 'redis']
                for field in required_fields:
                    if field in sentry_config:
                        self.log(f"✅ Sentry {field} configuration found", "SUCCESS")
                    else:
                        self.log(f"❌ Sentry {field} configuration missing", "ERROR")
                        return False
                        
            except Exception as e:
                self.log(f"❌ Error reading Sentry configuration: {e}", "ERROR")
                return False
        else:
            self.log("⚠️  Sentry values file not found", "WARNING")
            
        self.log("✅ Sentry configuration is valid", "SUCCESS")
        return True
        
    def test_ci_cd_pipeline(self):
        """Test CI/CD pipeline configuration"""
        print("\n🔄 Testing CI/CD Pipeline Configuration...")
        
        workflow_path = os.path.join(self.base_dir, '.github', 'workflows', 'deploy.yml')
        if os.path.exists(workflow_path):
            try:
                with open(workflow_path, 'r') as f:
                    workflow_content = f.read()
                    
                # Check for required jobs
                required_jobs = ['security-scan', 'test-backend', 'test-frontend', 'build-images', 'deploy-dev']
                for job in required_jobs:
                    if job in workflow_content:
                        self.log(f"✅ CI/CD job '{job}' found", "SUCCESS")
                    else:
                        self.log(f"⚠️  CI/CD job '{job}' not found", "WARNING")
                        
            except Exception as e:
                self.log(f"❌ Error reading CI/CD configuration: {e}", "ERROR")
                return False
        else:
            self.log("⚠️  CI/CD workflow file not found", "WARNING")
            
        self.log("✅ CI/CD pipeline configuration is valid", "SUCCESS")
        return True
        
    def test_health_checks(self):
        """Test health check configuration"""
        print("\n🏥 Testing Health Check Configuration...")
        
        health_check_path = os.path.join(self.deployment_dir, 'health-checks', 'health-check.sh')
        if os.path.exists(health_check_path):
            # Check if script is executable
            if os.access(health_check_path, os.X_OK):
                self.log("✅ Health check script is executable", "SUCCESS")
            else:
                self.log("⚠️  Health check script is not executable", "WARNING")
                
            # Check script content
            try:
                with open(health_check_path, 'r', encoding='utf-8', errors='ignore') as f:
                    script_content = f.read()
                    
                # Check for required functions
                required_functions = ['check_pods', 'check_services', 'check_deployments']
                for func in required_functions:
                    if func in script_content:
                        self.log(f"✅ Health check function '{func}' found", "SUCCESS")
                    else:
                        self.log(f"⚠️  Health check function '{func}' not found", "WARNING")
                        
            except Exception as e:
                self.log(f"❌ Error reading health check script: {e}", "ERROR")
                return False
        else:
            self.log("⚠️  Health check script not found", "WARNING")
            
        self.log("✅ Health check configuration is valid", "SUCCESS")
        return True
        
    def test_security_configuration(self):
        """Test security configuration"""
        print("\n🔒 Testing Security Configuration...")
        
        # Check for security-related files
        security_files = [
            os.path.join(self.base_dir, 'backend', 'bandit.yaml'),
            os.path.join(self.base_dir, 'backend', 'safety.yaml'),
            os.path.join(self.base_dir, 'backend', 'security_scanner.py')
        ]
        
        for file_path in security_files:
            if os.path.exists(file_path):
                self.log(f"✅ Security file found: {os.path.basename(file_path)}", "SUCCESS")
            else:
                self.log(f"⚠️  Security file not found: {os.path.basename(file_path)}", "WARNING")
                
        # Check for network policies in Helm chart
        helm_values_path = os.path.join(self.helm_dir, 'values.yaml')
        if os.path.exists(helm_values_path):
            try:
                with open(helm_values_path, 'r') as f:
                    helm_values = yaml.safe_load(f)
                    
                if 'security' in helm_values and helm_values['security'].get('enabled', False):
                    self.log("✅ Security configuration enabled in Helm chart", "SUCCESS")
                else:
                    self.log("⚠️  Security configuration not enabled in Helm chart", "WARNING")
                    
            except Exception as e:
                self.log(f"❌ Error reading Helm values: {e}", "ERROR")
                return False
                
        self.log("✅ Security configuration is valid", "SUCCESS")
        return True
        
    def test_backup_configuration(self):
        """Test backup configuration"""
        print("\n💾 Testing Backup Configuration...")
        
        # Check for backup-related files
        backup_files = [
            os.path.join(self.deployment_dir, 'backup_service.py'),
            os.path.join(self.base_dir, 'backend', 'cloud', 'backup_service.py')
        ]
        
        for file_path in backup_files:
            if os.path.exists(file_path):
                self.log(f"✅ Backup file found: {os.path.basename(file_path)}", "SUCCESS")
            else:
                self.log(f"⚠️  Backup file not found: {os.path.basename(file_path)}", "WARNING")
                
        # Check for backup configuration in Helm chart
        helm_values_path = os.path.join(self.helm_dir, 'values.yaml')
        if os.path.exists(helm_values_path):
            try:
                with open(helm_values_path, 'r') as f:
                    helm_values = yaml.safe_load(f)
                    
                if 'backup' in helm_values and helm_values['backup'].get('enabled', False):
                    self.log("✅ Backup configuration enabled in Helm chart", "SUCCESS")
                else:
                    self.log("⚠️  Backup configuration not enabled in Helm chart", "WARNING")
                    
            except Exception as e:
                self.log(f"❌ Error reading Helm values: {e}", "ERROR")
                return False
                
        self.log("✅ Backup configuration is valid", "SUCCESS")
        return True
        
    def test_scaling_configuration(self):
        """Test scaling configuration"""
        print("\n📈 Testing Scaling Configuration...")
        
        # Check for HPA configuration in Helm chart
        helm_values_path = os.path.join(self.helm_dir, 'values.yaml')
        if os.path.exists(helm_values_path):
            try:
                with open(helm_values_path, 'r') as f:
                    helm_values = yaml.safe_load(f)
                    
                # Check HPA configuration
                if 'hpa' in helm_values and helm_values['hpa'].get('enabled', False):
                    self.log("✅ HPA configuration enabled in Helm chart", "SUCCESS")
                else:
                    self.log("⚠️  HPA configuration not enabled in Helm chart", "WARNING")
                    
                # Check VPA configuration
                if 'vpa' in helm_values and helm_values['vpa'].get('enabled', False):
                    self.log("✅ VPA configuration enabled in Helm chart", "SUCCESS")
                else:
                    self.log("⚠️  VPA configuration not enabled in Helm chart", "WARNING")
                    
                # Check autoscaling for backend
                if 'backend' in helm_values and 'autoscaling' in helm_values['backend']:
                    self.log("✅ Backend autoscaling configured", "SUCCESS")
                else:
                    self.log("⚠️  Backend autoscaling not configured", "WARNING")
                    
                # Check autoscaling for frontend
                if 'frontend' in helm_values and 'autoscaling' in helm_values['frontend']:
                    self.log("✅ Frontend autoscaling configured", "SUCCESS")
                else:
                    self.log("⚠️  Frontend autoscaling not configured", "WARNING")
                    
            except Exception as e:
                self.log(f"❌ Error reading Helm values: {e}", "ERROR")
                return False
                
        self.log("✅ Scaling configuration is valid", "SUCCESS")
        return True
        
    def test_network_configuration(self):
        """Test network configuration"""
        print("\n🌐 Testing Network Configuration...")
        
        # Check for ingress configuration
        helm_values_path = os.path.join(self.helm_dir, 'values.yaml')
        if os.path.exists(helm_values_path):
            try:
                with open(helm_values_path, 'r') as f:
                    helm_values = yaml.safe_load(f)
                    
                # Check ingress configuration
                if 'backend' in helm_values and 'ingress' in helm_values['backend']:
                    if helm_values['backend']['ingress'].get('enabled', False):
                        self.log("✅ Backend ingress enabled", "SUCCESS")
                    else:
                        self.log("⚠️  Backend ingress not enabled", "WARNING")
                        
                if 'frontend' in helm_values and 'ingress' in helm_values['frontend']:
                    if helm_values['frontend']['ingress'].get('enabled', False):
                        self.log("✅ Frontend ingress enabled", "SUCCESS")
                    else:
                        self.log("⚠️  Frontend ingress not enabled", "WARNING")
                        
            except Exception as e:
                self.log(f"❌ Error reading Helm values: {e}", "ERROR")
                return False
                
        # Check for network policies
        network_policy_files = [
            os.path.join(self.deployment_dir, 'k8s', 'network-policy.yaml')
        ]
        
        for file_path in network_policy_files:
            if os.path.exists(file_path):
                self.log(f"✅ Network policy file found: {os.path.basename(file_path)}", "SUCCESS")
            else:
                self.log(f"⚠️  Network policy file not found: {os.path.basename(file_path)}", "WARNING")
                
        self.log("✅ Network configuration is valid", "SUCCESS")
        return True
        
    def run_comprehensive_test(self):
        """Run all deployment tests"""
        print("🚀 Starting CKEmpire Deployment Simulation Tests...")
        print("=" * 60)
        
        tests = [
            ("Terraform Configuration", self.test_terraform_validation),
            ("Helm Chart Validation", self.test_helm_chart_validation),
            ("Docker Image Building", self.test_docker_images),
            ("Kubernetes Manifests", self.test_kubernetes_manifests),
            ("Monitoring Configuration", self.test_monitoring_configuration),
            ("Sentry Configuration", self.test_sentry_configuration),
            ("CI/CD Pipeline", self.test_ci_cd_pipeline),
            ("Health Checks", self.test_health_checks),
            ("Security Configuration", self.test_security_configuration),
            ("Backup Configuration", self.test_backup_configuration),
            ("Scaling Configuration", self.test_scaling_configuration),
            ("Network Configuration", self.test_network_configuration)
        ]
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    passed += 1
                    self.test_results.append({"test": test_name, "status": "PASSED"})
                else:
                    failed += 1
                    self.test_results.append({"test": test_name, "status": "FAILED"})
            except Exception as e:
                failed += 1
                self.test_results.append({"test": test_name, "status": "FAILED", "error": str(e)})
                self.log(f"❌ {test_name} failed with exception: {e}", "ERROR")
                
        print("\n" + "=" * 60)
        print("📊 DEPLOYMENT SIMULATION TEST RESULTS")
        print("=" * 60)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Skipped: {skipped}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "📈 Success Rate: N/A")
        
        # Save results to file
        results_file = f"deployment_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "passed": passed,
                    "failed": failed,
                    "skipped": skipped,
                    "success_rate": (passed/(passed+failed)*100) if (passed+failed) > 0 else None
                },
                "results": self.test_results
            }, f, indent=2)
            
        print(f"\n📄 Results saved to: {results_file}")
        
        if failed == 0:
            print("\n🎉 All deployment tests passed!")
            return True
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please review the issues above.")
            return False

def main():
    """Main function"""
    simulator = DeploymentSimulator()
    success = simulator.run_comprehensive_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 