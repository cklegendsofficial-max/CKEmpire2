#!/usr/bin/env python3
"""
Comprehensive Test Runner for CK Empire
Runs all types of tests and generates reports
"""

import os
import sys
import subprocess
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
import shutil

class TestRunner:
    """Comprehensive test runner for CK Empire"""
    
    def __init__(self, args):
        self.args = args
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        self.start_time = time.time()
        self.results = {
            "unit_tests": {},
            "integration_tests": {},
            "e2e_tests": {},
            "load_tests": {},
            "security_tests": {},
            "coverage": {},
            "performance": {},
            "summary": {}
        }
    
    def run_command(self, command, description, capture_output=True):
        """Run a command and capture results"""
        print(f"\n🔧 {description}")
        print(f"Command: {' '.join(command)}")
        
        try:
            if capture_output:
                result = subprocess.run(command, capture_output=True, text=True, timeout=300)
            else:
                result = subprocess.run(command, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ {description} completed successfully")
                return True, result.stdout if capture_output else ""
            else:
                print(f"❌ {description} failed with return code {result.returncode}")
                if capture_output and result.stderr:
                    print(f"Error: {result.stderr}")
                return False, result.stderr if capture_output else ""
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} timed out")
            return False, "Timeout"
        except Exception as e:
            print(f"💥 {description} failed with exception: {e}")
            return False, str(e)
    
    def run_unit_tests(self):
        """Run unit tests with pytest"""
        print("\n" + "="*60)
        print("🧪 RUNNING UNIT TESTS")
        print("="*60)
        
        command = [
            "python", "-m", "pytest",
            "tests/",
            "-m", "unit",
            "--cov=.",
            "--cov-report=html:reports/coverage-html",
            "--cov-report=xml:reports/coverage.xml",
            "--cov-report=term-missing",
            "--cov-fail-under=90",
            "--html=reports/unit-tests-report.html",
            "--json-report=reports/unit-tests-report.json",
            "-v"
        ]
        
        success, output = self.run_command(command, "Unit Tests")
        self.results["unit_tests"] = {
            "success": success,
            "output": output
        }
        return success
    
    def run_integration_tests(self):
        """Run integration tests"""
        print("\n" + "="*60)
        print("🔗 RUNNING INTEGRATION TESTS")
        print("="*60)
        
        command = [
            "python", "-m", "pytest",
            "tests/",
            "-m", "integration",
            "--html=reports/integration-tests-report.html",
            "--json-report=reports/integration-tests-report.json",
            "-v"
        ]
        
        success, output = self.run_command(command, "Integration Tests")
        self.results["integration_tests"] = {
            "success": success,
            "output": output
        }
        return success
    
    def run_e2e_tests(self):
        """Run end-to-end tests with Selenium"""
        print("\n" + "="*60)
        print("🌐 RUNNING E2E TESTS")
        print("="*60)
        
        # Check if frontend is running
        try:
            import requests
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code != 200:
                print("⚠️  Frontend not running on localhost:3000, skipping E2E tests")
                self.results["e2e_tests"] = {
                    "success": False,
                    "output": "Frontend not available"
                }
                return False
        except:
            print("⚠️  Frontend not running on localhost:3000, skipping E2E tests")
            self.results["e2e_tests"] = {
                "success": False,
                "output": "Frontend not available"
            }
            return False
        
        command = [
            "python", "-m", "pytest",
            "tests/test_e2e_selenium.py",
            "-m", "e2e",
            "--html=reports/e2e-tests-report.html",
            "--json-report=reports/e2e-tests-report.json",
            "-v"
        ]
        
        success, output = self.run_command(command, "E2E Tests")
        self.results["e2e_tests"] = {
            "success": success,
            "output": output
        }
        return success
    
    def run_load_tests(self):
        """Run load tests with Locust"""
        print("\n" + "="*60)
        print("⚡ RUNNING LOAD TESTS")
        print("="*60)
        
        # Check if backend is running
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code != 200:
                print("⚠️  Backend not running on localhost:8000, skipping load tests")
                self.results["load_tests"] = {
                    "success": False,
                    "output": "Backend not available"
                }
                return False
        except:
            print("⚠️  Backend not running on localhost:8000, skipping load tests")
            self.results["load_tests"] = {
                "success": False,
                "output": "Backend not available"
            }
            return False
        
        # Run Locust for a short duration
        command = [
            "locust",
            "-f", "tests/load/locustfile.py",
            "--host=http://localhost:8000",
            "--users", "5",
            "--spawn-rate", "1",
            "--run-time", "60s",
            "--headless",
            "--html=reports/load-test-report.html",
            "--csv=reports/load-test-results"
        ]
        
        success, output = self.run_command(command, "Load Tests")
        self.results["load_tests"] = {
            "success": success,
            "output": output
        }
        return success
    
    def run_security_tests(self):
        """Run security tests with Bandit and Safety"""
        print("\n" + "="*60)
        print("🔒 RUNNING SECURITY TESTS")
        print("="*60)
        
        # Run Bandit
        bandit_command = [
            "bandit",
            "-r", ".",
            "-f", "json",
            "-o", "reports/bandit-report.json",
            "-c", "bandit.yaml"
        ]
        
        bandit_success, bandit_output = self.run_command(bandit_command, "Bandit Security Scan")
        
        # Run Safety
        safety_command = [
            "safety",
            "check",
            "--json",
            "--output", "reports/safety-report.json"
        ]
        
        safety_success, safety_output = self.run_command(safety_command, "Safety Dependency Check")
        
        # Run Semgrep (if available)
        semgrep_command = [
            "semgrep",
            "--config=auto",
            "--json",
            "--output=reports/semgrep-report.json",
            "."
        ]
        
        try:
            semgrep_success, semgrep_output = self.run_command(semgrep_command, "Semgrep Security Scan")
        except FileNotFoundError:
            print("⚠️  Semgrep not installed, skipping")
            semgrep_success, semgrep_output = False, "Semgrep not available"
        
        overall_success = bandit_success and safety_success
        
        self.results["security_tests"] = {
            "success": overall_success,
            "bandit": {"success": bandit_success, "output": bandit_output},
            "safety": {"success": safety_success, "output": safety_output},
            "semgrep": {"success": semgrep_success, "output": semgrep_output}
        }
        
        return overall_success
    
    def run_performance_tests(self):
        """Run performance tests"""
        print("\n" + "="*60)
        print("📊 RUNNING PERFORMANCE TESTS")
        print("="*60)
        
        command = [
            "python", "-m", "pytest",
            "tests/",
            "-m", "performance",
            "--benchmark-only",
            "--benchmark-skip",
            "--benchmark-min-rounds=10",
            "--benchmark-warmup=on",
            "--benchmark-disable-gc",
            "--html=reports/performance-tests-report.html",
            "--json-report=reports/performance-tests-report.json",
            "-v"
        ]
        
        success, output = self.run_command(command, "Performance Tests")
        self.results["performance"] = {
            "success": success,
            "output": output
        }
        return success
    
    def generate_coverage_report(self):
        """Generate comprehensive coverage report"""
        print("\n" + "="*60)
        print("📈 GENERATING COVERAGE REPORT")
        print("="*60)
        
        # Combine coverage from all test runs
        command = [
            "coverage", "combine",
            "--rcfile=.coveragerc"
        ]
        
        success, output = self.run_command(command, "Combining Coverage Data")
        
        if success:
            # Generate HTML report
            html_command = [
                "coverage", "html",
                "--directory=reports/coverage-html",
                "--rcfile=.coveragerc"
            ]
            self.run_command(html_command, "Generating HTML Coverage Report")
            
            # Generate XML report
            xml_command = [
                "coverage", "xml",
                "--output=reports/coverage.xml",
                "--rcfile=.coveragerc"
            ]
            self.run_command(xml_command, "Generating XML Coverage Report")
            
            # Get coverage percentage
            report_command = [
                "coverage", "report",
                "--rcfile=.coveragerc"
            ]
            success, output = self.run_command(report_command, "Coverage Report")
            
            self.results["coverage"] = {
                "success": success,
                "output": output
            }
        
        return success
    
    def generate_summary_report(self):
        """Generate comprehensive test summary"""
        print("\n" + "="*60)
        print("📋 GENERATING SUMMARY REPORT")
        print("="*60)
        
        end_time = time.time()
        duration = end_time - self.start_time
        
        # Calculate overall success
        all_tests = [
            self.results["unit_tests"]["success"],
            self.results["integration_tests"]["success"],
            self.results["e2e_tests"]["success"],
            self.results["load_tests"]["success"],
            self.results["security_tests"]["success"],
            self.results["performance"]["success"]
        ]
        
        overall_success = all(all_tests)
        success_count = sum(all_tests)
        total_count = len(all_tests)
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "overall_success": overall_success,
            "success_rate": f"{success_count}/{total_count}",
            "results": self.results,
            "reports_generated": [
                "reports/unit-tests-report.html",
                "reports/integration-tests-report.html",
                "reports/e2e-tests-report.html",
                "reports/load-test-report.html",
                "reports/bandit-report.json",
                "reports/safety-report.json",
                "reports/coverage-html/index.html"
            ]
        }
        
        # Save summary to JSON
        with open("reports/test-summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print(f"\n📊 TEST SUMMARY")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Overall Success: {'✅ PASS' if overall_success else '❌ FAIL'}")
        print(f"Success Rate: {success_count}/{total_count}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for test_type, result in self.results.items():
            if isinstance(result, dict) and "success" in result:
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                print(f"  {test_type.replace('_', ' ').title()}: {status}")
        
        print(f"\n📁 REPORTS GENERATED:")
        for report in summary["reports_generated"]:
            if os.path.exists(report):
                print(f"  ✅ {report}")
            else:
                print(f"  ❌ {report} (not found)")
        
        self.results["summary"] = summary
        return overall_success
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 CK EMPIRE COMPREHENSIVE TEST SUITE")
        print("="*60)
        
        # Run tests based on arguments
        if self.args.unit or self.args.all:
            self.run_unit_tests()
        
        if self.args.integration or self.args.all:
            self.run_integration_tests()
        
        if self.args.e2e or self.args.all:
            self.run_e2e_tests()
        
        if self.args.load or self.args.all:
            self.run_load_tests()
        
        if self.args.security or self.args.all:
            self.run_security_tests()
        
        if self.args.performance or self.args.all:
            self.run_performance_tests()
        
        # Generate coverage report if unit tests were run
        if self.args.unit or self.args.all:
            self.generate_coverage_report()
        
        # Generate summary
        overall_success = self.generate_summary_report()
        
        return overall_success

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="CK Empire Comprehensive Test Runner")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--e2e", action="store_true", help="Run E2E tests")
    parser.add_argument("--load", action="store_true", help="Run load tests")
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--clean", action="store_true", help="Clean previous test artifacts")
    
    args = parser.parse_args()
    
    # If no specific tests selected, run all
    if not any([args.unit, args.integration, args.e2e, args.load, args.security, args.performance, args.all]):
        args.all = True
    
    # Clean previous artifacts if requested
    if args.clean:
        print("🧹 Cleaning previous test artifacts...")
        for pattern in ["*.pyc", "__pycache__", ".pytest_cache", ".coverage", "htmlcov"]:
            for path in Path(".").rglob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
        print("✅ Cleanup completed")
    
    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Run tests
    runner = TestRunner(args)
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 