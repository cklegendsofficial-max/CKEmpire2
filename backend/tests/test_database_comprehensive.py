import pytest
import tempfile
import os
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm import joinedload

from database import (
    Base, Project, Content, Revenue, AuditLog, EthicsLog, AILog,
    get_db, init_db, create_project, create_content, create_revenue,
    get_project_by_id, get_content_by_id, get_revenue_by_id,
    get_audit_logs, encrypt_value, decrypt_value, get_audit_logs_by_record,
    update_project, delete_project, get_projects_by_status,
    get_content_by_project, get_revenue_by_project, get_audit_logs_by_user,
    get_ethics_logs_by_project, get_ai_logs_by_project
)

@pytest.mark.database
@pytest.mark.unit
class TestDatabaseModels:
    """Comprehensive database model tests"""
    
    def test_project_creation_with_all_fields(self, db_session, sample_project_data):
        """Test project creation with all fields"""
        project = Project(**sample_project_data)
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        
        assert project.id is not None
        assert project.name == sample_project_data["name"]
        assert project.description == sample_project_data["description"]
        assert project.status == sample_project_data["status"]
        assert project.budget == sample_project_data["budget"]
        assert project.revenue == sample_project_data["revenue"]
        assert project.created_at is not None
        assert project.updated_at is not None
    
    def test_project_creation_minimal_fields(self, db_session):
        """Test project creation with minimal required fields"""
        project = Project(name="Minimal Project", status="active")
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        
        assert project.id is not None
        assert project.name == "Minimal Project"
        assert project.status == "active"
        assert project.description is None
        assert project.budget == 0.0
        assert project.revenue == 0.0
    
    def test_project_status_validation(self, db_session):
        """Test project status validation"""
        valid_statuses = ["active", "inactive", "completed", "cancelled"]
        
        for status in valid_statuses:
            project = Project(name=f"Test Project {status}", status=status)
            db_session.add(project)
            db_session.commit()
            db_session.refresh(project)
            assert project.status == status
    
    def test_project_budget_revenue_types(self, db_session):
        """Test project budget and revenue with different numeric types"""
        project = Project(
            name="Numeric Test Project",
            status="active",
            budget=Decimal("1000.50"),
            revenue=Decimal("500.25")
        )
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        
        assert float(project.budget) == 1000.50
        assert float(project.revenue) == 500.25
    
    def test_content_creation_with_metadata(self, db_session, sample_content_data):
        """Test content creation with metadata"""
        # First create a project
        project = Project(name="Test Project", status="active")
        db_session.add(project)
        db_session.commit()
        
        content = Content(**sample_content_data)
        db_session.add(content)
        db_session.commit()
        db_session.refresh(content)
        
        assert content.id is not None
        assert content.title == sample_content_data["title"]
        assert content.content_type == sample_content_data["content_type"]
        assert content.content_data == sample_content_data["content_data"]
        assert content.metadata == sample_content_data["metadata"]
        assert content.status == sample_content_data["status"]
        assert content.ai_generated == sample_content_data["ai_generated"]
    
    def test_content_types_validation(self, db_session):
        """Test content type validation"""
        project = Project(name="Test Project", status="active")
        db_session.add(project)
        db_session.commit()
        
        valid_types = ["blog", "article", "video", "image", "document"]
        
        for content_type in valid_types:
            content = Content(
                project_id=project.id,
                title=f"Test {content_type}",
                content_type=content_type,
                content_data=f"Test {content_type} content"
            )
            db_session.add(content)
            db_session.commit()
            db_session.refresh(content)
            assert content.content_type == content_type
    
    def test_revenue_creation_with_source(self, db_session, sample_revenue_data):
        """Test revenue creation with source tracking"""
        # First create a project
        project = Project(name="Test Project", status="active")
        db_session.add(project)
        db_session.commit()
        
        revenue = Revenue(**sample_revenue_data)
        db_session.add(revenue)
        db_session.commit()
        db_session.refresh(revenue)
        
        assert revenue.id is not None
        assert revenue.project_id == sample_revenue_data["project_id"]
        assert revenue.amount == sample_revenue_data["amount"]
        assert revenue.source == sample_revenue_data["source"]
        assert revenue.description == sample_revenue_data["description"]
    
    def test_audit_log_creation(self, db_session):
        """Test audit log creation"""
        audit_log = AuditLog(
            user_id=1,
            action="CREATE",
            table_name="projects",
            record_id=1,
            old_values={"name": "Old Name"},
            new_values={"name": "New Name"},
            ip_address="192.168.1.1"
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)
        
        assert audit_log.id is not None
        assert audit_log.user_id == 1
        assert audit_log.action == "CREATE"
        assert audit_log.table_name == "projects"
        assert audit_log.record_id == 1
        assert audit_log.old_values == {"name": "Old Name"}
        assert audit_log.new_values == {"name": "New Name"}
        assert audit_log.ip_address == "192.168.1.1"
    
    def test_ethics_log_creation(self, db_session):
        """Test ethics log creation"""
        ethics_log = EthicsLog(
            project_id=1,
            content_id=1,
            check_type="content_review",
            result="approved",
            confidence=0.95,
            issues=[],
            metadata={"model": "gpt-4", "version": "1.0"}
        )
        db_session.add(ethics_log)
        db_session.commit()
        db_session.refresh(ethics_log)
        
        assert ethics_log.id is not None
        assert ethics_log.project_id == 1
        assert ethics_log.content_id == 1
        assert ethics_log.check_type == "content_review"
        assert ethics_log.result == "approved"
        assert ethics_log.confidence == 0.95
        assert ethics_log.issues == []
    
    def test_ai_log_creation(self, db_session):
        """Test AI log creation"""
        ai_log = AILog(
            project_id=1,
            content_id=1,
            model="gpt-4",
            prompt="Test prompt",
            response="Test response",
            tokens_used=100,
            cost=0.05,
            metadata={"temperature": 0.7, "max_tokens": 500}
        )
        db_session.add(ai_log)
        db_session.commit()
        db_session.refresh(ai_log)
        
        assert ai_log.id is not None
        assert ai_log.project_id == 1
        assert ai_log.content_id == 1
        assert ai_log.model == "gpt-4"
        assert ai_log.prompt == "Test prompt"
        assert ai_log.response == "Test response"
        assert ai_log.tokens_used == 100
        assert ai_log.cost == 0.05

@pytest.mark.database
@pytest.mark.unit
class TestEncryption:
    """Test encryption and decryption functionality"""
    
    def test_encrypt_decrypt_string(self):
        """Test encrypting and decrypting a string"""
        original_value = "sensitive data"
        encrypted = encrypt_value(original_value)
        decrypted = decrypt_value(encrypted)
        
        assert encrypted != original_value
        assert decrypted == original_value
    
    def test_encrypt_decrypt_json(self):
        """Test encrypting and decrypting JSON data"""
        original_value = '{"key": "value", "number": 123}'
        encrypted = encrypt_value(original_value)
        decrypted = decrypt_value(encrypted)
        
        assert encrypted != original_value
        assert decrypted == original_value
    
    def test_encrypt_empty_string(self):
        """Test encrypting empty string"""
        encrypted = encrypt_value("")
        decrypted = decrypt_value(encrypted)
        
        assert decrypted == ""
    
    def test_encrypt_none_value(self):
        """Test encrypting None value"""
        encrypted = encrypt_value(None)
        decrypted = decrypt_value(encrypted)
        
        assert decrypted is None
    
    def test_encrypt_special_characters(self):
        """Test encrypting special characters"""
        original_value = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        encrypted = encrypt_value(original_value)
        decrypted = decrypt_value(encrypted)
        
        assert encrypted != original_value
        assert decrypted == original_value
    
    def test_encrypt_large_data(self):
        """Test encrypting large data"""
        original_value = "x" * 1000
        encrypted = encrypt_value(original_value)
        decrypted = decrypt_value(encrypted)
        
        assert encrypted != original_value
        assert decrypted == original_value

@pytest.mark.database
@pytest.mark.integration
class TestDatabaseOperations:
    """Test database CRUD operations"""
    
    def test_create_project_utility(self, db_session, sample_project_data):
        """Test create_project utility function"""
        project = create_project(db_session, **sample_project_data)
        
        assert project.id is not None
        assert project.name == sample_project_data["name"]
        assert project.status == sample_project_data["status"]
    
    def test_get_project_by_id(self, db_session, sample_project_data):
        """Test get_project_by_id function"""
        project = create_project(db_session, **sample_project_data)
        retrieved_project = get_project_by_id(db_session, project.id)
        
        assert retrieved_project is not None
        assert retrieved_project.id == project.id
        assert retrieved_project.name == project.name
    
    def test_update_project(self, db_session, sample_project_data):
        """Test project update functionality"""
        project = create_project(db_session, **sample_project_data)
        
        # Update project
        update_data = {"name": "Updated Project", "status": "completed"}
        updated_project = update_project(db_session, project.id, **update_data)
        
        assert updated_project.name == "Updated Project"
        assert updated_project.status == "completed"
    
    def test_delete_project(self, db_session, sample_project_data):
        """Test project deletion"""
        project = create_project(db_session, **sample_project_data)
        project_id = project.id
        
        # Delete project
        delete_project(db_session, project_id)
        
        # Verify deletion
        retrieved_project = get_project_by_id(db_session, project_id)
        assert retrieved_project is None
    
    def test_get_projects_by_status(self, db_session):
        """Test getting projects by status"""
        # Create projects with different statuses
        active_project = create_project(db_session, name="Active Project", status="active")
        inactive_project = create_project(db_session, name="Inactive Project", status="inactive")
        completed_project = create_project(db_session, name="Completed Project", status="completed")
        
        # Get active projects
        active_projects = get_projects_by_status(db_session, "active")
        assert len(active_projects) == 1
        assert active_projects[0].id == active_project.id
    
    def test_create_content_with_project_relationship(self, db_session, sample_content_data):
        """Test content creation with project relationship"""
        # Create project first
        project = create_project(db_session, name="Test Project", status="active")
        
        # Create content
        content_data = {**sample_content_data, "project_id": project.id}
        content = create_content(db_session, **content_data)
        
        assert content.id is not None
        assert content.project_id == project.id
        
        # Test relationship
        project_with_content = db_session.query(Project).options(joinedload(Project.content)).filter(Project.id == project.id).first()
        assert len(project_with_content.content) == 1
        assert project_with_content.content[0].id == content.id
    
    def test_get_content_by_project(self, db_session, sample_content_data):
        """Test getting content by project"""
        # Create project and content
        project = create_project(db_session, name="Test Project", status="active")
        content_data = {**sample_content_data, "project_id": project.id}
        content = create_content(db_session, **content_data)
        
        # Get content by project
        project_content = get_content_by_project(db_session, project.id)
        assert len(project_content) == 1
        assert project_content[0].id == content.id
    
    def test_create_revenue_with_project_relationship(self, db_session, sample_revenue_data):
        """Test revenue creation with project relationship"""
        # Create project first
        project = create_project(db_session, name="Test Project", status="active")
        
        # Create revenue
        revenue_data = {**sample_revenue_data, "project_id": project.id}
        revenue = create_revenue(db_session, **revenue_data)
        
        assert revenue.id is not None
        assert revenue.project_id == project.id
        
        # Test relationship
        project_with_revenue = db_session.query(Project).options(joinedload(Project.revenue)).filter(Project.id == project.id).first()
        assert len(project_with_revenue.revenue) == 1
        assert project_with_revenue.revenue[0].id == revenue.id
    
    def test_get_revenue_by_project(self, db_session, sample_revenue_data):
        """Test getting revenue by project"""
        # Create project and revenue
        project = create_project(db_session, name="Test Project", status="active")
        revenue_data = {**sample_revenue_data, "project_id": project.id}
        revenue = create_revenue(db_session, **revenue_data)
        
        # Get revenue by project
        project_revenue = get_revenue_by_project(db_session, project.id)
        assert len(project_revenue) == 1
        assert project_revenue[0].id == revenue.id

@pytest.mark.database
@pytest.mark.integration
class TestAuditLogging:
    """Test audit logging functionality"""
    
    def test_audit_log_creation_for_project(self, db_session):
        """Test audit log creation for project operations"""
        # Create project
        project = create_project(db_session, name="Test Project", status="active")
        
        # Create audit log
        audit_log = AuditLog(
            user_id=1,
            action="CREATE",
            table_name="projects",
            record_id=project.id,
            new_values={"name": "Test Project", "status": "active"},
            ip_address="192.168.1.1"
        )
        db_session.add(audit_log)
        db_session.commit()
        
        assert audit_log.id is not None
        assert audit_log.record_id == project.id
    
    def test_get_audit_logs_by_record(self, db_session):
        """Test getting audit logs by record"""
        # Create project
        project = create_project(db_session, name="Test Project", status="active")
        
        # Create multiple audit logs
        audit_log1 = AuditLog(
            user_id=1, action="CREATE", table_name="projects", record_id=project.id,
            new_values={"name": "Test Project"}, ip_address="192.168.1.1"
        )
        audit_log2 = AuditLog(
            user_id=1, action="UPDATE", table_name="projects", record_id=project.id,
            old_values={"status": "active"}, new_values={"status": "completed"},
            ip_address="192.168.1.1"
        )
        db_session.add_all([audit_log1, audit_log2])
        db_session.commit()
        
        # Get audit logs by record
        logs = get_audit_logs_by_record(db_session, "projects", project.id)
        assert len(logs) == 2
    
    def test_get_audit_logs_by_user(self, db_session):
        """Test getting audit logs by user"""
        # Create audit logs for different users
        audit_log1 = AuditLog(
            user_id=1, action="CREATE", table_name="projects", record_id=1,
            new_values={"name": "Project 1"}, ip_address="192.168.1.1"
        )
        audit_log2 = AuditLog(
            user_id=2, action="CREATE", table_name="projects", record_id=2,
            new_values={"name": "Project 2"}, ip_address="192.168.1.2"
        )
        db_session.add_all([audit_log1, audit_log2])
        db_session.commit()
        
        # Get audit logs by user
        user_logs = get_audit_logs_by_user(db_session, 1)
        assert len(user_logs) == 1
        assert user_logs[0].user_id == 1

@pytest.mark.database
@pytest.mark.integration
class TestEthicsAndAILogging:
    """Test ethics and AI logging functionality"""
    
    def test_ethics_log_creation_for_content(self, db_session):
        """Test ethics log creation for content review"""
        # Create project and content
        project = create_project(db_session, name="Test Project", status="active")
        content = create_content(db_session, project_id=project.id, title="Test Content", content_type="blog", content_data="Test content")
        
        # Create ethics log
        ethics_log = EthicsLog(
            project_id=project.id,
            content_id=content.id,
            check_type="content_review",
            result="approved",
            confidence=0.95,
            issues=[],
            metadata={"model": "gpt-4"}
        )
        db_session.add(ethics_log)
        db_session.commit()
        
        assert ethics_log.id is not None
        assert ethics_log.project_id == project.id
        assert ethics_log.content_id == content.id
    
    def test_get_ethics_logs_by_project(self, db_session):
        """Test getting ethics logs by project"""
        # Create project and ethics logs
        project = create_project(db_session, name="Test Project", status="active")
        
        ethics_log1 = EthicsLog(
            project_id=project.id, content_id=1, check_type="content_review",
            result="approved", confidence=0.95, issues=[]
        )
        ethics_log2 = EthicsLog(
            project_id=project.id, content_id=2, check_type="sentiment_analysis",
            result="approved", confidence=0.88, issues=[]
        )
        db_session.add_all([ethics_log1, ethics_log2])
        db_session.commit()
        
        # Get ethics logs by project
        logs = get_ethics_logs_by_project(db_session, project.id)
        assert len(logs) == 2
    
    def test_ai_log_creation_for_content_generation(self, db_session):
        """Test AI log creation for content generation"""
        # Create project and content
        project = create_project(db_session, name="Test Project", status="active")
        content = create_content(db_session, project_id=project.id, title="Test Content", content_type="blog", content_data="Test content")
        
        # Create AI log
        ai_log = AILog(
            project_id=project.id,
            content_id=content.id,
            model="gpt-4",
            prompt="Write a blog post about AI",
            response="Generated blog post content...",
            tokens_used=150,
            cost=0.075,
            metadata={"temperature": 0.7, "max_tokens": 500}
        )
        db_session.add(ai_log)
        db_session.commit()
        
        assert ai_log.id is not None
        assert ai_log.project_id == project.id
        assert ai_log.content_id == content.id
        assert ai_log.model == "gpt-4"
    
    def test_get_ai_logs_by_project(self, db_session):
        """Test getting AI logs by project"""
        # Create project and AI logs
        project = create_project(db_session, name="Test Project", status="active")
        
        ai_log1 = AILog(
            project_id=project.id, content_id=1, model="gpt-4",
            prompt="Write blog post", response="Generated content", tokens_used=100, cost=0.05
        )
        ai_log2 = AILog(
            project_id=project.id, content_id=2, model="gpt-3.5-turbo",
            prompt="Analyze sentiment", response="Positive", tokens_used=50, cost=0.025
        )
        db_session.add_all([ai_log1, ai_log2])
        db_session.commit()
        
        # Get AI logs by project
        logs = get_ai_logs_by_project(db_session, project.id)
        assert len(logs) == 2

@pytest.mark.database
@pytest.mark.unit
class TestDataValidation:
    """Test data validation and constraints"""
    
    def test_project_required_fields(self, db_session):
        """Test project required fields validation"""
        # Test missing required fields
        with pytest.raises(IntegrityError):
            project = Project()  # Missing name and status
            db_session.add(project)
            db_session.commit()
    
    def test_content_required_fields(self, db_session):
        """Test content required fields validation"""
        # Test missing required fields
        with pytest.raises(IntegrityError):
            content = Content()  # Missing required fields
            db_session.add(content)
            db_session.commit()
    
    def test_revenue_required_fields(self, db_session):
        """Test revenue required fields validation"""
        # Test missing required fields
        with pytest.raises(IntegrityError):
            revenue = Revenue()  # Missing required fields
            db_session.add(revenue)
            db_session.commit()
    
    def test_project_name_uniqueness(self, db_session):
        """Test project name uniqueness constraint"""
        # Create first project
        project1 = Project(name="Unique Project", status="active")
        db_session.add(project1)
        db_session.commit()
        
        # Try to create second project with same name
        with pytest.raises(IntegrityError):
            project2 = Project(name="Unique Project", status="active")
            db_session.add(project2)
            db_session.commit()
    
    def test_content_project_foreign_key(self, db_session):
        """Test content project foreign key constraint"""
        # Try to create content with non-existent project
        with pytest.raises(IntegrityError):
            content = Content(
                project_id=999,  # Non-existent project
                title="Test Content",
                content_type="blog",
                content_data="Test content"
            )
            db_session.add(content)
            db_session.commit()
    
    def test_revenue_project_foreign_key(self, db_session):
        """Test revenue project foreign key constraint"""
        # Try to create revenue with non-existent project
        with pytest.raises(IntegrityError):
            revenue = Revenue(
                project_id=999,  # Non-existent project
                amount=100.0,
                source="test",
                description="Test revenue"
            )
            db_session.add(revenue)
            db_session.commit()

@pytest.mark.database
@pytest.mark.performance
class TestDatabasePerformance:
    """Test database performance with large datasets"""
    
    def test_bulk_project_creation(self, db_session, benchmark):
        """Test bulk project creation performance"""
        def create_bulk_projects():
            projects = []
            for i in range(100):
                project = Project(
                    name=f"Bulk Project {i}",
                    status="active",
                    budget=1000.0,
                    revenue=500.0
                )
                projects.append(project)
            
            db_session.add_all(projects)
            db_session.commit()
            return len(projects)
        
        result = benchmark(create_bulk_projects)
        assert result == 100
    
    def test_bulk_content_creation(self, db_session, benchmark):
        """Test bulk content creation performance"""
        # Create project first
        project = create_project(db_session, name="Bulk Test Project", status="active")
        
        def create_bulk_content():
            contents = []
            for i in range(100):
                content = Content(
                    project_id=project.id,
                    title=f"Bulk Content {i}",
                    content_type="blog",
                    content_data=f"Bulk content data {i}"
                )
                contents.append(content)
            
            db_session.add_all(contents)
            db_session.commit()
            return len(contents)
        
        result = benchmark(create_bulk_content)
        assert result == 100
    
    def test_complex_query_performance(self, db_session, benchmark):
        """Test complex query performance"""
        # Create test data
        project = create_project(db_session, name="Performance Test Project", status="active")
        
        # Create content and revenue
        for i in range(50):
            content = create_content(db_session, project_id=project.id, title=f"Content {i}", content_type="blog", content_data=f"Content {i}")
            revenue = create_revenue(db_session, project_id=project.id, amount=100.0 + i, source=f"source_{i}", description=f"Revenue {i}")
        
        def complex_query():
            # Complex query with joins
            result = db_session.query(Project).options(
                joinedload(Project.content),
                joinedload(Project.revenue)
            ).filter(Project.id == project.id).first()
            return result
        
        result = benchmark(complex_query)
        assert result is not None
        assert len(result.content) == 50
        assert len(result.revenue) == 50 