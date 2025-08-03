# CK Empire Deployment Guide

## Overview

This guide covers the complete deployment setup for CK Empire, including local development, production deployment on Kubernetes, and monitoring configuration.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Monitoring Setup](#monitoring-setup)
6. [SSL/HTTPS Configuration](#sslhttps-configuration)
7. [Scaling Configuration](#scaling-configuration)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

- Docker and Docker Compose
- Kubernetes cluster (EKS, GKE, or local)
- Helm 3.x
- kubectl
- AWS CLI (for EKS) or gcloud CLI (for GKE)
- Git

### System Requirements

- **Local Development**: 8GB RAM, 4 CPU cores
- **Production**: 16GB RAM, 8 CPU cores minimum
- **Storage**: 100GB minimum for production

## Local Development

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ckempire/ckempire.git
   cd ckempire
   ```

2. **Set up environment variables**:
   ```bash
   cp backend/env.example backend/.env
   cp deployment/env.example deployment/.env
   # Edit the .env files with your configuration
   ```

3. **Start the development stack**:
   ```bash
   cd deployment
   docker-compose up -d
   ```

4. **Run database migrations**:
   ```bash
   docker-compose exec backend python run_migrations.py
   ```

5. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Grafana: http://localhost:3001
   - Prometheus: http://localhost:9090

### Development Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Rebuild images
docker-compose build --no-cache

# Run tests
docker-compose exec backend python run_tests.py --all

# Access database
docker-compose exec postgres psql -U ckempire_user -d ckempire
```

## Production Deployment

### Docker Compose Production

1. **Create production environment**:
   ```bash
   cd deployment
   cp env.example .env.production
   # Edit .env.production with production values
   ```

2. **Start production stack**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

3. **Verify deployment**:
   ```bash
   docker-compose ps
   curl https://your-domain.com/health
   ```

### Environment Variables

Create a `.env.production` file with the following variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/ckempire
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_URL=redis://host:6379

# Security
SECRET_KEY=your-super-secret-key
OPENAI_API_KEY=your-openai-api-key

# Monitoring
SENTRY_DSN=your-sentry-dsn
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200

# Cloud Configuration
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
GOOGLE_CLOUD_PROJECT=your-gcp-project
```

## Kubernetes Deployment

### Prerequisites

1. **Install Helm**:
   ```bash
   curl https://get.helm.sh/helm-v3.12.0-linux-amd64.tar.gz | tar xz
   sudo mv linux-amd64/helm /usr/local/bin/
   ```

2. **Configure kubectl**:
   ```bash
   # For AWS EKS
   aws eks update-kubeconfig --name ckempire-cluster --region us-west-2
   
   # For GKE
   gcloud container clusters get-credentials ckempire-cluster --zone us-central1-a
   ```

### Deploy to Kubernetes

1. **Create namespace**:
   ```bash
   kubectl create namespace ckempire
   ```

2. **Create secrets**:
   ```bash
   kubectl create secret generic ckempire-secrets \
     --from-literal=database-url="postgresql://user:pass@host:5432/ckempire" \
     --from-literal=redis-url="redis://host:6379" \
     --from-literal=secret-key="your-secret-key" \
     --from-literal=openai-api-key="your-openai-key" \
     --from-literal=sentry-dsn="your-sentry-dsn" \
     -n ckempire
   ```

3. **Deploy with Helm**:
   ```bash
   cd deployment/helm
   helm upgrade --install ckempire . \
     --namespace ckempire \
     --set global.environment=production \
     --set backend.replicaCount=3 \
     --set frontend.replicaCount=2
   ```

4. **Verify deployment**:
   ```bash
   kubectl get pods -n ckempire
   kubectl get services -n ckempire
   kubectl get ingress -n ckempire
   ```

### Scaling Configuration

The deployment includes automatic scaling:

- **Backend**: 3-10 replicas based on CPU/Memory usage
- **Frontend**: 2-5 replicas based on CPU/Memory usage
- **Celery Workers**: 2-8 replicas based on CPU usage

To manually scale:
```bash
kubectl scale deployment ckempire-backend --replicas=5 -n ckempire
```

## Monitoring Setup

### Prometheus & Grafana

1. **Deploy monitoring stack**:
   ```bash
   kubectl create namespace monitoring
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
     --namespace monitoring \
     --set grafana.enabled=true
   ```

2. **Import dashboards**:
   ```bash
   kubectl apply -f deployment/monitoring/grafana-dashboards/ -n monitoring
   ```

3. **Access Grafana**:
   ```bash
   kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
   # Access at http://localhost:3000 (admin/admin)
   ```

### Alerting

Configure alerts in `deployment/prometheus/alerts.yml`:

```yaml
groups:
  - name: ckempire-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
```

## SSL/HTTPS Configuration

### Let's Encrypt Setup

1. **Install cert-manager**:
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml
   ```

2. **Create ClusterIssuer**:
   ```yaml
   apiVersion: cert-manager.io/v1
   kind: ClusterIssuer
   metadata:
     name: letsencrypt-prod
   spec:
     acme:
       server: https://acme-v02.api.letsencrypt.org/directory
       email: admin@ckempire.com
       privateKeySecretRef:
         name: letsencrypt-prod
       solvers:
       - http01:
           ingress:
             class: nginx
   ```

3. **Apply to cluster**:
   ```bash
   kubectl apply -f deployment/production/ssl/cluster-issuer.yaml
   ```

### SSL Configuration

The ingress automatically configures SSL:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - ckempire.com
    secretName: ckempire-tls
```

## CI/CD Pipeline

### GitHub Actions Setup

1. **Configure secrets** in GitHub repository:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `GCP_PROJECT_ID`
   - `GCP_SA_KEY`
   - `SLACK_WEBHOOK_URL`

2. **Pipeline triggers**:
   - Push to `main`: Deploy to production
   - Push to `develop`: Deploy to development
   - Pull requests: Run tests only

3. **Manual deployment**:
   ```bash
   # Create a release to trigger production deployment
   git tag v1.0.0
   git push origin v1.0.0
   ```

### Pipeline Stages

1. **Security Scan**: Bandit, Safety, Semgrep
2. **Testing**: Unit, Integration, E2E, Load tests
3. **Build**: Docker images
4. **Deploy**: Kubernetes deployment
5. **Monitoring**: Setup dashboards and alerts

## Troubleshooting

### Common Issues

1. **Database connection failed**:
   ```bash
   kubectl logs deployment/ckempire-backend -n ckempire
   kubectl exec -it deployment/ckempire-backend -n ckempire -- python -c "from database import get_db; print(get_db())"
   ```

2. **SSL certificate issues**:
   ```bash
   kubectl describe certificate -n ckempire
   kubectl logs -n cert-manager
   ```

3. **Scaling not working**:
   ```bash
   kubectl describe hpa -n ckempire
   kubectl top pods -n ckempire
   ```

4. **Monitoring not working**:
   ```bash
   kubectl get pods -n monitoring
   kubectl logs deployment/prometheus-server -n monitoring
   ```

### Health Checks

```bash
# Check application health
curl https://ckempire.com/health

# Check API health
curl https://api.ckempire.com/health

# Check metrics
curl https://api.ckempire.com/metrics

# Check database
kubectl exec -it deployment/ckempire-postgresql -n ckempire -- psql -U ckempire_user -d ckempire -c "SELECT 1;"
```

### Logs and Debugging

```bash
# View all logs
kubectl logs -f -l app=ckempire-backend -n ckempire

# View specific pod logs
kubectl logs -f deployment/ckempire-backend -n ckempire

# Access pod shell
kubectl exec -it deployment/ckempire-backend -n ckempire -- /bin/bash

# Check resource usage
kubectl top pods -n ckempire
kubectl describe pod -n ckempire
```

## Performance Optimization

### Resource Limits

```yaml
resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi
```

### Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_content_project_id ON content(project_id);
CREATE INDEX idx_revenue_project_id ON revenue(project_id);

-- Analyze tables
ANALYZE projects;
ANALYZE content;
ANALYZE revenue;
```

### Caching Strategy

- Redis for session storage
- Application-level caching
- CDN for static assets
- Database query caching

## Security Best Practices

1. **Network Policies**: Restrict pod-to-pod communication
2. **RBAC**: Use least privilege access
3. **Secrets Management**: Use Kubernetes secrets or external vault
4. **Image Security**: Scan images for vulnerabilities
5. **SSL/TLS**: Enforce HTTPS everywhere
6. **Rate Limiting**: Prevent abuse
7. **Monitoring**: Alert on security events

## Backup and Recovery

### Database Backup

```bash
# Create backup
kubectl exec -it deployment/ckempire-postgresql -n ckempire -- \
  pg_dump -U ckempire_user ckempire > backup.sql

# Restore backup
kubectl exec -i deployment/ckempire-postgresql -n ckempire -- \
  psql -U ckempire_user ckempire < backup.sql
```

### Automated Backups

```yaml
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: db-backup
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            command: ["pg_dump", "-h", "ckempire-postgresql", "-U", "ckempire_user", "ckempire"]
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: ckempire-secrets
                  key: postgres-password
```

## Support and Maintenance

### Regular Maintenance

1. **Update dependencies**: Monthly
2. **Security patches**: As needed
3. **Database maintenance**: Weekly
4. **Log rotation**: Daily
5. **Backup verification**: Weekly

### Monitoring Alerts

- High error rates
- Slow response times
- Resource exhaustion
- Security events
- Business metrics

### Contact Information

- **Technical Support**: support@ckempire.com
- **Security Issues**: security@ckempire.com
- **Documentation**: https://docs.ckempire.com 