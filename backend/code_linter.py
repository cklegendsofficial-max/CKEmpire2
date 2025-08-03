#!/usr/bin/env python3
"""
CK Empire Code Linter
Comprehensive code quality analysis and linting for the entire project.
"""

import os
import sys
import subprocess
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeLinter:
    """Comprehensive code linter for CK Empire project."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.results = {
            'python_files': [],
            'javascript_files': [],
            'yaml_files': [],
            'markdown_files': [],
            'docker_files': [],
            'issues': [],
            'statistics': {}
        }
        
    def find_files(self, extensions: List[str]) -> List[Path]:
        """Find all files with given extensions."""
        files = []
        for ext in extensions:
            files.extend(self.project_root.rglob(f"*.{ext}"))
        return files
    
    def run_flake8(self) -> Dict[str, Any]:
        """Run flake8 for Python code style checking."""
        logger.info("Running flake8...")
        
        try:
            result = subprocess.run(
                ["flake8", "--max-line-length=88", "--extend-ignore=E203,W503"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            issues = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(':', 3)
                        if len(parts) >= 4:
                            issues.append({
                                'file': parts[0],
                                'line': int(parts[1]),
                                'column': int(parts[2]),
                                'message': parts[3].strip(),
                                'type': 'flake8'
                            })
            
            return {
                'success': result.returncode == 0,
                'issues': issues,
                'total_issues': len(issues)
            }
        except FileNotFoundError:
            logger.warning("flake8 not found, skipping...")
            return {'success': True, 'issues': [], 'total_issues': 0}
    
    def run_black_check(self) -> Dict[str, Any]:
        """Run black to check code formatting."""
        logger.info("Running black check...")
        
        try:
            result = subprocess.run(
                ["black", "--check", "--diff", "."],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            return {
                'success': result.returncode == 0,
                'needs_formatting': result.returncode != 0,
                'diff': result.stdout if result.stdout else None
            }
        except FileNotFoundError:
            logger.warning("black not found, skipping...")
            return {'success': True, 'needs_formatting': False}
    
    def run_isort_check(self) -> Dict[str, Any]:
        """Run isort to check import sorting."""
        logger.info("Running isort check...")
        
        try:
            result = subprocess.run(
                ["isort", "--check-only", "--diff"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            return {
                'success': result.returncode == 0,
                'needs_sorting': result.returncode != 0,
                'diff': result.stdout if result.stdout else None
            }
        except FileNotFoundError:
            logger.warning("isort not found, skipping...")
            return {'success': True, 'needs_sorting': False}
    
    def run_mypy(self) -> Dict[str, Any]:
        """Run mypy for type checking."""
        logger.info("Running mypy...")
        
        try:
            result = subprocess.run(
                ["mypy", "--ignore-missing-imports", "--no-strict-optional"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            issues = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line and ':' in line:
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            issues.append({
                                'file': parts[0],
                                'line': int(parts[1]) if parts[1].isdigit() else 0,
                                'message': parts[2].strip(),
                                'type': 'mypy'
                            })
            
            return {
                'success': result.returncode == 0,
                'issues': issues,
                'total_issues': len(issues)
            }
        except FileNotFoundError:
            logger.warning("mypy not found, skipping...")
            return {'success': True, 'issues': [], 'total_issues': 0}
    
    def run_bandit(self) -> Dict[str, Any]:
        """Run bandit for security analysis."""
        logger.info("Running bandit...")
        
        try:
            result = subprocess.run(
                ["bandit", "-r", ".", "-f", "json"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.stdout:
                try:
                    bandit_results = json.loads(result.stdout)
                    return {
                        'success': True,
                        'issues': bandit_results.get('results', []),
                        'total_issues': len(bandit_results.get('results', [])),
                        'metrics': bandit_results.get('metrics', {})
                    }
                except json.JSONDecodeError:
                    logger.warning("Failed to parse bandit JSON output")
                    return {'success': True, 'issues': [], 'total_issues': 0}
            
            return {'success': True, 'issues': [], 'total_issues': 0}
        except FileNotFoundError:
            logger.warning("bandit not found, skipping...")
            return {'success': True, 'issues': [], 'total_issues': 0}
    
    def run_eslint(self) -> Dict[str, Any]:
        """Run ESLint for JavaScript/TypeScript files."""
        logger.info("Running ESLint...")
        
        js_files = self.find_files(['js', 'jsx', 'ts', 'tsx'])
        if not js_files:
            return {'success': True, 'issues': [], 'total_issues': 0}
        
        try:
            result = subprocess.run(
                ["npx", "eslint", "--format", "json", "."],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.stdout:
                try:
                    eslint_results = json.loads(result.stdout)
                    issues = []
                    for file_result in eslint_results:
                        for message in file_result.get('messages', []):
                            issues.append({
                                'file': file_result['filePath'],
                                'line': message.get('line', 0),
                                'column': message.get('column', 0),
                                'message': message.get('message', ''),
                                'severity': message.get('severity', 1),
                                'type': 'eslint'
                            })
                    
                    return {
                        'success': result.returncode == 0,
                        'issues': issues,
                        'total_issues': len(issues)
                    }
                except json.JSONDecodeError:
                    logger.warning("Failed to parse ESLint JSON output")
                    return {'success': True, 'issues': [], 'total_issues': 0}
            
            return {'success': True, 'issues': [], 'total_issues': 0}
        except FileNotFoundError:
            logger.warning("ESLint not found, skipping...")
            return {'success': True, 'issues': [], 'total_issues': 0}
    
    def analyze_python_complexity(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Python file complexity."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Count functions, classes, imports
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            
            # Calculate cyclomatic complexity
            complexity = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler, 
                                   ast.With, ast.Assert, ast.Raise)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
            
            return {
                'functions': len(functions),
                'classes': len(classes),
                'imports': len(imports),
                'complexity': complexity,
                'lines': len(content.split('\n'))
            }
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return {}
    
    def check_docker_best_practices(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check Dockerfile for best practices."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Check for common issues
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Check for root user
                if line.startswith('USER root') or line.startswith('USER 0'):
                    issues.append({
                        'line': i,
                        'message': 'Avoid running as root user',
                        'severity': 'warning'
                    })
                
                # Check for latest tag
                if 'FROM' in line and ':latest' in line:
                    issues.append({
                        'line': i,
                        'message': 'Avoid using :latest tag for better reproducibility',
                        'severity': 'info'
                    })
                
                # Check for unnecessary packages
                if 'apt-get install' in line and any(pkg in line for pkg in ['vim', 'nano', 'curl', 'wget']):
                    if not any(pkg in line for pkg in ['curl', 'wget']) or 'curl' not in line:
                        issues.append({
                            'line': i,
                            'message': 'Consider removing unnecessary packages',
                            'severity': 'info'
                        })
            
            return issues
        except Exception as e:
            logger.error(f"Error checking Dockerfile {file_path}: {e}")
            return []
    
    def check_yaml_syntax(self, file_path: Path) -> Dict[str, Any]:
        """Check YAML file syntax."""
        try:
            import yaml
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            return {'valid': True, 'issues': []}
        except Exception as e:
            return {
                'valid': False,
                'issues': [{'message': str(e), 'severity': 'error'}]
            }
    
    def run_comprehensive_linting(self) -> Dict[str, Any]:
        """Run comprehensive linting on the entire project."""
        logger.info("Starting comprehensive code linting...")
        
        # Find all files
        python_files = self.find_files(['py'])
        js_files = self.find_files(['js', 'jsx', 'ts', 'tsx'])
        yaml_files = self.find_files(['yml', 'yaml'])
        md_files = self.find_files(['md'])
        docker_files = self.find_files(['dockerfile', 'Dockerfile'])
        
        self.results['python_files'] = [str(f) for f in python_files]
        self.results['javascript_files'] = [str(f) for f in js_files]
        self.results['yaml_files'] = [str(f) for f in yaml_files]
        self.results['markdown_files'] = [str(f) for f in md_files]
        self.results['docker_files'] = [str(f) for f in docker_files]
        
        # Run Python linters
        flake8_results = self.run_flake8()
        black_results = self.run_black_check()
        isort_results = self.run_isort_check()
        mypy_results = self.run_mypy()
        bandit_results = self.run_bandit()
        
        # Run JavaScript linters
        eslint_results = self.run_eslint()
        
        # Analyze Python complexity
        complexity_results = {}
        for py_file in python_files:
            complexity_results[str(py_file)] = self.analyze_python_complexity(py_file)
        
        # Check Docker best practices
        docker_issues = []
        for docker_file in docker_files:
            docker_issues.extend(self.check_docker_best_practices(docker_file))
        
        # Check YAML syntax
        yaml_results = {}
        for yaml_file in yaml_files:
            yaml_results[str(yaml_file)] = self.check_yaml_syntax(yaml_file)
        
        # Compile results
        all_results = {
            'flake8': flake8_results,
            'black': black_results,
            'isort': isort_results,
            'mypy': mypy_results,
            'bandit': bandit_results,
            'eslint': eslint_results,
            'complexity': complexity_results,
            'docker_issues': docker_issues,
            'yaml_results': yaml_results
        }
        
        # Generate statistics
        total_issues = (
            flake8_results['total_issues'] +
            mypy_results['total_issues'] +
            bandit_results['total_issues'] +
            eslint_results['total_issues'] +
            len(docker_issues)
        )
        
        self.results['statistics'] = {
            'total_files': len(python_files) + len(js_files) + len(yaml_files) + len(md_files) + len(docker_files),
            'python_files': len(python_files),
            'javascript_files': len(js_files),
            'yaml_files': len(yaml_files),
            'markdown_files': len(md_files),
            'docker_files': len(docker_files),
            'total_issues': total_issues,
            'critical_issues': sum(1 for issue in bandit_results['issues'] if issue.get('severity') == 'HIGH'),
            'formatting_issues': (0 if black_results['success'] else 1) + (0 if isort_results['success'] else 1)
        }
        
        return all_results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive linting report."""
        report = []
        report.append("=" * 60)
        report.append("CK EMPIRE CODE LINTING REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Statistics
        stats = self.results['statistics']
        report.append("📊 PROJECT STATISTICS")
        report.append("-" * 40)
        report.append(f"  Total files: {stats['total_files']}")
        report.append(f"  Python files: {stats['python_files']}")
        report.append(f"  JavaScript files: {stats['javascript_files']}")
        report.append(f"  YAML files: {stats['yaml_files']}")
        report.append(f"  Markdown files: {stats['markdown_files']}")
        report.append(f"  Docker files: {stats['docker_files']}")
        report.append("")
        
        # Issues summary
        report.append("🚨 ISSUES SUMMARY")
        report.append("-" * 40)
        report.append(f"  Total issues: {stats['total_issues']}")
        report.append(f"  Critical security issues: {stats['critical_issues']}")
        report.append(f"  Formatting issues: {stats['formatting_issues']}")
        report.append("")
        
        # Detailed results
        report.append("📋 DETAILED RESULTS")
        report.append("-" * 40)
        
        # Python linting results
        if results['flake8']['total_issues'] > 0:
            report.append("  🔍 Flake8 Issues:")
            for issue in results['flake8']['issues'][:5]:  # Show first 5
                report.append(f"    {issue['file']}:{issue['line']} - {issue['message']}")
            if len(results['flake8']['issues']) > 5:
                report.append(f"    ... and {len(results['flake8']['issues']) - 5} more issues")
        
        if not results['black']['success']:
            report.append("  🎨 Black: Code formatting issues detected")
        
        if not results['isort']['success']:
            report.append("  📦 isort: Import sorting issues detected")
        
        if results['mypy']['total_issues'] > 0:
            report.append("  🔍 MyPy Issues:")
            for issue in results['mypy']['issues'][:5]:
                report.append(f"    {issue['file']}:{issue['line']} - {issue['message']}")
        
        if results['bandit']['total_issues'] > 0:
            report.append("  🔒 Security Issues (Bandit):")
            for issue in results['bandit']['issues'][:5]:
                report.append(f"    {issue.get('filename', 'unknown')}:{issue.get('line_number', 0)} - {issue.get('issue_text', '')}")
        
        if results['eslint']['total_issues'] > 0:
            report.append("  🔍 ESLint Issues:")
            for issue in results['eslint']['issues'][:5]:
                report.append(f"    {issue['file']}:{issue['line']} - {issue['message']}")
        
        if results['docker_issues']:
            report.append("  🐳 Docker Best Practices:")
            for issue in results['docker_issues'][:5]:
                report.append(f"    Line {issue['line']}: {issue['message']} ({issue['severity']})")
        
        # Complexity analysis
        high_complexity_files = []
        for file_path, complexity in results['complexity'].items():
            if complexity.get('complexity', 0) > 10:
                high_complexity_files.append((file_path, complexity['complexity']))
        
        if high_complexity_files:
            report.append("")
            report.append("  ⚠️  High Complexity Files:")
            for file_path, complexity in sorted(high_complexity_files, key=lambda x: x[1], reverse=True)[:5]:
                report.append(f"    {file_path}: complexity {complexity}")
        
        # Recommendations
        report.append("")
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 40)
        
        if stats['total_issues'] > 0:
            report.append("  🔧 Fix identified issues:")
            if results['flake8']['total_issues'] > 0:
                report.append("     - Run: flake8 --max-line-length=88")
            if not results['black']['success']:
                report.append("     - Run: black .")
            if not results['isort']['success']:
                report.append("     - Run: isort .")
            if results['mypy']['total_issues'] > 0:
                report.append("     - Fix type annotations")
            if stats['critical_issues'] > 0:
                report.append("     - Address security vulnerabilities")
        
        if high_complexity_files:
            report.append("  🔄 Refactor complex functions:")
            report.append("     - Break down functions with complexity > 10")
            report.append("     - Extract helper functions")
            report.append("     - Consider using design patterns")
        
        report.append("  ✅ Best practices:")
        report.append("     - Keep functions small and focused")
        report.append("     - Use meaningful variable names")
        report.append("     - Add comprehensive docstrings")
        report.append("     - Write unit tests for complex logic")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_results(self, results: Dict[str, Any], filename: str = "linting_results.json"):
        """Save linting results to JSON file."""
        output = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.results['statistics'],
            'results': results,
            'file_counts': {
                'python_files': self.results['python_files'],
                'javascript_files': self.results['javascript_files'],
                'yaml_files': self.results['yaml_files'],
                'markdown_files': self.results['markdown_files'],
                'docker_files': self.results['docker_files']
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"Linting results saved to {filename}")

def main():
    """Main function to run comprehensive linting."""
    linter = CodeLinter()
    results = linter.run_comprehensive_linting()
    
    # Generate and print report
    report = linter.generate_report(results)
    print(report)
    
    # Save results
    linter.save_results(results)
    
    # Return exit code based on issues
    total_issues = linter.results['statistics']['total_issues']
    critical_issues = linter.results['statistics']['critical_issues']
    
    if critical_issues > 0:
        logger.error(f"Found {critical_issues} critical issues!")
        return 2
    elif total_issues > 0:
        logger.warning(f"Found {total_issues} issues to address")
        return 1
    else:
        logger.info("No issues found! Code quality is excellent.")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 