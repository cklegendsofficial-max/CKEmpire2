import pytest
import asyncio
import tempfile
import os
import sys
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from fastapi import FastAPI
import httpx
import json
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from database import Base, get_db
from config import get_settings
from models import Project, Content, Revenue, AuditLog, EthicsLog, AILog
from ai import AIProcessor
from ethics import EthicsProcessor
from performance import PerformanceProcessor
from monitoring import get_monitoring

# Test settings
@pytest.fixture(scope="session")
def test_settings():
    """Test settings with overrides"""
    settings = get_settings()
    settings.database_url = "sqlite:///./test.db"
    settings.environment = "test"
    settings.debug = True
    return settings

# Database fixtures
@pytest.fixture(scope="function")
def test_db():
    """Create test database"""
    # Create temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    # Create engine for test database
    engine = create_engine(
        f"sqlite:///{temp_db.name}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield TestingSessionLocal()
    
    # Cleanup
    os.unlink(temp_db.name)

@pytest.fixture(scope="function")
def db_session(test_db):
    """Database session for testing"""
    try:
        yield test_db
    finally:
        test_db.rollback()
        test_db.close()

# FastAPI test client
@pytest.fixture(scope="function")
def client(test_db) -> Generator:
    """FastAPI test client"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# Async HTTP client
@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async HTTP client for testing"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Authentication fixtures
@pytest.fixture
def mock_auth():
    """Mock authentication"""
    with patch('main.get_current_user') as mock:
        mock.return_value = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "role": "admin"
        }
        yield mock

@pytest.fixture
def auth_headers(mock_auth):
    """Authentication headers"""
    return {"Authorization": "Bearer test-token"}

# Sample data fixtures
@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return {
        "name": "Test Project",
        "description": "Test project description",
        "status": "active",
        "budget": 1000.0,
        "revenue": 500.0,
        "metadata": "Test encrypted metadata"
    }

@pytest.fixture
def sample_content_data():
    """Sample content data for testing"""
    return {
        "project_id": 1,
        "title": "Test Content",
        "content_type": "blog",
        "content_data": "This is test content data",
        "metadata": {"tags": ["test", "blog"]},
        "status": "draft",
        "ai_generated": False
    }

@pytest.fixture
def sample_revenue_data():
    """Sample revenue data for testing"""
    return {
        "project_id": 1,
        "amount": 100.0,
        "source": "test_source",
        "description": "Test revenue",
        "metadata": "Test revenue metadata"
    }

@pytest.fixture
def sample_ai_request_data():
    """Sample AI request data for testing"""
    return {
        "prompt": "Write a blog post about AI",
        "model": "gpt-4",
        "max_tokens": 500,
        "temperature": 0.7
    }

@pytest.fixture
def sample_ethics_check_data():
    """Sample ethics check data for testing"""
    return {
        "content": "This is test content for ethics checking",
        "content_type": "blog",
        "project_id": 1
    }

# Mock services
@pytest.fixture
def mock_ai_processor():
    """Mock AI processor"""
    with patch('ai.AIProcessor') as mock:
        processor = Mock()
        processor.generate_content.return_value = {
            "content": "Generated test content",
            "tokens_used": 100,
            "model": "gpt-4"
        }
        processor.analyze_sentiment.return_value = {
            "sentiment": "positive",
            "confidence": 0.85
        }
        mock.return_value = processor
        yield mock

@pytest.fixture
def mock_ethics_processor():
    """Mock ethics processor"""
    with patch('ethics.EthicsProcessor') as mock:
        processor = Mock()
        processor.check_content.return_value = {
            "is_ethical": True,
            "confidence": 0.9,
            "issues": []
        }
        processor.audit_decision.return_value = {
            "decision": "approved",
            "reason": "Content meets ethical guidelines"
        }
        mock.return_value = processor
        yield mock

@pytest.fixture
def mock_performance_processor():
    """Mock performance processor"""
    with patch('performance.PerformanceProcessor') as mock:
        processor = Mock()
        processor.analyze_performance.return_value = {
            "score": 85.5,
            "metrics": {
                "response_time": 0.5,
                "throughput": 100,
                "error_rate": 0.01
            }
        }
        processor.optimize_system.return_value = {
            "optimizations": ["cache_enabled", "compression_enabled"],
            "improvement": 15.2
        }
        mock.return_value = processor
        yield mock

@pytest.fixture
def mock_monitoring():
    """Mock monitoring system"""
    with patch('monitoring.get_monitoring') as mock:
        monitoring = Mock()
        monitoring.record_http_request.return_value = None
        monitoring.record_error.return_value = None
        monitoring.record_ai_request.return_value = None
        monitoring.record_ethics_check.return_value = None
        monitoring.health_check.return_value = {"status": "healthy"}
        monitoring.get_metrics.return_value = "test_metrics"
        mock.return_value = monitoring
        yield mock

# Cloud service mocks
@pytest.fixture
def mock_aws_manager():
    """Mock AWS manager"""
    with patch('cloud.aws_manager.AWSManager') as mock:
        aws = Mock()
        aws.upload_file.return_value = "s3://bucket/test-file.txt"
        aws.download_file.return_value = "/tmp/test-file.txt"
        aws.create_backup.return_value = {"backup_id": "backup-123", "status": "completed"}
        mock.return_value = aws
        yield mock

@pytest.fixture
def mock_google_cloud_manager():
    """Mock Google Cloud manager"""
    with patch('cloud.google_cloud_manager.GoogleCloudManager') as mock:
        gcp = Mock()
        gcp.upload_file.return_value = "gs://bucket/test-file.txt"
        gcp.download_file.return_value = "/tmp/test-file.txt"
        gcp.create_backup.return_value = {"backup_id": "backup-456", "status": "completed"}
        mock.return_value = gcp
        yield mock

# Test utilities
@pytest.fixture
def create_test_project(db_session, sample_project_data):
    """Utility to create a test project"""
    def _create_project(**kwargs):
        data = {**sample_project_data, **kwargs}
        project = Project(**data)
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        return project
    return _create_project

@pytest.fixture
def create_test_content(db_session, sample_content_data):
    """Utility to create test content"""
    def _create_content(**kwargs):
        data = {**sample_content_data, **kwargs}
        content = Content(**data)
        db_session.add(content)
        db_session.commit()
        db_session.refresh(content)
        return content
    return _create_content

@pytest.fixture
def create_test_revenue(db_session, sample_revenue_data):
    """Utility to create test revenue"""
    def _create_revenue(**kwargs):
        data = {**sample_revenue_data, **kwargs}
        revenue = Revenue(**data)
        db_session.add(revenue)
        db_session.commit()
        db_session.refresh(revenue)
        return revenue
    return _create_revenue

# Performance testing fixtures
@pytest.fixture
def benchmark_config():
    """Benchmark configuration"""
    return {
        "min_rounds": 10,
        "max_time": 10.0,
        "warmup": True,
        "disable_gc": True
    }

# Load testing fixtures
@pytest.fixture
def locust_config():
    """Locust configuration for load testing"""
    return {
        "host": "http://localhost:8000",
        "users": 10,
        "spawn_rate": 2,
        "run_time": "60s"
    }

# Security testing fixtures
@pytest.fixture
def security_scan_config():
    """Security scan configuration"""
    return {
        "bandit_config": "bandit.yaml",
        "safety_config": "safety.yaml",
        "semgrep_config": "semgrep.yaml"
    }

# E2E testing fixtures
@pytest.fixture
def browser_config():
    """Browser configuration for E2E tests"""
    return {
        "headless": True,
        "slow_mo": 100,
        "timeout": 30000,
        "viewport": {"width": 1920, "height": 1080}
    }

# Event loop for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_test_data(db_session):
    """Clean up test data after each test"""
    yield
    # Clean up all test data
    db_session.query(AILog).delete()
    db_session.query(EthicsLog).delete()
    db_session.query(AuditLog).delete()
    db_session.query(Revenue).delete()
    db_session.query(Content).delete()
    db_session.query(Project).delete()
    db_session.commit() 