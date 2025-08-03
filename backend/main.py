from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging
import structlog
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from routers import projects, revenue, ethics, ai, performance, cloud, test, subscription, video, finance, analytics
from database import init_db, get_db
try:
    from config.cloud_config import cloud_config
except ImportError:
    cloud_config = None
from monitoring import get_monitoring
from middleware import MonitoringMiddleware, HealthCheckMiddleware, MetricsMiddleware

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting CK Empire Builder application")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Initialize cloud configuration
    try:
        if cloud_config:
            validation = cloud_config.validate_config()
            if not validation['valid']:
                logger.warning(f"Cloud configuration validation failed: {validation['errors']}")
            else:
                logger.info("Cloud configuration validated successfully")
        else:
            logger.warning("Cloud configuration module not found. Skipping validation.")
    except Exception as e:
        logger.error(f"Failed to validate cloud configuration: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CK Empire Builder application")

# Create FastAPI app with comprehensive documentation
app = FastAPI(
    title="CK Empire Builder API",
    description="""
    # CK Empire Builder - Advanced Digital Empire Management API
    
    ## Overview
    
    CK Empire Builder is a comprehensive digital empire management platform that provides:
    
    * **Project Management**: Organize and track digital projects
    * **Revenue Tracking**: Monitor income streams and financial metrics
    * **AI Integration**: Advanced AI features for content generation
    * **Ethics Monitoring**: Built-in ethical AI monitoring
    * **Performance Analytics**: Real-time metrics and insights
    * **Cloud Integration**: AWS/GCP integration with auto-scaling
    * **Backup & Recovery**: Automated backup and disaster recovery
    
    ## Features
    
    ### 🔥 Core Features
    - **Project Management**: Create, track, and manage digital projects
    - **Revenue Analytics**: Monitor income streams and financial performance
    - **AI-Powered Content**: Generate content using advanced AI models
    - **Ethics Compliance**: Built-in ethical AI monitoring and compliance
    - **Performance Monitoring**: Real-time analytics and insights
    
    ### ☁️ Cloud Features
    - **AWS Integration**: S3 backup, RDS database, ElastiCache Redis
    - **GCP Integration**: Cloud Storage, Cloud SQL, Memorystore
    - **Auto-scaling**: Kubernetes HPA for automatic scaling
    - **Backup & Recovery**: Automated database backups and restoration
    - **Monitoring**: CloudWatch metrics and alerts
    
    ### 🔒 Security Features
    - **Authentication**: JWT-based authentication
    - **Encryption**: End-to-end data encryption
    - **Rate Limiting**: API rate limiting and protection
    - **CORS**: Configurable CORS policies
    - **Audit Logging**: Comprehensive audit trails
    
    ## API Endpoints
    
    ### Projects
    - `GET /api/v1/projects` - List all projects
    - `POST /api/v1/projects` - Create new project
    - `GET /api/v1/projects/{project_id}` - Get project details
    - `PUT /api/v1/projects/{project_id}` - Update project
    - `DELETE /api/v1/projects/{project_id}` - Delete project
    
    ### Revenue
    - `GET /api/v1/revenue` - Get revenue analytics
    - `POST /api/v1/revenue` - Add revenue entry
    - `GET /api/v1/revenue/analytics` - Get revenue analytics
    - `GET /api/v1/revenue/trends` - Get revenue trends
    
    ### AI Features
    - `POST /api/v1/ai/ideas` - Generate AI ideas
    - `POST /api/v1/ai/content` - Generate AI content
    - `GET /api/v1/ai/agi-state` - Get AGI state
    - `POST /api/v1/ai/analyze` - Analyze content with AI
    
    ### Ethics
    - `POST /api/v1/ethics/check` - Check content ethics
    - `GET /api/v1/ethics/reports` - Get ethics reports
    - `POST /api/v1/ethics/flag` - Flag content for review
    
    ### Performance
    - `GET /api/v1/performance/metrics` - Get performance metrics
    - `GET /api/v1/performance/health` - Health check
    - `GET /api/v1/performance/status` - System status
    
    ### Cloud
    - `GET /api/v1/cloud/config` - Get cloud configuration
    - `POST /api/v1/cloud/backup` - Create backup
    - `GET /api/v1/cloud/backups` - List backups
    - `POST /api/v1/cloud/restore` - Restore from backup
    - `GET /api/v1/cloud/metrics` - Get cloud metrics
    
    ## Authentication
    
    Most endpoints require authentication. Use the following header:
    
    ```
    Authorization: Bearer <your-jwt-token>
    ```
    
    ## Rate Limiting
    
    API endpoints are rate-limited to ensure fair usage:
    - **Default**: 100 requests per minute
    - **Authentication**: 10 requests per minute
    - **Metrics**: 30 requests per minute
    
    ## Error Handling
    
    The API returns standard HTTP status codes:
    - `200` - Success
    - `201` - Created
    - `400` - Bad Request
    - `401` - Unauthorized
    - `403` - Forbidden
    - `404` - Not Found
    - `429` - Too Many Requests
    - `500` - Internal Server Error
    
    ## Development
    
    ### Local Development
    
    ```bash
    # Install dependencies
    pip install -r requirements.txt
    
    # Run the application
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    
    ### Docker
    
    ```bash
    # Build and run with Docker
    docker-compose up --build
    ```
    
    ### Kubernetes
    
    ```bash
    # Deploy to Kubernetes
    kubectl apply -f deployment/k8s/
    ```
    
    ## Support
    
    - **Documentation**: https://docs.ckempire.com
    - **GitHub**: https://github.com/ckempire/ck-empire-builder
    - **Issues**: https://github.com/ckempire/ck-empire-builder/issues
    - **Email**: support@ckempire.com
    
    ## License
    
    This project is licensed under the MIT License - see the LICENSE file for details.
    """,
    version="1.0.0",
    contact={
        "name": "CK Empire Team",
        "email": "support@ckempire.com",
        "url": "https://ckempire.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "https://api.ckempire.com",
            "description": "Production server"
        },
        {
            "url": "https://staging-api.ckempire.com",
            "description": "Staging server"
        },
        {
            "url": "http://localhost:8000",
            "description": "Local development server"
        }
    ],
    tags_metadata=[
        {
            "name": "projects",
            "description": "Project management operations. Create, read, update, and delete projects.",
        },
        {
            "name": "revenue",
            "description": "Revenue tracking and analytics. Monitor income streams and financial metrics.",
        },
        {
            "name": "ai",
            "description": "AI-powered features. Generate content, ideas, and analyze data using AI.",
        },
        {
            "name": "ethics",
            "description": "Ethics monitoring and compliance. Check content for ethical concerns.",
        },
        {
            "name": "performance",
            "description": "Performance monitoring and analytics. Get system metrics and health status.",
        },
        {
            "name": "cloud",
            "description": "Cloud infrastructure management. Backup, restore, and monitor cloud resources.",
        },
    ],
    lifespan=lifespan
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add monitoring middleware
app.add_middleware(MonitoringMiddleware)
app.add_middleware(HealthCheckMiddleware)
app.add_middleware(MetricsMiddleware)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Configure appropriately for production
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(projects.router, prefix="/api/v1")
app.include_router(revenue.router, prefix="/api/v1")
app.include_router(ethics.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(performance.router, prefix="/api/v1")
app.include_router(cloud.router, prefix="/api/v1")
app.include_router(test.router, prefix="/api/v1")
app.include_router(subscription.router, prefix="/api/v1")
app.include_router(video.router, prefix="/api/v1")
app.include_router(finance.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")

@app.get("/", 
    response_description="Root endpoint with API information",
    summary="API Root",
    description="Get basic API information and available endpoints"
)
@limiter.limit("10/minute")
async def root(request: Request):
    """Root endpoint with API information"""
    return {
        "message": "CK Empire Builder API",
        "version": "1.0.0",
        "status": "running",
        "cloud_enabled": cloud_config.is_cloud_enabled() if cloud_config else False,
        "cloud_provider": cloud_config.config.provider.value if cloud_config else "N/A",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json"
    }

@app.get("/health",
    response_description="Health check status",
    summary="Health Check",
    description="Check the health status of the API and its dependencies"
)
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db = get_db()
        db.execute("SELECT 1")
        
        # Get monitoring health status
        monitoring = get_monitoring()
        monitoring_health = monitoring.health_check()
        
        return {
            "status": "healthy",
            "database": "connected",
            "cloud_enabled": cloud_config.is_cloud_enabled() if cloud_config else False,
            "monitoring": monitoring_health,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/metrics",
    response_description="Application metrics",
    summary="Get Metrics",
    description="Get application performance metrics and statistics"
)
@limiter.limit("30/minute")
async def metrics(request: Request):
    """Application metrics endpoint"""
    try:
        db = get_db()
        
        # Get monitoring metrics
        monitoring = get_monitoring()
        prometheus_metrics = monitoring.get_metrics()
        
        # Get basic metrics
        metrics_data = {
            "consciousness_score": 0.45,
            "total_revenue": 48000,
            "active_agents": 18,
            "total_projects": 12,
            "total_content": 156,
            "cloud_provider": cloud_config.config.provider.value if cloud_config else "N/A",
            "cloud_enabled": cloud_config.is_cloud_enabled() if cloud_config else False,
            "prometheus_metrics": prometheus_metrics
        }
        
        return metrics_data
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")

@app.get("/info",
    response_description="Application information",
    summary="Get Info",
    description="Get detailed information about the application and its features"
)
async def info():
    """Application information endpoint"""
    return {
        "name": "CK Empire Builder",
        "version": "1.0.0",
        "description": "Advanced Digital Empire Management Tool",
        "features": [
            "Project Management",
            "Revenue Tracking",
            "AI Integration",
            "Ethics Monitoring",
            "Performance Analytics",
            "Cloud Backup",
            "Auto-scaling"
        ],
        "cloud_config": {
            "provider": cloud_config.config.provider.value if cloud_config else "N/A",
            "enabled": cloud_config.is_cloud_enabled() if cloud_config else False,
            "auto_backup": cloud_config.config.auto_backup if cloud_config else "N/A",
            "auto_scaling": cloud_config.config.auto_scaling if cloud_config else "N/A",
            "monitoring": cloud_config.config.monitoring if cloud_config else "N/A"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 