import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database import Base, get_db
from backend.models import ProjectCreate

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

class TestProjects:
    """Test class for projects endpoints"""
    
    def test_create_project(self):
        """Test creating a new project"""
        project_data = {
            "name": "Test Project",
            "description": "A test project for testing",
            "status": "active",
            "budget": 10000.0,
            "revenue": 5000.0
        }
        
        response = client.post("/api/v1/projects", json=project_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == project_data["name"]
        assert data["description"] == project_data["description"]
        assert data["status"] == project_data["status"]
        assert data["budget"] == project_data["budget"]
        assert data["revenue"] == project_data["revenue"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_get_projects(self):
        """Test getting all projects"""
        response = client.get("/api/v1/projects")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "projects" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert isinstance(data["projects"], list)
    
    def test_get_project_by_id(self):
        """Test getting a specific project by ID"""
        # First create a project
        project_data = {
            "name": "Test Project for Get",
            "description": "Test project for get by ID",
            "status": "active",
            "budget": 5000.0,
            "revenue": 2500.0
        }
        
        create_response = client.post("/api/v1/projects", json=project_data)
        project_id = create_response.json()["id"]
        
        # Get the project by ID
        response = client.get(f"/api/v1/projects/{project_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == project_id
        assert data["name"] == project_data["name"]
    
    def test_get_nonexistent_project(self):
        """Test getting a project that doesn't exist"""
        response = client.get("/api/v1/projects/99999")
        
        assert response.status_code == 404
        assert "Project not found" in response.json()["detail"]
    
    def test_update_project(self):
        """Test updating a project"""
        # First create a project
        project_data = {
            "name": "Test Project for Update",
            "description": "Test project for update",
            "status": "active",
            "budget": 3000.0,
            "revenue": 1500.0
        }
        
        create_response = client.post("/api/v1/projects", json=project_data)
        project_id = create_response.json()["id"]
        
        # Update the project
        update_data = {
            "name": "Updated Test Project",
            "budget": 4000.0
        }
        
        response = client.put(f"/api/v1/projects/{project_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == update_data["name"]
        assert data["budget"] == update_data["budget"]
        assert data["description"] == project_data["description"]  # Should remain unchanged
    
    def test_delete_project(self):
        """Test deleting a project"""
        # First create a project
        project_data = {
            "name": "Test Project for Delete",
            "description": "Test project for delete",
            "status": "active",
            "budget": 2000.0,
            "revenue": 1000.0
        }
        
        create_response = client.post("/api/v1/projects", json=project_data)
        project_id = create_response.json()["id"]
        
        # Delete the project
        response = client.delete(f"/api/v1/projects/{project_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "Project" in data["message"]
        assert "deleted successfully" in data["message"]
        
        # Verify project is deleted
        get_response = client.get(f"/api/v1/projects/{project_id}")
        assert get_response.status_code == 404
    
    def test_project_stats(self):
        """Test getting project statistics"""
        # First create a project
        project_data = {
            "name": "Test Project for Stats",
            "description": "Test project for statistics",
            "status": "active",
            "budget": 10000.0,
            "revenue": 6000.0
        }
        
        create_response = client.post("/api/v1/projects", json=project_data)
        project_id = create_response.json()["id"]
        
        # Get project stats
        response = client.get(f"/api/v1/projects/{project_id}/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["project_id"] == project_id
        assert data["project_name"] == project_data["name"]
        assert data["total_revenue"] == project_data["revenue"]
        assert data["budget"] == project_data["budget"]
        assert "budget_utilization" in data
        assert "profit_margin" in data
    
    def test_invalid_project_data(self):
        """Test creating project with invalid data"""
        # Test with missing required field
        invalid_data = {
            "description": "Project without name",
            "status": "active",
            "budget": 1000.0
        }
        
        response = client.post("/api/v1/projects", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert "docs" in data
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data

if __name__ == "__main__":
    pytest.main([__file__]) 