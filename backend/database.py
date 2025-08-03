from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy import event
from datetime import datetime
import logging
from typing import Generator, Optional
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
try:
    from settings import settings
except ImportError:
    # For testing purposes, create a simple settings object
    class Settings:
        DATABASE_URL = "sqlite:///./test.db"
        DEBUG = True
    
    settings = Settings()

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Encryption setup
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    # Generate a new key if not provided
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    logger.warning("⚠️  No ENCRYPTION_KEY provided, using generated key")

try:
    cipher_suite = Fernet(ENCRYPTION_KEY.encode())
except Exception as e:
    logger.error(f"❌ Encryption setup failed: {e}")
    cipher_suite = None

def encrypt_value(value: str) -> str:
    """Encrypt a string value"""
    if not cipher_suite or not value:
        return value
    try:
        return cipher_suite.encrypt(value.encode()).decode()
    except Exception as e:
        logger.error(f"❌ Encryption failed: {e}")
        return value

def decrypt_value(encrypted_value: str) -> str:
    """Decrypt a string value"""
    if not cipher_suite or not encrypted_value:
        return encrypted_value
    try:
        return cipher_suite.decrypt(encrypted_value.encode()).decode()
    except Exception as e:
        logger.error(f"❌ Decryption failed: {e}")
        return encrypted_value

# Create SQLAlchemy engine with environment variable support
DATABASE_URL = os.getenv('DB_URL', settings.DATABASE_URL)
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base
Base = declarative_base()

# Database Models
class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active")
    budget = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    metadata_encrypted = Column(Text, nullable=True)  # Encrypted metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"

class Content(Base):
    """Content model for various content types"""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False)  # blog, video, social, email
    content_data = Column(Text, nullable=False)  # Encrypted content
    metadata_json = Column(JSON, nullable=True)  # Additional metadata
    status = Column(String(50), default="draft")
    ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Content(id={self.id}, title='{self.title}', type='{self.content_type}')>"

class Revenue(Base):
    """Revenue model"""
    __tablename__ = "revenues"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    source = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    metadata_encrypted = Column(Text, nullable=True)  # Encrypted metadata
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Revenue(id={self.id}, project_id={self.project_id}, amount={self.amount})>"

class AuditLog(Base):
    """Audit log for tracking all database operations"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=False)
    operation = Column(String(20), nullable=False)  # INSERT, UPDATE, DELETE
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    user_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, table='{self.table_name}', operation='{self.operation}')>"

class EthicsLog(Base):
    """Ethics monitoring log"""
    __tablename__ = "ethics_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, nullable=True, index=True)
    bias_detected = Column(Boolean, default=False)
    bias_score = Column(Float, nullable=True)
    fairness_score = Column(Float, nullable=True)
    bias_types = Column(Text, nullable=True)  # JSON string of bias types
    status = Column(String(50), nullable=True)  # approved, flagged, rejected, needs_review
    recommendations = Column(Text, nullable=True)  # JSON string of recommendations
    confidence_score = Column(Float, nullable=True)
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<EthicsLog(id={self.id}, content_id={self.content_id}, bias_detected={self.bias_detected})>"

class AILog(Base):
    """AI interaction log"""
    __tablename__ = "ai_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    model = Column(String(50), nullable=False)
    tokens_used = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AILog(id={self.id}, model='{self.model}', tokens={self.tokens_used})>"

class User(Base):
    """User model with enhanced security features"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=True)  # For local auth
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    oauth_provider = Column(String(50), nullable=True)  # google, github, microsoft
    oauth_id = Column(String(255), nullable=True)  # External provider user ID
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    
    # Enhanced security fields
    failed_login_attempts = Column(Integer, default=0)  # Track failed login attempts
    last_failed_login = Column(DateTime, nullable=True)  # Last failed login timestamp
    account_locked_until = Column(DateTime, nullable=True)  # Account lockout until
    password_changed_at = Column(DateTime, nullable=True)  # Last password change
    session_token_hash = Column(String(255), nullable=True)  # Current session token hash
    two_factor_enabled = Column(Boolean, default=False)  # 2FA status
    two_factor_secret = Column(String(255), nullable=True)  # 2FA secret
    last_security_audit = Column(DateTime, nullable=True)  # Last security audit
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

class Subscription(Base):
    """Subscription model"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    stripe_subscription_id = Column(String(255), unique=True, nullable=False, index=True)
    tier = Column(String(50), nullable=False)  # freemium, premium, enterprise
    billing_cycle = Column(String(20), nullable=False)  # monthly, yearly
    status = Column(String(50), nullable=False)  # active, inactive, trialing, past_due, canceled
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, tier='{self.tier}', status='{self.status}')>"

# SQLAlchemy event listeners for encryption and audit logging
@event.listens_for(Project, 'before_insert')
def encrypt_project_metadata(mapper, connection, target):
    """Encrypt sensitive fields before insert"""
    if target.metadata_encrypted:
        target.metadata_encrypted = encrypt_value(target.metadata_encrypted)

@event.listens_for(Project, 'before_update')
def encrypt_project_metadata_update(mapper, connection, target):
    """Encrypt sensitive fields before update"""
    if target.metadata_encrypted:
        target.metadata_encrypted = encrypt_value(target.metadata_encrypted)

@event.listens_for(Content, 'before_insert')
def encrypt_content_data(mapper, connection, target):
    """Encrypt content data before insert"""
    if target.content_data:
        target.content_data = encrypt_value(target.content_data)

@event.listens_for(Content, 'before_update')
def encrypt_content_data_update(mapper, connection, target):
    """Encrypt content data before update"""
    if target.content_data:
        target.content_data = encrypt_value(target.content_data)

@event.listens_for(Revenue, 'before_insert')
def encrypt_revenue_metadata(mapper, connection, target):
    """Encrypt revenue metadata before insert"""
    if target.metadata_encrypted:
        target.metadata_encrypted = encrypt_value(target.metadata_encrypted)

@event.listens_for(Revenue, 'before_update')
def encrypt_revenue_metadata_update(mapper, connection, target):
    """Encrypt revenue metadata before update"""
    if target.metadata_encrypted:
        target.metadata_encrypted = encrypt_value(target.metadata_encrypted)

# Audit logging events
def log_audit_event(db: Session, table_name: str, record_id: int, operation: str, 
                   old_values: dict = None, new_values: dict = None, user_id: int = None):
    """Log audit event"""
    try:
        audit_log = AuditLog(
            table_name=table_name,
            record_id=record_id,
            operation=operation,
            old_values=old_values,
            new_values=new_values,
            user_id=user_id
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        logger.error(f"❌ Audit logging failed: {e}")
        db.rollback()

@event.listens_for(Project, 'after_insert')
def audit_project_insert(mapper, connection, target):
    """Audit project insert"""
    db = SessionLocal()
    try:
        log_audit_event(db, 'projects', target.id, 'INSERT', new_values={
            'name': target.name,
            'status': target.status,
            'budget': target.budget,
            'revenue': target.revenue
        })
    finally:
        db.close()

@event.listens_for(Project, 'after_update')
def audit_project_update(mapper, connection, target):
    """Audit project update"""
    db = SessionLocal()
    try:
        log_audit_event(db, 'projects', target.id, 'UPDATE', new_values={
            'name': target.name,
            'status': target.status,
            'budget': target.budget,
            'revenue': target.revenue
        })
    finally:
        db.close()

@event.listens_for(Content, 'after_insert')
def audit_content_insert(mapper, connection, target):
    """Audit content insert"""
    db = SessionLocal()
    try:
        log_audit_event(db, 'content', target.id, 'INSERT', new_values={
            'title': target.title,
            'content_type': target.content_type,
            'status': target.status
        })
    finally:
        db.close()

@event.listens_for(Revenue, 'after_insert')
def audit_revenue_insert(mapper, connection, target):
    """Audit revenue insert"""
    db = SessionLocal()
    try:
        log_audit_event(db, 'revenues', target.id, 'INSERT', new_values={
            'project_id': target.project_id,
            'amount': target.amount,
            'source': target.source
        })
    finally:
        db.close()

# Database dependency
def get_db() -> Generator[Session, None, None]:
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database initialization
async def init_db():
    """Initialize database tables"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Create initial data if needed
        await create_initial_data()
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def create_initial_data():
    """Create initial data for the application"""
    db = SessionLocal()
    try:
        # Check if we have any projects
        project_count = db.query(Project).count()
        
        if project_count == 0:
            # Create sample project
            sample_project = Project(
                name="CK Empire Builder",
                description="Advanced digital empire management platform",
                status="active",
                budget=10000.0,
                revenue=5000.0,
                metadata_encrypted="Sample encrypted metadata"
            )
            db.add(sample_project)
            db.commit()
            logger.info("✅ Sample project created")
            
            # Create sample content
            sample_content = Content(
                project_id=sample_project.id,
                title="Welcome to CK Empire Builder",
                content_type="blog",
                content_data="This is the first blog post for our digital empire management platform.",
                status="published",
                ai_generated=False
            )
            db.add(sample_content)
            db.commit()
            logger.info("✅ Sample content created")
            
    except Exception as e:
        logger.error(f"❌ Failed to create initial data: {e}")
        db.rollback()
    finally:
        db.close()

# Database health check
def check_db_health() -> bool:
    """Check database health"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        return False

# Database utilities
def get_project_by_id(db: Session, project_id: int) -> Project:
    """Get project by ID"""
    return db.query(Project).filter(Project.id == project_id).first()

def get_all_projects(db: Session, skip: int = 0, limit: int = 100) -> list[Project]:
    """Get all projects with pagination"""
    return db.query(Project).offset(skip).limit(limit).all()

def create_project(db: Session, project_data: dict) -> Project:
    """Create new project"""
    project = Project(**project_data)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def update_project(db: Session, project_id: int, project_data: dict) -> Project:
    """Update project"""
    project = get_project_by_id(db, project_id)
    if project:
        for key, value in project_data.items():
            setattr(project, key, value)
        project.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(project)
    return project

def delete_project(db: Session, project_id: int) -> bool:
    """Delete project"""
    project = get_project_by_id(db, project_id)
    if project:
        db.delete(project)
        db.commit()
        return True
    return False

# Content utilities
def get_content_by_id(db: Session, content_id: int) -> Content:
    """Get content by ID"""
    return db.query(Content).filter(Content.id == content_id).first()

def get_content_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100) -> list[Content]:
    """Get content by project ID"""
    return db.query(Content).filter(Content.project_id == project_id).offset(skip).limit(limit).all()

def create_content(db: Session, content_data: dict) -> Content:
    """Create new content"""
    content = Content(**content_data)
    db.add(content)
    db.commit()
    db.refresh(content)
    return content

def update_content(db: Session, content_id: int, content_data: dict) -> Content:
    """Update content"""
    content = get_content_by_id(db, content_id)
    if content:
        for key, value in content_data.items():
            setattr(content, key, value)
        content.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(content)
    return content

def delete_content(db: Session, content_id: int) -> bool:
    """Delete content"""
    content = get_content_by_id(db, content_id)
    if content:
        db.delete(content)
        db.commit()
        return True
    return False

# Revenue utilities
def get_revenue_by_id(db: Session, revenue_id: int) -> Revenue:
    """Get revenue by ID"""
    return db.query(Revenue).filter(Revenue.id == revenue_id).first()

def get_revenue_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100) -> list[Revenue]:
    """Get revenue by project ID"""
    return db.query(Revenue).filter(Revenue.project_id == project_id).offset(skip).limit(limit).all()

def create_revenue(db: Session, revenue_data: dict) -> Revenue:
    """Create new revenue"""
    revenue = Revenue(**revenue_data)
    db.add(revenue)
    db.commit()
    db.refresh(revenue)
    return revenue

def update_revenue(db: Session, revenue_id: int, revenue_data: dict) -> Revenue:
    """Update revenue"""
    revenue = get_revenue_by_id(db, revenue_id)
    if revenue:
        for key, value in revenue_data.items():
            setattr(revenue, key, value)
        db.commit()
        db.refresh(revenue)
    return revenue

def delete_revenue(db: Session, revenue_id: int) -> bool:
    """Delete revenue"""
    revenue = get_revenue_by_id(db, revenue_id)
    if revenue:
        db.delete(revenue)
        db.commit()
        return True
    return False

# Audit log utilities
def get_audit_logs(db: Session, table_name: str = None, skip: int = 0, limit: int = 100) -> list[AuditLog]:
    """Get audit logs with optional filtering"""
    query = db.query(AuditLog)
    if table_name:
        query = query.filter(AuditLog.table_name == table_name)
    return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

def get_audit_logs_by_record(db: Session, table_name: str, record_id: int) -> list[AuditLog]:
    """Get audit logs for a specific record"""
    return db.query(AuditLog).filter(
        AuditLog.table_name == table_name,
        AuditLog.record_id == record_id
    ).order_by(AuditLog.timestamp.desc()).all() 