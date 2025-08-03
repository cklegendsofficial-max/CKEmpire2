# CK Empire Builder - Monitoring Startup Script (PowerShell)

Write-Host "🚀 Starting CK Empire Builder Monitoring System" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "deployment/prometheus" | Out-Null
New-Item -ItemType Directory -Force -Path "deployment/alertmanager" | Out-Null
New-Item -ItemType Directory -Force -Path "deployment/grafana/provisioning/datasources" | Out-Null
New-Item -ItemType Directory -Force -Path "deployment/grafana/provisioning/dashboards" | Out-Null
New-Item -ItemType Directory -Force -Path "deployment/logstash/pipeline" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# Start monitoring stack
Write-Host "🐳 Starting monitoring stack..." -ForegroundColor Yellow
Set-Location deployment
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service status
Write-Host "🔍 Checking service status..." -ForegroundColor Yellow

# Check Prometheus
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090/api/v1/status/config" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Prometheus is running at http://localhost:9090" -ForegroundColor Green
} catch {
    Write-Host "❌ Prometheus is not responding" -ForegroundColor Red
}

# Check Grafana
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Grafana is running at http://localhost:3000" -ForegroundColor Green
} catch {
    Write-Host "❌ Grafana is not responding" -ForegroundColor Red
}

# Check Elasticsearch
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9200/_cluster/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Elasticsearch is running at http://localhost:9200" -ForegroundColor Green
} catch {
    Write-Host "❌ Elasticsearch is not responding" -ForegroundColor Red
}

# Check Kibana
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5601/api/status" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Kibana is running at http://localhost:5601" -ForegroundColor Green
} catch {
    Write-Host "❌ Kibana is not responding" -ForegroundColor Red
}

# Check Alertmanager
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9093/api/v1/status" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Alertmanager is running at http://localhost:9093" -ForegroundColor Green
} catch {
    Write-Host "❌ Alertmanager is not responding" -ForegroundColor Red
}

# Start backend with monitoring
Write-Host "🐍 Starting CK Empire Builder backend..." -ForegroundColor Yellow
Set-Location ../backend

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& "venv/Scripts/Activate.ps1"

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Set environment variables
$env:SENTRY_DSN = "https://your-sentry-dsn@sentry.io/project-id"
$env:ELASTICSEARCH_HOST = "localhost"
$env:ELASTICSEARCH_PORT = "9200"
$env:ENVIRONMENT = "development"

# Start the application
Write-Host "🚀 Starting CK Empire Builder application..." -ForegroundColor Yellow
Start-Process python -ArgumentList "main.py" -WindowStyle Hidden

# Wait for backend to start
Start-Sleep -Seconds 10

# Test the monitoring system
Write-Host "🧪 Testing monitoring system..." -ForegroundColor Yellow

# Test health endpoint
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Backend health check passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend health check failed" -ForegroundColor Red
}

# Test metrics endpoint
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/metrics" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Metrics endpoint is working" -ForegroundColor Green
} catch {
    Write-Host "❌ Metrics endpoint failed" -ForegroundColor Red
}

# Run monitoring tests
Write-Host "🧪 Running monitoring tests..." -ForegroundColor Yellow
python test_monitoring.py

# Test error generation
Write-Host "🐛 Testing error generation..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://localhost:8000/api/v1/test/error" -Method POST -UseBasicParsing -TimeoutSec 5
} catch {
    Write-Host "Error generation test completed" -ForegroundColor Yellow
}

# Test metrics generation
Write-Host "📊 Testing metrics generation..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/test/metrics" -Method POST -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Metrics generation test completed" -ForegroundColor Green
} catch {
    Write-Host "❌ Metrics generation test failed" -ForegroundColor Red
}

# Test performance monitoring
Write-Host "⚡ Testing performance monitoring..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/test/performance" -Method POST -UseBasicParsing -TimeoutSec 10
    Write-Host "✅ Performance monitoring test completed" -ForegroundColor Green
} catch {
    Write-Host "❌ Performance monitoring test failed" -ForegroundColor Red
}

# Test log generation
Write-Host "📝 Testing log generation..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/test/logs" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Log generation test completed" -ForegroundColor Green
} catch {
    Write-Host "❌ Log generation test failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Monitoring system setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Monitoring URLs:" -ForegroundColor Cyan
Write-Host "   - Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "   - Grafana: http://localhost:3000 (admin/admin123)" -ForegroundColor White
Write-Host "   - Kibana: http://localhost:5601" -ForegroundColor White
Write-Host "   - Alertmanager: http://localhost:9093" -ForegroundColor White
Write-Host "   - cAdvisor: http://localhost:8080" -ForegroundColor White
Write-Host "   - Node Exporter: http://localhost:9100" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Backend URLs:" -ForegroundColor Cyan
Write-Host "   - API: http://localhost:8000" -ForegroundColor White
Write-Host "   - Health: http://localhost:8000/health" -ForegroundColor White
Write-Host "   - Metrics: http://localhost:8000/metrics" -ForegroundColor White
Write-Host "   - Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Test Endpoints:" -ForegroundColor Cyan
Write-Host "   - Error Generation: POST http://localhost:8000/api/v1/test/error" -ForegroundColor White
Write-Host "   - Metrics Generation: POST http://localhost:8000/api/v1/test/metrics" -ForegroundColor White
Write-Host "   - Performance Test: POST http://localhost:8000/api/v1/test/performance" -ForegroundColor White
Write-Host "   - Log Generation: GET http://localhost:8000/api/v1/test/logs" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation: docs/monitoring-setup.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "🛑 To stop the monitoring stack:" -ForegroundColor Yellow
Write-Host "   cd deployment && docker-compose -f docker-compose.monitoring.yml down" -ForegroundColor White 