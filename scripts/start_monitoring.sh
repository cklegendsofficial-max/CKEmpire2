#!/bin/bash

# CK Empire Builder - Monitoring Startup Script

echo "🚀 Starting CK Empire Builder Monitoring System"
echo "================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p deployment/prometheus
mkdir -p deployment/alertmanager
mkdir -p deployment/grafana/provisioning/datasources
mkdir -p deployment/grafana/provisioning/dashboards
mkdir -p deployment/logstash/pipeline
mkdir -p logs

# Copy configuration files if they don't exist
if [ ! -f deployment/prometheus/prometheus.yml ]; then
    echo "📋 Copying Prometheus configuration..."
    cp deployment/prometheus/prometheus.yml deployment/prometheus/prometheus.yml 2>/dev/null || echo "Prometheus config already exists"
fi

if [ ! -f deployment/alertmanager/alertmanager.yml ]; then
    echo "📋 Copying Alertmanager configuration..."
    cp deployment/alertmanager/alertmanager.yml deployment/alertmanager/alertmanager.yml 2>/dev/null || echo "Alertmanager config already exists"
fi

# Start monitoring stack
echo "🐳 Starting monitoring stack..."
cd deployment
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service status
echo "🔍 Checking service status..."

# Check Prometheus
if curl -s http://localhost:9090/api/v1/status/config > /dev/null; then
    echo "✅ Prometheus is running at http://localhost:9090"
else
    echo "❌ Prometheus is not responding"
fi

# Check Grafana
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ Grafana is running at http://localhost:3000"
else
    echo "❌ Grafana is not responding"
fi

# Check Elasticsearch
if curl -s http://localhost:9200/_cluster/health > /dev/null; then
    echo "✅ Elasticsearch is running at http://localhost:9200"
else
    echo "❌ Elasticsearch is not responding"
fi

# Check Kibana
if curl -s http://localhost:5601/api/status > /dev/null; then
    echo "✅ Kibana is running at http://localhost:5601"
else
    echo "❌ Kibana is not responding"
fi

# Check Alertmanager
if curl -s http://localhost:9093/api/v1/status > /dev/null; then
    echo "✅ Alertmanager is running at http://localhost:9093"
else
    echo "❌ Alertmanager is not responding"
fi

# Start backend with monitoring
echo "🐍 Starting CK Empire Builder backend..."
cd ../backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Set environment variables
export SENTRY_DSN="https://your-sentry-dsn@sentry.io/project-id"
export ELASTICSEARCH_HOST="localhost"
export ELASTICSEARCH_PORT="9200"
export ENVIRONMENT="development"

# Start the application
echo "🚀 Starting CK Empire Builder application..."
python main.py &

# Wait for backend to start
sleep 10

# Test the monitoring system
echo "🧪 Testing monitoring system..."

# Test health endpoint
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
fi

# Test metrics endpoint
if curl -s http://localhost:8000/metrics > /dev/null; then
    echo "✅ Metrics endpoint is working"
else
    echo "❌ Metrics endpoint failed"
fi

# Run monitoring tests
echo "🧪 Running monitoring tests..."
python test_monitoring.py

# Test error generation
echo "🐛 Testing error generation..."
curl -X POST http://localhost:8000/api/v1/test/error || echo "Error generation test completed"

# Test metrics generation
echo "📊 Testing metrics generation..."
curl -X POST http://localhost:8000/api/v1/test/metrics

# Test performance monitoring
echo "⚡ Testing performance monitoring..."
curl -X POST http://localhost:8000/api/v1/test/performance

# Test log generation
echo "📝 Testing log generation..."
curl -X GET http://localhost:8000/api/v1/test/logs

echo ""
echo "🎉 Monitoring system setup completed!"
echo ""
echo "📊 Monitoring URLs:"
echo "   - Prometheus: http://localhost:9090"
echo "   - Grafana: http://localhost:3000 (admin/admin123)"
echo "   - Kibana: http://localhost:5601"
echo "   - Alertmanager: http://localhost:9093"
echo "   - cAdvisor: http://localhost:8080"
echo "   - Node Exporter: http://localhost:9100"
echo ""
echo "🔧 Backend URLs:"
echo "   - API: http://localhost:8000"
echo "   - Health: http://localhost:8000/health"
echo "   - Metrics: http://localhost:8000/metrics"
echo "   - Docs: http://localhost:8000/docs"
echo ""
echo "🧪 Test Endpoints:"
echo "   - Error Generation: POST http://localhost:8000/api/v1/test/error"
echo "   - Metrics Generation: POST http://localhost:8000/api/v1/test/metrics"
echo "   - Performance Test: POST http://localhost:8000/api/v1/test/performance"
echo "   - Log Generation: GET http://localhost:8000/api/v1/test/logs"
echo ""
echo "📚 Documentation: docs/monitoring-setup.md"
echo ""
echo "🛑 To stop the monitoring stack:"
echo "   cd deployment && docker-compose -f docker-compose.monitoring.yml down" 