import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import tempfile
from datetime import datetime

from backend.database import (
    Base, Project, Content, Revenue, AuditLog, EthicsLog, AILog,
    get_db, init_db, create_project, create_content, create_revenue,
    get_project_by_id, get_content_by_id, get_revenue_by_id,
    get_audit_logs, encrypt_value, decrypt_value, get_audit_logs_by_record
)

# Test database setup
@pytest.fixture
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

class TestDatabaseModels:
    """Test database models"""
    
    def test_project_creation(self, test_db, sample_project_data):
        """Test project creation"""
        project = Project(**sample_project_data)
        test_db.add(project)
        test_db.commit()
        test_db.refresh(project)
        
        assert project.id is not None
        assert project.name == sample_project_data["name"]
        assert project.status == sample_project_data["status"]
        assert project.created_at is not None
        assert project.updated_at is not None
    
    def test_content_creation(self, test_db, sample_content_data):
        """Test content creation"""
        # First create a project
        project = Project(name="Test Project", status="active")
        test_db.add(project)
        test_db.commit()
        
        # Create content
        content_data = sample_content_data.copy()
        content_data["project_id"] = project.id
        content = Content(**content_data)
        test_db.add(content)
        test_db.commit()
        test_db.refresh(content)
        
        assert content.id is not None
        assert content.title == sample_content_data["title"]
        assert content.content_type == sample_content_data["content_type"]
        assert content.project_id == project.id
    
    def test_revenue_creation(self, test_db, sample_revenue_data):
        """Test revenue creation"""
        # First create a project
        project = Project(name="Test Project", status="active")
        test_db.add(project)
        test_db.commit()
        
        # Create revenue
        revenue_data = sample_revenue_data.copy()
        revenue_data["project_id"] = project.id
        revenue = Revenue(**revenue_data)
        test_db.add(revenue)
        test_db.commit()
        test_db.refresh(revenue)
        
        assert revenue.id is not None
        assert revenue.amount == sample_revenue_data["amount"]
        assert revenue.source == sample_revenue_data["source"]
        assert revenue.project_id == project.id

class TestEncryption:
    """Test encryption functionality"""
    
    def test_encrypt_decrypt_value(self):
        """Test encryption and decryption of values"""
        test_value = "sensitive data"
        
        # Encrypt
        encrypted = encrypt_value(test_value)
        assert encrypted != test_value
        assert encrypted is not None
        
        # Decrypt
        decrypted = decrypt_value(encrypted)
        assert decrypted == test_value
    
    def test_encrypt_empty_value(self):
        """Test encryption of empty value"""
        empty_value = ""
        encrypted = encrypt_value(empty_value)
        assert encrypted == empty_value
    
    def test_encrypt_none_value(self):
        """Test encryption of None value"""
        encrypted = encrypt_value(None)
        assert encrypted is None

class TestAuditLogging:
    """Test audit logging functionality"""
    
    def test_audit_log_creation(self, test_db, sample_project_data):
        """Test audit log creation"""
        # Create project (should trigger audit log)
        project = Project(**sample_project_data)
        test_db.add(project)
        test_db.commit()
        
        # Check audit logs
        audit_logs = get_audit_logs(test_db, table_name="projects")
        assert len(audit_logs) > 0
        
        # Check latest audit log
        latest_log = audit_logs[0]
        assert latest_log.table_name == "projects"
        assert latest_log.operation == "INSERT"
        assert latest_log.record_id == project.id
    
    def test_audit_log_filtering(self, test_db):
        """Test audit log filtering"""
        # Create multiple projects
        for i in range(3):
            project = Project(name=f"Project {i}", status="active")
            test_db.add(project)
        test_db.commit()
        
        # Test filtering by table
        project_logs = get_audit_logs(test_db, table_name="projects")
        assert len(project_logs) >= 3
        
        # Test filtering by record
        record_logs = get_audit_logs_by_record(test_db, "projects", 1)
        assert len(record_logs) >= 1

class TestDatabaseUtilities:
    """Test database utility functions"""
    
    def test_create_project(self, test_db, sample_project_data):
        """Test create_project utility"""
        project = create_project(test_db, sample_project_data)
        
        assert project.id is not None
        assert project.name == sample_project_data["name"]
        assert project.status == sample_project_data["status"]
    
    def test_get_project_by_id(self, test_db, sample_project_data):
        """Test get_project_by_id utility"""
        # Create project
        project = create_project(test_db, sample_project_data)
        
        # Retrieve project
        retrieved_project = get_project_by_id(test_db, project.id)
        
        assert retrieved_project is not None
        assert retrieved_project.id == project.id
        assert retrieved_project.name == project.name
    
    def test_create_content(self, test_db, sample_content_data):
        """Test create_content utility"""
        # First create a project
        project = create_project(test_db, {"name": "Test Project", "status": "active"})
        
        # Create content
        content_data = sample_content_data.copy()
        content_data["project_id"] = project.id
        content = create_content(test_db, content_data)
        
        assert content.id is not None
        assert content.title == sample_content_data["title"]
        assert content.project_id == project.id
    
    def test_create_revenue(self, test_db, sample_revenue_data):
        """Test create_revenue utility"""
        # First create a project
        project = create_project(test_db, {"name": "Test Project", "status": "active"})
        
        # Create revenue
        revenue_data = sample_revenue_data.copy()
        revenue_data["project_id"] = project.id
        revenue = create_revenue(test_db, revenue_data)
        
        assert revenue.id is not None
        assert revenue.amount == sample_revenue_data["amount"]
        assert revenue.project_id == project.id

class TestDatabaseInitialization:
    """Test database initialization"""
    
    def test_init_db(self, test_db):
        """Test database initialization"""
        # This should not raise any exceptions
        # Note: We can't easily test the async init_db function here
        # but we can test that the database is working
        result = test_db.execute("SELECT 1").scalar()
        assert result == 1

class TestModelRelationships:
    """Test model relationships"""
    
    def test_project_content_relationship(self, test_db):
        """Test project-content relationship"""
        # Create project
        project = Project(name="Test Project", status="active")
        test_db.add(project)
        test_db.commit()
        
        # Create content for project
        content = Content(
            project_id=project.id,
            title="Test Content",
            content_type="blog",
            content_data="Test content data"
        )
        test_db.add(content)
        test_db.commit()
        
        # Verify relationship
        assert content.project_id == project.id
        
        # Query content by project
        project_content = test_db.query(Content).filter(Content.project_id == project.id).all()
        assert len(project_content) == 1
        assert project_content[0].id == content.id
    
    def test_project_revenue_relationship(self, test_db):
        """Test project-revenue relationship"""
        # Create project
        project = Project(name="Test Project", status="active")
        test_db.add(project)
        test_db.commit()
        
        # Create revenue for project
        revenue = Revenue(
            project_id=project.id,
            amount=100.0,
            source="test_source"
        )
        test_db.add(revenue)
        test_db.commit()
        
        # Verify relationship
        assert revenue.project_id == project.id
        
        # Query revenue by project
        project_revenue = test_db.query(Revenue).filter(Revenue.project_id == project.id).all()
        assert len(project_revenue) == 1
        assert project_revenue[0].id == revenue.id

class TestDataValidation:
    """Test data validation"""
    
    def test_project_required_fields(self, test_db):
        """Test project required fields"""
        # Try to create project without required fields
        with pytest.raises(Exception):
            project = Project()  # Missing required fields
            test_db.add(project)
            test_db.commit()
    
    def test_content_required_fields(self, test_db):
        """Test content required fields"""
        # Try to create content without required fields
        with pytest.raises(Exception):
            content = Content()  # Missing required fields
            test_db.add(content)
            test_db.commit()
    
    def test_revenue_required_fields(self, test_db):
        """Test revenue required fields"""
        # Try to create revenue without required fields
        with pytest.raises(Exception):
            revenue = Revenue()  # Missing required fields
            test_db.add(revenue)
            test_db.commit()

if __name__ == "__main__":
    pytest.main([__file__]) 