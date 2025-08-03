#!/bin/bash

# CK Empire Builder - Minikube Test Deployment Script
# This script tests the deployment on a local minikube cluster

set -e

echo "🚀 Starting CK Empire Builder Minikube Test Deployment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if minikube is installed
check_minikube() {
    if ! command -v minikube &> /dev/null; then
        print_error "Minikube is not installed. Please install minikube first."
        exit 1
    fi
    print_success "Minikube is installed"
}

# Start minikube cluster
start_minikube() {
    print_status "Starting minikube cluster..."
    
    # Check if cluster is already running
    if minikube status | grep -q "Running"; then
        print_warning "Minikube cluster is already running"
    else
        minikube start --cpus 4 --memory 8192 --disk-size 20g
        print_success "Minikube cluster started"
    fi
    
    # Enable addons
    minikube addons enable ingress
    minikube addons enable metrics-server
    print_success "Minikube addons enabled"
}

# Build and load Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Set docker environment to minikube
    eval $(minikube docker-env)
    
    # Build backend image
    print_status "Building backend image..."
    docker build -t ck-empire-backend:latest ./backend
    print_success "Backend image built"
    
    # Build frontend image
    print_status "Building frontend image..."
    docker build -t ck-empire-frontend:latest ./frontend
    print_success "Frontend image built"
    
    # Reset docker environment
    eval $(minikube docker-env -u)
}

# Create namespace and secrets
setup_namespace() {
    print_status "Setting up namespace and secrets..."
    
    # Create namespace
    kubectl create namespace ck-empire --dry-run=client -o yaml | kubectl apply -f -
    
    # Create secrets
    kubectl create secret generic ck-empire-secrets \
        --from-literal=ENCRYPTION_KEY="test-key-32-chars-long-here-test" \
        --from-literal=OPENAI_API_KEY="sk-test-openai-api-key" \
        --from-literal=STRIPE_SECRET_KEY="sk_test_stripe_secret_key" \
        --from-literal=JWT_SECRET_KEY="test-jwt-secret-key-32-chars-long" \
        --from-literal=POSTGRES_PASSWORD="password" \
        --from-literal=REDIS_PASSWORD="redispassword" \
        -n ck-empire --dry-run=client -o yaml | kubectl apply -f -
    
    print_success "Namespace and secrets created"
}

# Deploy database services
deploy_database() {
    print_status "Deploying database services..."
    
    # Deploy PostgreSQL
    kubectl apply -f deployment/k8s/db-service.yaml
    print_success "PostgreSQL deployed"
    
    # Deploy Redis
    kubectl apply -f deployment/k8s/redis-service.yaml
    print_success "Redis deployed"
    
    # Wait for database services to be ready
    print_status "Waiting for database services to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres-service -n ck-empire --timeout=300s
    kubectl wait --for=condition=ready pod -l app=redis-service -n ck-empire --timeout=300s
    print_success "Database services are ready"
}

# Deploy application services
deploy_application() {
    print_status "Deploying application services..."
    
    # Update image tags in deployment files
    sed 's|IMAGE_TAG|latest|g' deployment/k8s/backend-deployment.yaml | kubectl apply -f -
    sed 's|IMAGE_TAG|latest|g' deployment/k8s/frontend-deployment.yaml | kubectl apply -f -
    
    # Apply services
    kubectl apply -f deployment/k8s/backend-service.yaml
    kubectl apply -f deployment/k8s/frontend-service.yaml
    
    print_success "Application services deployed"
}

# Deploy ingress
deploy_ingress() {
    print_status "Deploying ingress..."
    
    # Apply ingress configuration
    kubectl apply -f deployment/k8s/ingress.yaml
    
    print_success "Ingress deployed"
}

# Deploy HPA
deploy_hpa() {
    print_status "Deploying Horizontal Pod Autoscalers..."
    
    kubectl apply -f deployment/k8s/hpa.yaml
    
    print_success "HPA deployed"
}

# Wait for all pods to be ready
wait_for_pods() {
    print_status "Waiting for all pods to be ready..."
    
    kubectl wait --for=condition=ready pod -l app=ck-empire-backend -n ck-empire --timeout=300s
    kubectl wait --for=condition=ready pod -l app=ck-empire-frontend -n ck-empire --timeout=300s
    
    print_success "All pods are ready"
}

# Get service URLs
get_service_urls() {
    print_status "Getting service URLs..."
    
    # Get minikube IP
    MINIKUBE_IP=$(minikube ip)
    
    # Get service ports
    BACKEND_PORT=$(kubectl get service backend-service -n ck-empire -o jsonpath='{.spec.ports[0].nodePort}')
    FRONTEND_PORT=$(kubectl get service frontend-service -n ck-empire -o jsonpath='{.spec.ports[0].nodePort}')
    
    echo ""
    echo "🌐 Service URLs:"
    echo "   Backend API:  http://$MINIKUBE_IP:$BACKEND_PORT"
    echo "   Frontend:     http://$MINIKUBE_IP:$FRONTEND_PORT"
    echo "   Minikube IP:  $MINIKUBE_IP"
    echo ""
}

# Test endpoints
test_endpoints() {
    print_status "Testing endpoints..."
    
    MINIKUBE_IP=$(minikube ip)
    BACKEND_PORT=$(kubectl get service backend-service -n ck-empire -o jsonpath='{.spec.ports[0].nodePort}')
    FRONTEND_PORT=$(kubectl get service frontend-service -n ck-empire -o jsonpath='{.spec.ports[0].nodePort}')
    
    # Test backend health
    print_status "Testing backend health endpoint..."
    if curl -f "http://$MINIKUBE_IP:$BACKEND_PORT/health" > /dev/null 2>&1; then
        print_success "Backend health check passed"
    else
        print_error "Backend health check failed"
    fi
    
    # Test frontend
    print_status "Testing frontend..."
    if curl -f "http://$MINIKUBE_IP:$FRONTEND_PORT/" > /dev/null 2>&1; then
        print_success "Frontend is accessible"
    else
        print_error "Frontend is not accessible"
    fi
}

# Show cluster status
show_status() {
    print_status "Cluster status:"
    echo ""
    kubectl get pods -n ck-empire
    echo ""
    kubectl get services -n ck-empire
    echo ""
    kubectl get ingress -n ck-empire
    echo ""
    kubectl get hpa -n ck-empire
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    
    # Delete namespace (this will delete all resources)
    kubectl delete namespace ck-empire --ignore-not-found=true
    
    print_success "Cleanup completed"
}

# Main deployment function
deploy() {
    print_status "Starting deployment process..."
    
    check_minikube
    start_minikube
    build_images
    setup_namespace
    deploy_database
    deploy_application
    deploy_ingress
    deploy_hpa
    wait_for_pods
    get_service_urls
    test_endpoints
    show_status
    
    print_success "🎉 Deployment completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Access the application using the URLs above"
    echo "   2. Check logs: kubectl logs -f deployment/ck-empire-backend -n ck-empire"
    echo "   3. Monitor resources: kubectl top pods -n ck-empire"
    echo "   4. Clean up: ./scripts/test_minikube_deploy.sh cleanup"
    echo ""
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "cleanup")
        cleanup
        ;;
    "status")
        show_status
        ;;
    "test")
        test_endpoints
        ;;
    *)
        echo "Usage: $0 {deploy|cleanup|status|test}"
        echo "  deploy  - Deploy the application to minikube"
        echo "  cleanup - Clean up all resources"
        echo "  status  - Show cluster status"
        echo "  test    - Test endpoints"
        exit 1
        ;;
esac 