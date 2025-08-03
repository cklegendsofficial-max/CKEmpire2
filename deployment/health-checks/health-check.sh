#!/bin/bash

# CKEmpire Health Check Script
# This script performs comprehensive health checks on all components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE=${NAMESPACE:-"ckempire"}
MONITORING_NAMESPACE=${MONITORING_NAMESPACE:-"monitoring"}
TIMEOUT=${TIMEOUT:-30}
RETRY_COUNT=${RETRY_COUNT:-3}

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed or not in PATH"
        exit 1
    fi
    success "kubectl is available"
}

# Check cluster connectivity
check_cluster() {
    log "Checking cluster connectivity..."
    if kubectl cluster-info &> /dev/null; then
        success "Cluster is accessible"
    else
        error "Cannot connect to cluster"
        exit 1
    fi
}

# Check namespace exists
check_namespace() {
    log "Checking namespace: $NAMESPACE"
    if kubectl get namespace $NAMESPACE &> /dev/null; then
        success "Namespace $NAMESPACE exists"
    else
        error "Namespace $NAMESPACE does not exist"
        exit 1
    fi
}

# Check pod status
check_pods() {
    log "Checking pod status in namespace: $NAMESPACE"
    
    # Get all pods in the namespace
    pods=$(kubectl get pods -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}')
    
    if [ -z "$pods" ]; then
        error "No pods found in namespace $NAMESPACE"
        return 1
    fi
    
    all_healthy=true
    
    for pod in $pods; do
        status=$(kubectl get pod $pod -n $NAMESPACE -o jsonpath='{.status.phase}')
        ready=$(kubectl get pod $pod -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
        
        if [ "$status" = "Running" ] && [ "$ready" = "True" ]; then
            success "Pod $pod is Running and Ready"
        else
            error "Pod $pod is not healthy (Status: $status, Ready: $ready)"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = false ]; then
        return 1
    fi
}

# Check service endpoints
check_services() {
    log "Checking service endpoints..."
    
    services=$(kubectl get services -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}')
    
    for service in $services; do
        endpoints=$(kubectl get endpoints $service -n $NAMESPACE -o jsonpath='{.subsets[*].addresses[*].ip}')
        
        if [ -n "$endpoints" ]; then
            success "Service $service has endpoints: $endpoints"
        else
            warning "Service $service has no endpoints"
        fi
    done
}

# Check deployment status
check_deployments() {
    log "Checking deployment status..."
    
    deployments=$(kubectl get deployments -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}')
    
    for deployment in $deployments; do
        available=$(kubectl get deployment $deployment -n $NAMESPACE -o jsonpath='{.status.availableReplicas}')
        desired=$(kubectl get deployment $deployment -n $NAMESPACE -o jsonpath='{.spec.replicas}')
        
        if [ "$available" = "$desired" ]; then
            success "Deployment $deployment is fully available ($available/$desired)"
        else
            error "Deployment $deployment is not fully available ($available/$desired)"
        fi
    done
}

# Check ingress status
check_ingress() {
    log "Checking ingress status..."
    
    ingresses=$(kubectl get ingress -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}')
    
    for ingress in $ingresses; do
        address=$(kubectl get ingress $ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
        
        if [ -n "$address" ]; then
            success "Ingress $ingress has address: $address"
        else
            warning "Ingress $ingress has no address"
        fi
    done
}

# Check application health endpoints
check_health_endpoints() {
    log "Checking application health endpoints..."
    
    # Get backend service
    backend_service=$(kubectl get svc -n $NAMESPACE -l app=ckempire-backend -o jsonpath='{.items[0].metadata.name}')
    
    if [ -n "$backend_service" ]; then
        # Port forward to backend service
        kubectl port-forward -n $NAMESPACE svc/$backend_service 8000:8000 &
        PF_PID=$!
        
        # Wait for port forward to be ready
        sleep 5
        
        # Check health endpoint
        if curl -f http://localhost:8000/health &> /dev/null; then
            success "Backend health endpoint is responding"
        else
            error "Backend health endpoint is not responding"
        fi
        
        # Kill port forward
        kill $PF_PID 2>/dev/null || true
    else
        warning "Backend service not found"
    fi
}

# Check monitoring stack
check_monitoring() {
    log "Checking monitoring stack..."
    
    # Check Prometheus
    if kubectl get pods -n $MONITORING_NAMESPACE -l app=prometheus &> /dev/null; then
        prometheus_pods=$(kubectl get pods -n $MONITORING_NAMESPACE -l app=prometheus -o jsonpath='{.items[*].status.phase}')
        if echo "$prometheus_pods" | grep -q "Running"; then
            success "Prometheus is running"
        else
            warning "Prometheus is not running properly"
        fi
    else
        warning "Prometheus not found"
    fi
    
    # Check Grafana
    if kubectl get pods -n $MONITORING_NAMESPACE -l app=grafana &> /dev/null; then
        grafana_pods=$(kubectl get pods -n $MONITORING_NAMESPACE -l app=grafana -o jsonpath='{.items[*].status.phase}')
        if echo "$grafana_pods" | grep -q "Running"; then
            success "Grafana is running"
        else
            warning "Grafana is not running properly"
        fi
    else
        warning "Grafana not found"
    fi
    
    # Check Alertmanager
    if kubectl get pods -n $MONITORING_NAMESPACE -l app=alertmanager &> /dev/null; then
        alertmanager_pods=$(kubectl get pods -n $MONITORING_NAMESPACE -l app=alertmanager -o jsonpath='{.items[*].status.phase}')
        if echo "$alertmanager_pods" | grep -q "Running"; then
            success "Alertmanager is running"
        else
            warning "Alertmanager is not running properly"
        fi
    else
        warning "Alertmanager not found"
    fi
}

# Check Sentry
check_sentry() {
    log "Checking Sentry..."
    
    if kubectl get pods -n $MONITORING_NAMESPACE -l app=sentry &> /dev/null; then
        sentry_pods=$(kubectl get pods -n $MONITORING_NAMESPACE -l app=sentry -o jsonpath='{.items[*].status.phase}')
        if echo "$sentry_pods" | grep -q "Running"; then
            success "Sentry is running"
        else
            warning "Sentry is not running properly"
        fi
    else
        warning "Sentry not found"
    fi
}

# Check database connectivity
check_database() {
    log "Checking database connectivity..."
    
    # Check PostgreSQL
    if kubectl get pods -n $NAMESPACE -l app=postgresql &> /dev/null; then
        postgres_pods=$(kubectl get pods -n $NAMESPACE -l app=postgresql -o jsonpath='{.items[*].status.phase}')
        if echo "$postgres_pods" | grep -q "Running"; then
            success "PostgreSQL is running"
        else
            warning "PostgreSQL is not running properly"
        fi
    else
        warning "PostgreSQL not found"
    fi
    
    # Check Redis
    if kubectl get pods -n $NAMESPACE -l app=redis &> /dev/null; then
        redis_pods=$(kubectl get pods -n $NAMESPACE -l app=redis -o jsonpath='{.items[*].status.phase}')
        if echo "$redis_pods" | grep -q "Running"; then
            success "Redis is running"
        else
            warning "Redis is not running properly"
        fi
    else
        warning "Redis not found"
    fi
}

# Check resource usage
check_resources() {
    log "Checking resource usage..."
    
    # Check CPU and memory usage
    kubectl top pods -n $NAMESPACE 2>/dev/null || warning "Cannot get resource usage (metrics-server may not be installed)"
    
    # Check persistent volumes
    pvs=$(kubectl get pv -o jsonpath='{.items[*].status.phase}')
    for pv in $pvs; do
        if [ "$pv" = "Bound" ]; then
            success "Persistent volume is bound"
        else
            warning "Persistent volume is not bound (Status: $pv)"
        fi
    done
}

# Check network policies
check_network_policies() {
    log "Checking network policies..."
    
    policies=$(kubectl get networkpolicies -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
    
    if [ -n "$policies" ]; then
        success "Network policies are configured"
    else
        warning "No network policies found"
    fi
}

# Check secrets
check_secrets() {
    log "Checking secrets..."
    
    secrets=$(kubectl get secrets -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}')
    
    for secret in $secrets; do
        if kubectl get secret $secret -n $NAMESPACE &> /dev/null; then
            success "Secret $secret exists"
        else
            warning "Secret $secret is missing or inaccessible"
        fi
    done
}

# Check configmaps
check_configmaps() {
    log "Checking configmaps..."
    
    configmaps=$(kubectl get configmaps -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}')
    
    for configmap in $configmaps; do
        if kubectl get configmap $configmap -n $NAMESPACE &> /dev/null; then
            success "ConfigMap $configmap exists"
        else
            warning "ConfigMap $configmap is missing or inaccessible"
        fi
    done
}

# Check horizontal pod autoscalers
check_hpa() {
    log "Checking horizontal pod autoscalers..."
    
    hpas=$(kubectl get hpa -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
    
    for hpa in $hpas; do
        current=$(kubectl get hpa $hpa -n $NAMESPACE -o jsonpath='{.status.currentReplicas}')
        desired=$(kubectl get hpa $hpa -n $NAMESPACE -o jsonpath='{.status.desiredReplicas}')
        
        if [ "$current" = "$desired" ]; then
            success "HPA $hpa is at desired replicas ($current)"
        else
            warning "HPA $hpa is not at desired replicas (Current: $current, Desired: $desired)"
        fi
    done
}

# Check certificate status
check_certificates() {
    log "Checking certificates..."
    
    if kubectl get crd certificates.cert-manager.io &> /dev/null; then
        certificates=$(kubectl get certificates -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
        
        for cert in $certificates; do
            status=$(kubectl get certificate $cert -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
            
            if [ "$status" = "True" ]; then
                success "Certificate $cert is ready"
            else
                warning "Certificate $cert is not ready (Status: $status)"
            fi
        done
    else
        warning "cert-manager not installed"
    fi
}

# Main health check function
main() {
    log "Starting CKEmpire health checks..."
    
    # Basic checks
    check_kubectl
    check_cluster
    check_namespace
    
    # Application checks
    check_pods
    check_services
    check_deployments
    check_ingress
    check_health_endpoints
    
    # Infrastructure checks
    check_database
    check_resources
    check_secrets
    check_configmaps
    
    # Monitoring checks
    check_monitoring
    check_sentry
    
    # Security checks
    check_network_policies
    check_certificates
    
    # Scaling checks
    check_hpa
    
    log "Health checks completed!"
}

# Run main function
main "$@" 