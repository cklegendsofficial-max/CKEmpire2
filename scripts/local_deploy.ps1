# CK Empire Local Deployment Script (PowerShell)
# Deploys the entire stack locally using Docker Compose

param(
    [Parameter(Position=0)]
    [ValidateSet("deploy", "test", "load-test", "cleanup", "logs", "restart", "status")]
    [string]$Command = "deploy"
)

# Configuration
$ProjectName = "ckempire"
$ComposeFile = "docker-compose.yml"
$EnvFile = ".env"

Write-Host "🚀 CK Empire Local Deployment" -ForegroundColor Blue
Write-Host "==================================" -ForegroundColor Blue

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# Check prerequisites
function Test-Prerequisites {
    Write-Host "Checking prerequisites..." -ForegroundColor Blue
    
    # Check Docker
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker is not installed"
        exit 1
    }
    Write-Status "Docker is installed"
    
    # Check Docker Compose
    if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Write-Error "Docker Compose is not installed"
        exit 1
    }
    Write-Status "Docker Compose is installed"
    
    # Check if ports are available
    $ports = @(8000, 3000, 5432, 6379, 9200, 5601, 9090, 3001, 9093, 80, 443)
    foreach ($port in $ports) {
        $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connection) {
            Write-Warning "Port $port is already in use"
        }
    }
}

# Create environment file if it doesn't exist
function Setup-Environment {
    Write-Host "Setting up environment..." -ForegroundColor Blue
    
    if (-not (Test-Path $EnvFile)) {
        Write-Warning "Creating .env file with default values"
        @"
# CK Empire Environment Variables
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://ckempire:password@postgres:5432/ckempire
POSTGRES_DB=ckempire
POSTGRES_USER=ckempire
POSTGRES_PASSWORD=password

# Redis
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=your-secret-key-change-in-production
ENCRYPTION_KEY=your-encryption-key-change-in-production

# OpenAI (optional)
OPENAI_API_KEY=

# Sentry (optional)
SENTRY_DSN=

# AWS (optional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
ELASTICSEARCH_ENABLED=true
"@ | Out-File -FilePath $EnvFile -Encoding UTF8
        Write-Status "Created .env file"
    } else {
        Write-Status ".env file already exists"
    }
}

# Build and start services
function Deploy-Services {
    Write-Host "Deploying services..." -ForegroundColor Blue
    
    # Stop existing containers
    Write-Status "Stopping existing containers"
    docker-compose down --remove-orphans
    
    # Build images
    Write-Status "Building Docker images"
    docker-compose build --no-cache
    
    # Start services
    Write-Status "Starting services"
    docker-compose up -d
    
    # Wait for services to be ready
    Write-Status "Waiting for services to be ready..."
    Start-Sleep -Seconds 30
}

# Health checks
function Test-Health {
    Write-Host "Running health checks..." -ForegroundColor Blue
    
    $services = @(
        @{Name="backend"; Port=8000},
        @{Name="frontend"; Port=3000},
        @{Name="postgres"; Port=5432},
        @{Name="redis"; Port=6379},
        @{Name="elasticsearch"; Port=9200},
        @{Name="kibana"; Port=5601},
        @{Name="prometheus"; Port=9090},
        @{Name="grafana"; Port=3001},
        @{Name="alertmanager"; Port=9093}
    )
    
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$($service.Port)" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Status "$($service.Name) is healthy"
            } else {
                Write-Warning "$($service.Name) health check failed"
            }
        } catch {
            Write-Warning "$($service.Name) health check failed"
        }
    }
}

# Test API endpoints
function Test-API {
    Write-Host "Testing API endpoints..." -ForegroundColor Blue
    
    $endpoints = @(
        "http://localhost:8000/health",
        "http://localhost:8000/api/v1/projects",
        "http://localhost:8000/api/v1/analytics/health",
        "http://localhost:8000/api/v1/ai/health",
        "http://localhost:8000/api/v1/ethics/health",
        "http://localhost:8000/api/v1/finance/health",
        "http://localhost:8000/api/v1/video/health"
    )
    
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Status "API endpoint $endpoint is working"
            } else {
                Write-Warning "API endpoint $endpoint failed"
            }
        } catch {
            Write-Warning "API endpoint $endpoint failed"
        }
    }
}

# Show service URLs
function Show-URLs {
    Write-Host "Service URLs:" -ForegroundColor Blue
    Write-Host "==================================" -ForegroundColor Blue
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
    Write-Host "Backend API: http://localhost:8000" -ForegroundColor Green
    Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Green
    Write-Host "Grafana Dashboard: http://localhost:3001 (admin/admin)" -ForegroundColor Green
    Write-Host "Prometheus: http://localhost:9090" -ForegroundColor Green
    Write-Host "Kibana: http://localhost:5601" -ForegroundColor Green
    Write-Host "Alertmanager: http://localhost:9093" -ForegroundColor Green
    Write-Host "PostgreSQL: localhost:5432" -ForegroundColor Green
    Write-Host "Redis: localhost:6379" -ForegroundColor Green
    Write-Host "Elasticsearch: http://localhost:9200" -ForegroundColor Green
    Write-Host ""
}

# Load testing
function Test-Load {
    Write-Host "Running load test..." -ForegroundColor Blue
    
    if (Get-Command locust -ErrorAction SilentlyContinue) {
        Write-Status "Starting load test with Locust"
        Set-Location backend
        locust -f tests/performance/locustfile.py `
            --host=http://localhost:8000 `
            --users=10 `
            --spawn-rate=2 `
            --run-time=60s `
            --headless `
            --html=load-test-report.html
        Set-Location ..
        Write-Status "Load test completed. Report saved to backend/load-test-report.html"
    } else {
        Write-Warning "Locust not installed. Skipping load test."
        Write-Warning "Install with: pip install locust"
    }
}

# Cleanup function
function Remove-All {
    Write-Host "Cleaning up..." -ForegroundColor Blue
    docker-compose down --volumes --remove-orphans
    Write-Status "Cleanup completed"
}

# Main execution
switch ($Command) {
    "deploy" {
        Test-Prerequisites
        Setup-Environment
        Deploy-Services
        Test-Health
        Test-API
        Show-URLs
    }
    "test" {
        Test-API
    }
    "load-test" {
        Test-Load
    }
    "cleanup" {
        Remove-All
    }
    "logs" {
        docker-compose logs -f
    }
    "restart" {
        docker-compose restart
    }
    "status" {
        docker-compose ps
    }
    default {
        Write-Host "Usage: .\local_deploy.ps1 {deploy|test|load-test|cleanup|logs|restart|status}" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Commands:" -ForegroundColor Yellow
        Write-Host "  deploy     - Deploy all services" -ForegroundColor White
        Write-Host "  test       - Test API endpoints" -ForegroundColor White
        Write-Host "  load-test  - Run load tests" -ForegroundColor White
        Write-Host "  cleanup    - Stop and remove all containers" -ForegroundColor White
        Write-Host "  logs       - Show logs from all services" -ForegroundColor White
        Write-Host "  restart    - Restart all services" -ForegroundColor White
        Write-Host "  status     - Show service status" -ForegroundColor White
        exit 1
    }
} 