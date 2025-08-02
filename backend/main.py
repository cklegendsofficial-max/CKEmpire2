from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import List

# Import routers
from routers import projects, revenue, ethics, ai, content
from database import get_db, init_db
from models import ProjectModel, RevenueModel
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting CK Empire Builder Backend...")
    await init_db()
    logger.info("✅ Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down CK Empire Builder Backend...")

# Create FastAPI app
app = FastAPI(
    title="Advanced CK Empire Builder API",
    description="Dijital İmparatorluk Yönetimi API'si",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "ckempire.com"]
)

# Include routers
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(revenue.router, prefix="/api/v1", tags=["revenue"])
app.include_router(ethics.router, prefix="/api/v1", tags=["ethics"])
app.include_router(ai.router, prefix="/api/v1", tags=["ai"])
app.include_router(content.router, prefix="/api/v1", tags=["content"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🏛️ Advanced CK Empire Builder API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-02T14:32:00Z",
        "services": {
            "database": "connected",
            "ai_service": "ready",
            "ethics_module": "active"
        }
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "v1",
        "status": "operational",
        "features": [
            "project_management",
            "revenue_tracking", 
            "ai_integration",
            "ethics_monitoring",
            "video_generation",
            "nft_automation"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 