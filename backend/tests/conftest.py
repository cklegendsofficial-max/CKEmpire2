"""
Common test configuration and fixtures for CK Empire Builder
"""

import pytest
import asyncio
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from config import settings, constants
from database import Base, get_db
from main import app
from utils import generate_secure_password, hash_password

# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    # Clean up
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session(test_db):
    """Create database session for tests"""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session) -> Generator[TestClient, None, None]:
    """Create test client"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Test user data"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }

@pytest.fixture
def test_project_data() -> Dict[str, Any]:
    """Test project data"""
    return {
        "name": "Test Project",
        "description": "A test project",
        "status": constants.PROJECT_STATUS_ACTIVE,
        "budget": 1000.0,
        "revenue": 500.0
    }

@pytest.fixture
def test_content_data() -> Dict[str, Any]:
    """Test content data"""
    return {
        "project_id": 1,
        "title": "Test Content",
        "content_type": constants.CONTENT_TYPE_ARTICLE,
        "content_data": "This is test content",
        "status": "draft"
    }

@pytest.fixture
def test_revenue_data() -> Dict[str, Any]:
    """Test revenue data"""
    return {
        "project_id": 1,
        "amount": 100.0,
        "source": constants.REVENUE_SOURCE_ADS,
        "description": "Test revenue"
    }

@pytest.fixture
def auth_headers(client, test_user_data) -> Dict[str, str]:
    """Get authentication headers"""
    # Create user
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    
    # Login
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    token = token_data["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(client) -> Dict[str, str]:
    """Get admin authentication headers"""
    admin_data = {
        "username": "admin",
        "email": "admin@example.com",
        "password": "AdminPassword123!",
        "full_name": "Admin User"
    }
    
    # Create admin user
    response = client.post("/api/v1/auth/register", json=admin_data)
    assert response.status_code == 201
    
    # Login
    login_data = {
        "username": admin_data["username"],
        "password": admin_data["password"]
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    token = token_data["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_settings():
    """Test settings"""
    return {
        "DATABASE_URL": TEST_DATABASE_URL,
        "DEBUG": True,
        "ENVIRONMENT": "testing",
        "SECRET_KEY": "test-secret-key",
        "OPENAI_API_KEY": "test-openai-key",
        "STRIPE_SECRET_KEY": "test-stripe-key"
    }

@pytest.fixture
def mock_ai_response():
    """Mock AI response"""
    return {
        "strategy_type": "lean_startup",
        "title": "Test Strategy",
        "description": "A test strategy",
        "key_actions": ["Action 1", "Action 2"],
        "timeline_months": 6,
        "estimated_investment": 5000.0,
        "projected_roi": 0.25,
        "risk_level": "medium",
        "success_metrics": ["Metric 1", "Metric 2"]
    }

@pytest.fixture
def mock_ethics_report():
    """Mock ethics report"""
    return {
        "bias_detected": False,
        "bias_score": 0.1,
        "fairness_score": 0.9,
        "flagged_keywords": [],
        "status": constants.ETHICS_STATUS_APPROVED,
        "recommendations": [],
        "confidence_score": 0.95
    }

@pytest.fixture
def mock_metrics():
    """Mock metrics data"""
    return {
        "consciousness_score": 0.45,
        "total_revenue": 48000,
        "active_agents": 18,
        "total_projects": 12,
        "total_content": 156,
        "cloud_provider": "aws",
        "cloud_enabled": True
    }

# Test utilities
def create_test_user(db_session, user_data: Dict[str, Any]):
    """Create a test user"""
    from database import User
    
    hashed_password = hash_password(user_data["password"])
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        full_name=user_data.get("full_name"),
        hashed_password=hashed_password,
        is_active=True
    )
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def create_test_project(db_session, project_data: Dict[str, Any]):
    """Create a test project"""
    from database import Project
    
    project = Project(**project_data)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project

def create_test_content(db_session, content_data: Dict[str, Any]):
    """Create test content"""
    from database import Content
    
    content = Content(**content_data)
    db_session.add(content)
    db_session.commit()
    db_session.refresh(content)
    return content

def create_test_revenue(db_session, revenue_data: Dict[str, Any]):
    """Create test revenue"""
    from database import Revenue
    
    revenue = Revenue(**revenue_data)
    db_session.add(revenue)
    db_session.commit()
    db_session.refresh(revenue)
    return revenue

def assert_response_structure(response_data: Dict[str, Any]):
    """Assert response has correct structure"""
    assert "success" in response_data
    assert "message" in response_data
    assert "timestamp" in response_data

def assert_pagination_structure(pagination_data: Dict[str, Any]):
    """Assert pagination has correct structure"""
    required_fields = ["total", "page", "page_size", "pages", "has_next", "has_prev"]
    for field in required_fields:
        assert field in pagination_data

def assert_error_response(response_data: Dict[str, Any]):
    """Assert error response structure"""
    assert response_data["success"] is False
    assert "error" in response_data
    assert "code" in response_data["error"]
    assert "message" in response_data["error"]

def assert_success_response(response_data: Dict[str, Any]):
    """Assert success response structure"""
    assert response_data["success"] is True
    assert "data" in response_data

# Test decorators
def skip_if_no_openai():
    """Skip test if OpenAI is not configured"""
    return pytest.mark.skipif(
        not settings.OPENAI_API_KEY,
        reason="OpenAI API key not configured"
    )

def skip_if_no_stripe():
    """Skip test if Stripe is not configured"""
    return pytest.mark.skipif(
        not settings.STRIPE_SECRET_KEY,
        reason="Stripe secret key not configured"
    )

def skip_if_no_cloud():
    """Skip test if cloud is not configured"""
    return pytest.mark.skipif(
        settings.CLOUD_PROVIDER == "none",
        reason="Cloud provider not configured"
    )

# Test markers
pytest_plugins = [
    "pytest_asyncio"
]

# Configure pytest
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    ) 