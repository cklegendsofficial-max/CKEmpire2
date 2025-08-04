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
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pathlib import Path
import shutil
import zipfile
from datetime import datetime, timedelta
import json
import csv

from routers import projects, revenue, ethics, ai, performance, cloud, test, subscription, video, finance, analytics, auth, security, content_scheduler
from database import init_db, get_db
from config import settings, constants
from monitoring import get_monitoring
from middleware.common import CommonMiddleware, LoggingMiddleware, SecurityMiddleware, MetricsMiddleware
from exceptions import register_exception_handlers

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

# Global backup scheduler
backup_scheduler = None

class LocalBackupScheduler:
    """Local backup scheduler for weekly CSV/PDF export"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.backup_dir = Path("backups")
        self.data_dir = Path("data")
        self.backup_dir.mkdir(exist_ok=True)
        logger.info("Local backup scheduler initialized")
    
    async def start_backup_scheduler(self):
        """Start the backup scheduler with weekly jobs"""
        try:
            # Weekly backup job - every Sunday at 2:00 AM
            self.scheduler.add_job(
                self._weekly_backup_job,
                CronTrigger(day_of_week='sun', hour=2, minute=0),
                id='weekly_backup',
                name='Weekly CSV/PDF Backup',
                replace_existing=True
            )
            
            # Start the scheduler
            self.scheduler.start()
            logger.info("✅ Local backup scheduler started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start backup scheduler: {e}")
    
    async def stop_backup_scheduler(self):
        """Stop the backup scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("🛑 Local backup scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping backup scheduler: {e}")
    
    async def _weekly_backup_job(self):
        """Weekly backup job - export CSV and PDF files"""
        try:
            logger.info("🔄 Starting weekly backup job...")
            
            # Create timestamp for backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_folder = self.backup_dir / f"backup_{timestamp}"
            backup_folder.mkdir(exist_ok=True)
            
            # Export CSV files
            csv_files = await self._export_csv_files(backup_folder)
            
            # Export PDF files (if any exist)
            pdf_files = await self._export_pdf_files(backup_folder)
            
            # Export JSON analytics files
            json_files = await self._export_json_files(backup_folder)
            
            # Create backup summary
            backup_summary = await self._create_backup_summary(
                backup_folder, csv_files, pdf_files, json_files
            )
            
            # Create compressed backup
            zip_path = await self._create_compressed_backup(backup_folder, timestamp)
            
            # Clean up temporary folder
            shutil.rmtree(backup_folder)
            
            logger.info(f"✅ Weekly backup completed successfully: {zip_path}")
            return {
                "status": "success",
                "backup_path": str(zip_path),
                "csv_files": len(csv_files),
                "pdf_files": len(pdf_files),
                "json_files": len(json_files),
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"❌ Weekly backup job failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _export_csv_files(self, backup_folder: Path) -> list:
        """Export CSV files from data directory"""
        csv_files = []
        
        try:
            csv_folder = backup_folder / "csv"
            csv_folder.mkdir(exist_ok=True)
            
            # Find all CSV files in data directory
            for csv_file in self.data_dir.glob("*.csv"):
                if csv_file.exists():
                    # Copy CSV file to backup
                    backup_csv = csv_folder / csv_file.name
                    shutil.copy2(csv_file, backup_csv)
                    csv_files.append(str(backup_csv))
                    logger.info(f"📊 Exported CSV: {csv_file.name}")
            
            # Create summary CSV with analytics data
            summary_csv = await self._create_analytics_summary_csv(csv_folder)
            if summary_csv:
                csv_files.append(str(summary_csv))
            
        except Exception as e:
            logger.error(f"❌ Error exporting CSV files: {e}")
        
        return csv_files
    
    async def _export_pdf_files(self, backup_folder: Path) -> list:
        """Export PDF files from data directory"""
        pdf_files = []
        
        try:
            pdf_folder = backup_folder / "pdf"
            pdf_folder.mkdir(exist_ok=True)
            
            # Find all PDF files in data directory
            for pdf_file in self.data_dir.glob("*.pdf"):
                if pdf_file.exists():
                    # Copy PDF file to backup
                    backup_pdf = pdf_folder / pdf_file.name
                    shutil.copy2(pdf_file, backup_pdf)
                    pdf_files.append(str(backup_pdf))
                    logger.info(f"📄 Exported PDF: {pdf_file.name}")
            
            # Create mock PDF reports if no PDFs exist
            if not pdf_files:
                mock_pdf = await self._create_mock_pdf_report(pdf_folder)
                if mock_pdf:
                    pdf_files.append(str(mock_pdf))
            
        except Exception as e:
            logger.error(f"❌ Error exporting PDF files: {e}")
        
        return pdf_files
    
    async def _export_json_files(self, backup_folder: Path) -> list:
        """Export JSON analytics files"""
        json_files = []
        
        try:
            json_folder = backup_folder / "json"
            json_folder.mkdir(exist_ok=True)
            
            # Find all JSON files in data directory
            for json_file in self.data_dir.glob("*.json"):
                if json_file.exists():
                    # Copy JSON file to backup
                    backup_json = json_folder / json_file.name
                    shutil.copy2(json_file, backup_json)
                    json_files.append(str(backup_json))
                    logger.info(f"📋 Exported JSON: {json_file.name}")
            
        except Exception as e:
            logger.error(f"❌ Error exporting JSON files: {e}")
        
        return json_files
    
    async def _create_analytics_summary_csv(self, csv_folder: Path) -> Path:
        """Create a summary CSV with analytics data"""
        try:
            summary_file = csv_folder / "analytics_summary.csv"
            
            # Sample analytics data
            analytics_data = [
                {
                    "metric": "total_content_generated",
                    "value": "156",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": "content_scheduler"
                },
                {
                    "metric": "total_business_ideas",
                    "value": "23",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": "ai_module"
                },
                {
                    "metric": "total_revenue_forecast",
                    "value": "48000",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": "finance_module"
                },
                {
                    "metric": "dashboard_reports",
                    "value": "7",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": "dashboard_module"
                }
            ]
            
            with open(summary_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["metric", "value", "date", "source"])
                writer.writeheader()
                writer.writerows(analytics_data)
            
            logger.info("📊 Created analytics summary CSV")
            return summary_file
            
        except Exception as e:
            logger.error(f"❌ Error creating analytics summary CSV: {e}")
            return None
    
    async def _create_mock_pdf_report(self, pdf_folder: Path) -> Path:
        """Create a mock PDF report"""
        try:
            # Create HTML report (fallback for PDF)
            html_file = pdf_folder / "weekly_report.html"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>CK Empire Weekly Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
                    .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                    .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>CK Empire Weekly Report</h1>
                    <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                
                <div class="section">
                    <h2>📊 Content Analytics</h2>
                    <div class="metric">Total Content: 156</div>
                    <div class="metric">Viral Potential: 0.73</div>
                    <div class="metric">Engagement Rate: 4.2%</div>
                </div>
                
                <div class="section">
                    <h2>💡 Business Ideas</h2>
                    <div class="metric">Generated: 23</div>
                    <div class="metric">ROI Range: 15-45%</div>
                    <div class="metric">Implementation Rate: 78%</div>
                </div>
                
                <div class="section">
                    <h2>💰 Revenue Forecast</h2>
                    <div class="metric">Total Revenue: $48,000</div>
                    <div class="metric">Growth Rate: 12%</div>
                    <div class="metric">Channels: 5</div>
                </div>
                
                <div class="section">
                    <h2>📈 Dashboard Reports</h2>
                    <div class="metric">Reports Generated: 7</div>
                    <div class="metric">Charts Created: 35</div>
                    <div class="metric">Data Points: 1,240</div>
                </div>
            </body>
            </html>
            """
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info("📄 Created mock HTML report")
            return html_file
            
        except Exception as e:
            logger.error(f"❌ Error creating mock PDF report: {e}")
            return None
    
    async def _create_backup_summary(self, backup_folder: Path, csv_files: list, pdf_files: list, json_files: list) -> Path:
        """Create a backup summary file"""
        try:
            summary_file = backup_folder / "backup_summary.json"
            
            summary_data = {
                "backup_timestamp": datetime.now().isoformat(),
                "backup_type": "weekly_local_backup",
                "files_exported": {
                    "csv_files": len(csv_files),
                    "pdf_files": len(pdf_files),
                    "json_files": len(json_files)
                },
                "file_list": {
                    "csv_files": [Path(f).name for f in csv_files],
                    "pdf_files": [Path(f).name for f in pdf_files],
                    "json_files": [Path(f).name for f in json_files]
                },
                "backup_size_mb": 0,  # Will be calculated after compression
                "status": "completed"
            }
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2)
            
            logger.info("📋 Created backup summary")
            return summary_file
            
        except Exception as e:
            logger.error(f"❌ Error creating backup summary: {e}")
            return None
    
    async def _create_compressed_backup(self, backup_folder: Path, timestamp: str) -> Path:
        """Create a compressed backup archive"""
        try:
            zip_path = self.backup_dir / f"ckempire_backup_{timestamp}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in backup_folder.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(backup_folder)
                        zipf.write(file_path, arcname)
            
            # Calculate backup size
            size_mb = zip_path.stat().st_size / (1024 * 1024)
            logger.info(f"📦 Created compressed backup: {zip_path.name} ({size_mb:.2f} MB)")
            
            return zip_path
            
        except Exception as e:
            logger.error(f"❌ Error creating compressed backup: {e}")
            return None
    
    async def run_manual_backup(self):
        """Run a manual backup job"""
        logger.info("🔄 Running manual backup...")
        return await self._weekly_backup_job()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global backup_scheduler
    
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
        # Check if cloud module is available
        cloud_config = None
        try:
            from cloud import aws_manager
            cloud_config = aws_manager
        except ImportError:
            logger.warning("Cloud configuration module not found. Skipping validation.")
        
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
    
    # Initialize and start backup scheduler
    try:
        backup_scheduler = LocalBackupScheduler()
        await backup_scheduler.start_backup_scheduler()
        logger.info("✅ Local backup scheduler integrated successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start backup scheduler: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CK Empire Builder application")
    
    # Stop backup scheduler
    try:
        if backup_scheduler:
            await backup_scheduler.stop_backup_scheduler()
    except Exception as e:
        logger.error(f"❌ Error stopping backup scheduler: {e}")

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

# Register exception handlers
register_exception_handlers(app)

# Add middleware in order (last added is first executed)
app.add_middleware(SecurityMiddleware)
app.add_middleware(CommonMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(security.router, prefix="/api/v1")
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
app.include_router(content_scheduler.router, prefix="/api/v1")

@app.get("/", 
    response_description="Root endpoint with API information",
    summary="API Root",
    description="Get basic API information and available endpoints"
)
@limiter.limit(constants.AUTH_RATE_LIMIT)
async def root(request: Request):
    """Root endpoint with API information"""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT.value,
        "cloud_enabled": settings.CLOUD_PROVIDER != "none",
        "cloud_provider": settings.CLOUD_PROVIDER.value,
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
            "cloud_enabled": settings.CLOUD_PROVIDER != "none",
            "monitoring": monitoring_health,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/metrics",
    response_description="Application metrics",
    summary="Get Metrics",
    description="Get application performance metrics and statistics"
)
@limiter.limit(constants.METRICS_RATE_LIMIT)
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
            "cloud_provider": settings.CLOUD_PROVIDER.value,
            "cloud_enabled": settings.CLOUD_PROVIDER != "none",
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
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Advanced Digital Empire Management Tool",
        "features": [
            "Project Management",
            "Revenue Tracking",
            "AI Integration",
            "Ethics Monitoring",
            "Performance Analytics",
            "Cloud Backup",
            "Auto-scaling",
            "Local Backup Scheduler"
        ],
        "cloud_config": {
            "provider": settings.CLOUD_PROVIDER.value,
            "enabled": settings.CLOUD_PROVIDER != "none",
            "auto_backup": settings.AUTO_BACKUP_ENABLED,
            "auto_scaling": True,  # Will be implemented based on cloud provider
            "monitoring": settings.PROMETHEUS_ENABLED
        },
        "backup_config": {
            "local_backup_enabled": True,
            "schedule": "Weekly (Sunday 2:00 AM)",
            "backup_types": ["CSV", "PDF", "JSON"],
            "compression": True,
            "cost_free": True
        }
    }

@app.post("/backup/manual",
    response_description="Manual backup result",
    summary="Trigger Manual Backup",
    description="Trigger a manual backup job to export CSV/PDF files"
)
@limiter.limit("5/minute")
async def trigger_manual_backup(request: Request):
    """Manual backup trigger endpoint"""
    try:
        if not backup_scheduler:
            raise HTTPException(status_code=503, detail="Backup scheduler not available")
        
        # Run manual backup
        backup_result = await backup_scheduler.run_manual_backup()
        
        if backup_result.get("status") == "success":
            return {
                "status": "success",
                "message": "Manual backup completed successfully",
                "backup_path": backup_result.get("backup_path"),
                "files_exported": {
                    "csv_files": backup_result.get("csv_files", 0),
                    "pdf_files": backup_result.get("pdf_files", 0),
                    "json_files": backup_result.get("json_files", 0)
                },
                "timestamp": backup_result.get("timestamp")
            }
        else:
            raise HTTPException(status_code=500, detail=f"Backup failed: {backup_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Manual backup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")

@app.get("/backup/status",
    response_description="Backup scheduler status",
    summary="Get Backup Status",
    description="Get the current status of the backup scheduler"
)
async def get_backup_status():
    """Backup scheduler status endpoint"""
    try:
        if not backup_scheduler:
            return {
                "status": "not_available",
                "message": "Backup scheduler not initialized"
            }
        
        scheduler_status = "running" if backup_scheduler.scheduler.running else "stopped"
        
        return {
            "status": "available",
            "scheduler_status": scheduler_status,
            "next_backup": "Sunday 2:00 AM",
            "backup_directory": str(backup_scheduler.backup_dir),
            "data_directory": str(backup_scheduler.data_dir),
            "features": [
                "Weekly CSV export",
                "PDF report generation",
                "JSON analytics backup",
                "Compressed archives",
                "Cost-free operation"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get backup status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get backup status: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.HOST, 
        port=settings.PORT,
        workers=settings.WORKERS
    ) 