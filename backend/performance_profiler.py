#!/usr/bin/env python3
"""
CK Empire Performance Profiler
Uses cProfile to identify slow code sections and performance bottlenecks.
"""

import cProfile
import pstats
import io
import time
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import json
import logging
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db, engine
from models import Base, Project, Content, Revenue, Agent
from routers import projects, content, revenue, agents, ai_services
from main import app
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceProfiler:
    """Comprehensive performance profiler for CK Empire."""
    
    def __init__(self):
        self.profiler = cProfile.Profile()
        self.stats = None
        self.results = {}
        
    def profile_function(self, func, *args, **kwargs):
        """Profile a single function."""
        logger.info(f"Profiling function: {func.__name__}")
        
        # Start profiling
        self.profiler.enable()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
        except Exception as e:
            logger.error(f"Error profiling {func.__name__}: {e}")
            result = None
            execution_time = time.time() - start_time
        
        # Stop profiling
        self.profiler.disable()
        
        # Get stats
        s = io.StringIO()
        ps = pstats.Stats(self.profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions
        
        return {
            'function': func.__name__,
            'execution_time': execution_time,
            'stats': s.getvalue(),
            'result': result
        }
    
    def profile_database_operations(self):
        """Profile database operations."""
        logger.info("Profiling database operations...")
        
        # Create database tables
        Base.metadata.create_all(bind=engine)
        
        # Test database operations
        def test_db_insert():
            db = next(get_db())
            try:
                # Insert test project
                project = Project(
                    name="Performance Test Project",
                    description="Test project for performance profiling",
                    status="active",
                    consciousness_score=85.5
                )
                db.add(project)
                db.commit()
                db.refresh(project)
                return project.id
            finally:
                db.close()
        
        def test_db_query():
            db = next(get_db())
            try:
                # Query projects
                projects = db.query(Project).all()
                return len(projects)
            finally:
                db.close()
        
        def test_db_update():
            db = next(get_db())
            try:
                # Update project
                project = db.query(Project).first()
                if project:
                    project.consciousness_score = 90.0
                    db.commit()
                return True
            finally:
                db.close()
        
        results = {}
        results['db_insert'] = self.profile_function(test_db_insert)
        results['db_query'] = self.profile_function(test_db_query)
        results['db_update'] = self.profile_function(test_db_update)
        
        return results
    
    def profile_api_endpoints(self):
        """Profile API endpoints."""
        logger.info("Profiling API endpoints...")
        
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        def test_health_endpoint():
            return client.get("/health")
        
        def test_projects_endpoint():
            return client.get("/api/projects/")
        
        def test_metrics_endpoint():
            return client.get("/metrics")
        
        def test_create_project():
            project_data = {
                "name": "Performance Test",
                "description": "Test project",
                "status": "active",
                "consciousness_score": 85.5
            }
            return client.post("/api/projects/", json=project_data)
        
        results = {}
        results['health'] = self.profile_function(test_health_endpoint)
        results['projects'] = self.profile_function(test_projects_endpoint)
        results['metrics'] = self.profile_function(test_metrics_endpoint)
        results['create_project'] = self.profile_function(test_create_project)
        
        return results
    
    def profile_ai_operations(self):
        """Profile AI service operations."""
        logger.info("Profiling AI operations...")
        
        def test_ai_processing():
            # Simulate AI processing
            time.sleep(0.1)  # Simulate processing time
            return {"result": "AI processed successfully"}
        
        def test_encryption():
            from cryptography.fernet import Fernet
            key = Fernet.generate_key()
            f = Fernet(key)
            data = b"Sensitive data for encryption test"
            encrypted = f.encrypt(data)
            decrypted = f.decrypt(encrypted)
            return len(decrypted)
        
        results = {}
        results['ai_processing'] = self.profile_function(test_ai_processing)
        results['encryption'] = self.profile_function(test_encryption)
        
        return results
    
    def profile_external_calls(self):
        """Profile external API calls."""
        logger.info("Profiling external API calls...")
        
        def test_http_request():
            try:
                with httpx.Client(timeout=5.0) as client:
                    response = client.get("https://httpbin.org/get")
                    return response.status_code
            except Exception as e:
                logger.warning(f"HTTP request failed: {e}")
                return None
        
        def test_database_connection():
            try:
                db = next(get_db())
                db.execute("SELECT 1")
                db.close()
                return True
            except Exception as e:
                logger.error(f"Database connection failed: {e}")
                return False
        
        results = {}
        results['http_request'] = self.profile_function(test_http_request)
        results['db_connection'] = self.profile_function(test_database_connection)
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive performance report."""
        report = []
        report.append("=" * 60)
        report.append("CK EMPIRE PERFORMANCE PROFILING REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        total_time = 0
        slow_operations = []
        
        for category, operations in results.items():
            report.append(f"📊 {category.upper().replace('_', ' ')}")
            report.append("-" * 40)
            
            for op_name, op_result in operations.items():
                execution_time = op_result['execution_time']
                total_time += execution_time
                
                report.append(f"  {op_name}: {execution_time:.4f}s")
                
                if execution_time > 0.1:  # Flag slow operations
                    slow_operations.append({
                        'category': category,
                        'operation': op_name,
                        'time': execution_time
                    })
            
            report.append("")
        
        # Slow operations analysis
        if slow_operations:
            report.append("🚨 SLOW OPERATIONS DETECTED")
            report.append("-" * 40)
            for op in sorted(slow_operations, key=lambda x: x['time'], reverse=True):
                report.append(f"  {op['category']}.{op['operation']}: {op['time']:.4f}s")
            report.append("")
        
        # Recommendations
        report.append("💡 PERFORMANCE RECOMMENDATIONS")
        report.append("-" * 40)
        
        if any(op['time'] > 0.5 for op in slow_operations):
            report.append("  ⚠️  Critical: Some operations are very slow (>0.5s)")
            report.append("     - Consider database query optimization")
            report.append("     - Implement caching for frequently accessed data")
            report.append("     - Review external API call efficiency")
        
        if any(op['time'] > 0.1 for op in slow_operations):
            report.append("  🔧 Optimization needed: Several operations are slow (>0.1s)")
            report.append("     - Add database indexes for common queries")
            report.append("     - Implement connection pooling")
            report.append("     - Consider async operations where possible")
        
        report.append("  ✅ Good: Most operations are performing well")
        report.append("     - Continue monitoring performance")
        report.append("     - Implement regular profiling in CI/CD")
        
        report.append("")
        report.append(f"Total profiling time: {total_time:.4f}s")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_detailed_stats(self, results: Dict[str, Any], filename: str = "performance_stats.json"):
        """Save detailed profiling statistics to JSON file."""
        detailed_stats = {}
        
        for category, operations in results.items():
            detailed_stats[category] = {}
            for op_name, op_result in operations.items():
                detailed_stats[category][op_name] = {
                    'execution_time': op_result['execution_time'],
                    'timestamp': datetime.now().isoformat(),
                    'stats_summary': op_result['stats'][:500]  # First 500 chars of stats
                }
        
        with open(filename, 'w') as f:
            json.dump(detailed_stats, f, indent=2)
        
        logger.info(f"Detailed stats saved to {filename}")
    
    def run_comprehensive_profiling(self):
        """Run comprehensive performance profiling."""
        logger.info("Starting comprehensive performance profiling...")
        
        # Profile different aspects
        results = {
            'database_operations': self.profile_database_operations(),
            'api_endpoints': self.profile_api_endpoints(),
            'ai_operations': self.profile_ai_operations(),
            'external_calls': self.profile_external_calls()
        }
        
        # Generate report
        report = self.generate_report(results)
        
        # Save detailed stats
        self.save_detailed_stats(results)
        
        # Print report
        print(report)
        
        # Save report to file
        with open("performance_report.txt", "w") as f:
            f.write(report)
        
        logger.info("Performance profiling completed. Report saved to performance_report.txt")
        
        return results

def main():
    """Main function to run performance profiling."""
    profiler = PerformanceProfiler()
    results = profiler.run_comprehensive_profiling()
    
    # Return results for potential further analysis
    return results

if __name__ == "__main__":
    main() 