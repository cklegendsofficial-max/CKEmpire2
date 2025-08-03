#!/bin/bash

# CK Empire Local Deployment Script
# Deploys the entire stack locally using Docker Compose

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ckempire"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

echo -e "${BLUE}🚀 CK Empire Local Deployment${NC}"
echo "=================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_status "Docker is installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_status "Docker Compose is installed"
    
    # Check if ports are available
    local ports=(8000 3000 5432 6379 9200 5601 9090 3001 9093 80 443)
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "Port $port is already in use"
        fi
    done
}

# Create environment file if it doesn't exist
setup_environment() {
    echo -e "${BLUE}Setting up environment...${NC}"
    
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "Creating .env file with default values"
        cat > "$ENV_FILE" << EOF
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
EOF
        print_status "Created .env file"
    else
        print_status ".env file already exists"
    fi
}

# Build and start services
deploy_services() {
    echo -e "${BLUE}Deploying services...${NC}"
    
    # Stop existing containers
    print_status "Stopping existing containers"
    docker-compose down --remove-orphans
    
    # Build images
    print_status "Building Docker images"
    docker-compose build --no-cache
    
    # Start services
    print_status "Starting services"
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
}

# Health checks
check_health() {
    echo -e "${BLUE}Running health checks...${NC}"
    
    local services=(
        "backend:8000"
        "frontend:3000"
        "postgres:5432"
        "redis:6379"
        "elasticsearch:9200"
        "kibana:5601"
        "prometheus:9090"
        "grafana:3001"
        "alertmanager:9093"
    )
    
    for service in "${services[@]}"; do
        local service_name=$(echo $service | cut -d: -f1)
        local port=$(echo $service | cut -d: -f2)
        
        if curl -f http://localhost:$port >/dev/null 2>&1; then
            print_status "$service_name is healthy"
        else
            print_warning "$service_name health check failed"
        fi
    done
}

# Test API endpoints
test_api() {
    echo -e "${BLUE}Testing API endpoints...${NC}"
    
    local endpoints=(
        "http://localhost:8000/health"
        "http://localhost:8000/api/v1/projects"
        "http://localhost:8000/api/v1/analytics/health"
        "http://localhost:8000/api/v1/ai/health"
        "http://localhost:8000/api/v1/ethics/health"
        "http://localhost:8000/api/v1/finance/health"
        "http://localhost:8000/api/v1/video/health"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -f "$endpoint" >/dev/null 2>&1; then
            print_status "API endpoint $endpoint is working"
        else
            print_warning "API endpoint $endpoint failed"
        fi
    done
}

# Show service URLs
show_urls() {
    echo -e "${BLUE}Service URLs:${NC}"
    echo "=================================="
    echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
    echo -e "${GREEN}Backend API:${NC} http://localhost:8000"
    echo -e "${GREEN}API Documentation:${NC} http://localhost:8000/docs"
    echo -e "${GREEN}Grafana Dashboard:${NC} http://localhost:3001 (admin/admin)"
    echo -e "${GREEN}Prometheus:${NC} http://localhost:9090"
    echo -e "${GREEN}Kibana:${NC} http://localhost:5601"
    echo -e "${GREEN}Alertmanager:${NC} http://localhost:9093"
    echo -e "${GREEN}PostgreSQL:${NC} localhost:5432"
    echo -e "${GREEN}Redis:${NC} localhost:6379"
    echo -e "${GREEN}Elasticsearch:${NC} http://localhost:9200"
    echo ""
}

# Load testing
run_load_test() {
    echo -e "${BLUE}Running load test...${NC}"
    
    if command -v locust &> /dev/null; then
        print_status "Starting load test with Locust"
        cd backend
        locust -f tests/performance/locustfile.py \
            --host=http://localhost:8000 \
            --users=10 \
            --spawn-rate=2 \
            --run-time=60s \
            --headless \
            --html=load-test-report.html
        cd ..
        print_status "Load test completed. Report saved to backend/load-test-report.html"
    else
        print_warning "Locust not installed. Skipping load test."
        print_warning "Install with: pip install locust"
    fi
}

# Cleanup function
cleanup() {
    echo -e "${BLUE}Cleaning up...${NC}"
    docker-compose down --volumes --remove-orphans
    print_status "Cleanup completed"
}

# Main execution
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            setup_environment
            deploy_services
            check_health
            test_api
            show_urls
            ;;
        "test")
            test_api
            ;;
        "load-test")
            run_load_test
            ;;
        "cleanup")
            cleanup
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "restart")
            docker-compose restart
            ;;
        "status")
            docker-compose ps
            ;;
        *)
            echo "Usage: $0 {deploy|test|load-test|cleanup|logs|restart|status}"
            echo ""
            echo "Commands:"
            echo "  deploy     - Deploy all services"
            echo "  test       - Test API endpoints"
            echo "  load-test  - Run load tests"
            echo "  cleanup    - Stop and remove all containers"
            echo "  logs       - Show logs from all services"
            echo "  restart    - Restart all services"
            echo "  status     - Show service status"
            exit 1
            ;;
    esac
}

# Handle script interruption
trap cleanup EXIT

# Run main function
main "$@" 