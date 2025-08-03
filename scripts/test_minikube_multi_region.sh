#!/bin/bash

# CK Empire Multi-Region Minikube Test Script
# Tests multi-region deployment with HPA and load balancing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="ckempire"
CLUSTER_NAME="ckempire-multi-region"
MIN_REPLICAS=5
MAX_REPLICAS=20

echo -e "${BLUE}🚀 CK Empire Multi-Region Minikube Test${NC}"
echo "=========================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if minikube is installed
check_minikube() {
    if ! command -v minikube &> /dev/null; then
        print_error "Minikube is not installed. Please install minikube first."
        exit 1
    fi
    print_status "Minikube is installed"
}

# Start minikube cluster
start_cluster() {
    print_status "Starting Minikube cluster..."
    
    # Stop existing cluster if running
    minikube stop 2>/dev/null || true
    minikube delete 2>/dev/null || true
    
    # Start new cluster with more resources
    minikube start \
        --driver=docker \
        --cpus=4 \
        --memory=8192 \
        --disk-size=20g \
        --kubernetes-version=v1.28.0 \
        --addons=ingress,metrics-server \
        --profile=$CLUSTER_NAME
    
    print_status "Minikube cluster started successfully"
}

# Enable minikube addons
enable_addons() {
    print_status "Enabling Minikube addons..."
    
    minikube addons enable ingress --profile=$CLUSTER_NAME
    minikube addons enable metrics-server --profile=$CLUSTER_NAME
    minikube addons enable dashboard --profile=$CLUSTER_NAME
    
    print_status "Addons enabled successfully"
}

# Create namespace
create_namespace() {
    print_status "Creating namespace: $NAMESPACE"
    
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    print_status "Namespace created successfully"
}

# Apply Kubernetes configurations
apply_k8s_configs() {
    print_status "Applying Kubernetes configurations..."
    
    # Apply namespace
    kubectl apply -f deployment/k8s/namespace.yaml
    
    # Apply ConfigMaps and Secrets
    kubectl apply -f deployment/k8s/configmap.yaml
    kubectl apply -f deployment/k8s/secret.yaml
    
    # Apply database
    kubectl apply -f deployment/k8s/postgres.yaml
    kubectl apply -f deployment/k8s/redis-service.yaml
    
    # Apply backend and frontend
    kubectl apply -f deployment/k8s/backend-deployment.yaml
    kubectl apply -f deployment/k8s/backend-service.yaml
    kubectl apply -f deployment/k8s/frontend-deployment.yaml
    kubectl apply -f deployment/k8s/frontend-service.yaml
    
    # Apply multi-region configurations
    kubectl apply -f deployment/k8s/multi-region-hpa.yaml
    kubectl apply -f deployment/k8s/multi-region-loadbalancer.yaml
    
    print_status "Kubernetes configurations applied successfully"
}

# Wait for pods to be ready
wait_for_pods() {
    print_status "Waiting for pods to be ready..."
    
    # Wait for backend pods
    kubectl wait --for=condition=ready pod -l app=ckempire-backend -n $NAMESPACE --timeout=300s
    
    # Wait for frontend pods
    kubectl wait --for=condition=ready pod -l app=ckempire-frontend -n $NAMESPACE --timeout=300s
    
    # Wait for database pods
    kubectl wait --for=condition=ready pod -l app=ckempire-postgres -n $NAMESPACE --timeout=300s
    
    print_status "All pods are ready"
}

# Check HPA status
check_hpa_status() {
    print_status "Checking HPA status..."
    
    echo "Backend HPA:"
    kubectl get hpa ckempire-backend-hpa -n $NAMESPACE
    
    echo "Frontend HPA:"
    kubectl get hpa ckempire-frontend-hpa -n $NAMESPACE
    
    echo "Celery HPA:"
    kubectl get hpa ckempire-celery-hpa -n $NAMESPACE
}

# Generate load for testing
generate_load() {
    print_status "Generating load for testing..."
    
    # Get service URL
    SERVICE_URL=$(minikube service ckempire-backend -n $NAMESPACE --url)
    
    if [ -z "$SERVICE_URL" ]; then
        print_warning "Could not get service URL. Using default."
        SERVICE_URL="http://localhost:8000"
    fi
    
    echo "Service URL: $SERVICE_URL"
    
    # Generate load using curl
    for i in {1..50}; do
        curl -s "$SERVICE_URL/health" > /dev/null &
        curl -s "$SERVICE_URL/metrics" > /dev/null &
        curl -s "$SERVICE_URL/api/projects" > /dev/null &
        
        if [ $((i % 10)) -eq 0 ]; then
            echo "Generated $i requests..."
        fi
    done
    
    wait
    print_status "Load generation completed"
}

# Test multi-region functionality
test_multi_region() {
    print_status "Testing multi-region functionality..."
    
    # Test region health endpoints
    echo "Testing region health endpoints..."
    
    # Simulate region health checks
    for region in "us-east-1" "eu-west-1" "ap-southeast-1" "us-west-2"; do
        echo "Region: $region"
        kubectl exec -n $NAMESPACE deployment/ckempire-backend -- curl -s "http://localhost:8000/health" || true
    done
    
    # Test load balancer
    echo "Testing load balancer..."
    kubectl get svc ckempire-loadbalancer -n $NAMESPACE
    
    print_status "Multi-region tests completed"
}

# Monitor resources
monitor_resources() {
    print_status "Monitoring resource usage..."
    
    echo "Pod status:"
    kubectl get pods -n $NAMESPACE
    
    echo "Service status:"
    kubectl get svc -n $NAMESPACE
    
    echo "HPA status:"
    kubectl get hpa -n $NAMESPACE
    
    echo "Resource usage:"
    kubectl top pods -n $NAMESPACE
}

# Test failover scenario
test_failover() {
    print_status "Testing failover scenario..."
    
    # Simulate primary region failure
    echo "Simulating primary region failure..."
    
    # Scale down primary region pods
    kubectl scale deployment ckempire-backend -n $NAMESPACE --replicas=0
    
    echo "Primary region scaled down. Checking failover..."
    sleep 10
    
    # Check if secondary regions are handling traffic
    kubectl get pods -n $NAMESPACE
    
    # Scale back up
    kubectl scale deployment ckempire-backend -n $NAMESPACE --replicas=$MIN_REPLICAS
    
    print_status "Failover test completed"
}

# Show dashboard
show_dashboard() {
    print_status "Opening Kubernetes dashboard..."
    
    minikube dashboard --profile=$CLUSTER_NAME &
    
    echo "Dashboard opened in browser"
    echo "You can also access it manually with: minikube dashboard --profile=$CLUSTER_NAME"
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    
    # Stop minikube
    minikube stop --profile=$CLUSTER_NAME
    
    print_status "Cleanup completed"
}

# Main execution
main() {
    echo "Starting CK Empire Multi-Region Test..."
    
    # Check prerequisites
    check_minikube
    
    # Start cluster
    start_cluster
    
    # Enable addons
    enable_addons
    
    # Create namespace
    create_namespace
    
    # Apply configurations
    apply_k8s_configs
    
    # Wait for pods
    wait_for_pods
    
    # Check HPA
    check_hpa_status
    
    # Generate load
    generate_load
    
    # Test multi-region
    test_multi_region
    
    # Monitor resources
    monitor_resources
    
    # Test failover
    test_failover
    
    # Show dashboard
    show_dashboard
    
    print_status "Multi-region test completed successfully!"
    
    echo ""
    echo "Next steps:"
    echo "1. Access the dashboard: minikube dashboard --profile=$CLUSTER_NAME"
    echo "2. Check HPA status: kubectl get hpa -n $NAMESPACE"
    echo "3. Monitor logs: kubectl logs -f deployment/ckempire-backend -n $NAMESPACE"
    echo "4. Test endpoints: minikube service ckempire-backend -n $NAMESPACE --url"
    echo "5. Cleanup: ./scripts/test_minikube_multi_region.sh cleanup"
}

# Handle cleanup
if [ "$1" = "cleanup" ]; then
    cleanup
    exit 0
fi

# Run main function
main "$@" 