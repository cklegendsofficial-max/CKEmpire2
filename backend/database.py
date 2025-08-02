from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from datetime import datetime
import logging
from typing import Generator
from config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"

class Revenue(Base):
    """Revenue model"""
    __tablename__ = "revenues"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    source = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Revenue(id={self.id}, project_id={self.project_id}, amount={self.amount})>"

class EthicsLog(Base):
    """Ethics monitoring log"""
    __tablename__ = "ethics_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    bias_score = Column(Float, nullable=True)
    risk_level = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<EthicsLog(id={self.id}, action='{self.action}', risk_level='{self.risk_level}')>"

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
                revenue=5000.0
            )
            db.add(sample_project)
            db.commit()
            logger.info("✅ Sample project created")
            
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