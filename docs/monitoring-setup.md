# CK Empire Builder - Monitoring Setup Guide

Bu dokümantasyon, CK Empire Builder projesi için kapsamlı monitoring sisteminin kurulumunu açıklar.

## 📊 Monitoring Bileşenleri

### 1. Prometheus + Grafana
- **Prometheus**: Metrik toplama ve depolama
- **Grafana**: Metrik görselleştirme ve dashboard'lar
- **Alertmanager**: Alert yönetimi

### 2. ELK Stack (Elasticsearch, Logstash, Kibana)
- **Elasticsearch**: Log depolama ve arama
- **Logstash**: Log işleme ve filtreleme
- **Kibana**: Log görselleştirme ve analiz

### 3. Sentry
- Error tracking ve performance monitoring
- Real-time error reporting

### 4. Health Checks
- `/health` endpoint'i
- Dependency monitoring
- Service status tracking

## 🚀 Kurulum Adımları

### Adım 1: Environment Variables

```bash
# Backend dizininde .env dosyası oluşturun
cp env.monitoring.example .env

# Gerekli değerleri güncelleyin
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
```

### Adım 2: Monitoring Stack'i Başlatın

```bash
# Monitoring stack'i başlatın
cd deployment
docker-compose -f docker-compose.monitoring.yml up -d

# Ana uygulamayı başlatın
docker-compose up -d
```

### Adım 3: Backend'i Başlatın

```bash
# Backend dizininde
pip install -r requirements.txt
python main.py
```

## 📈 Monitoring Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "cloud_enabled": true,
  "monitoring": {
    "status": "healthy",
    "components": {
      "prometheus": "healthy",
      "sentry": "healthy",
      "elasticsearch": "healthy"
    }
  }
}
```

### Metrics Endpoint
```bash
curl http://localhost:8000/metrics
```

### Prometheus Metrics
```bash
curl http://localhost:8000/metrics
```

## 🎯 Dashboard'lar

### Grafana Dashboard'ları
1. **CK Empire Overview**: Genel sistem durumu
2. **Business Metrics**: Gelir ve proje metrikleri
3. **AI Service Monitoring**: AI servis performansı
4. **Error Tracking**: Hata oranları ve türleri
5. **Infrastructure**: Sistem kaynakları

### Kibana Dashboard'ları
1. **Application Logs**: Uygulama logları
2. **Error Analysis**: Hata analizi
3. **Performance Monitoring**: Performans metrikleri
4. **User Activity**: Kullanıcı aktiviteleri

## 🔔 Alerting Kuralları

### Critical Alerts
- **High Error Rate**: %10'dan fazla hata oranı
- **Service Down**: Servis çökmesi
- **Database Connection Issues**: Veritabanı bağlantı sorunları
- **Cloud Backup Failures**: Cloud backup hataları
- **Disk Space Low**: Disk alanı %10'un altında

### Warning Alerts
- **High Response Time**: 2 saniyeden fazla yanıt süresi
- **High CPU Usage**: %80'den fazla CPU kullanımı
- **High Memory Usage**: %85'den fazla bellek kullanımı
- **Revenue Drop**: Gelir düşüşü
- **AI Service Errors**: AI servis hataları

## 🧪 Test Senaryoları

### Monitoring Test'i Çalıştırın

```bash
# Backend dizininde
python test_monitoring.py
```

Bu script şunları test eder:
- HTTP request metrics
- AI request tracking
- Ethics check monitoring
- Business metrics
- Cloud backup tracking
- Error generation (Sentry)
- Timing measurements
- Event logging

### Manuel Test

```bash
# Health check
curl http://localhost:8000/health

# Metrics
curl http://localhost:8000/metrics

# Error generation
curl -X POST http://localhost:8000/api/v1/test/error
```

## 📊 Monitoring URL'leri

### Development
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Kibana**: http://localhost:5601
- **Alertmanager**: http://localhost:9093
- **cAdvisor**: http://localhost:8080
- **Node Exporter**: http://localhost:9100

### Production
- **Prometheus**: https://prometheus.ckempire.com
- **Grafana**: https://grafana.ckempire.com
- **Kibana**: https://kibana.ckempire.com
- **Sentry**: https://sentry.io

## 🔧 Konfigürasyon

### Prometheus Alert Rules
`deployment/prometheus/alerts.yml` dosyasında alert kuralları tanımlanmıştır.

### Alertmanager
`deployment/alertmanager/alertmanager.yml` dosyasında alert yönetimi konfigürasyonu bulunur.

### Logstash Pipeline
`deployment/logstash/pipeline/` dizininde log işleme pipeline'ları tanımlanmıştır.

## 📈 Key Metrics

### Business Metrics
- `projects_total`: Toplam proje sayısı
- `revenue_total`: Toplam gelir
- `ai_requests_total`: AI istek sayısı
- `ethics_checks_total`: Ethics kontrol sayısı

### System Metrics
- `http_requests_total`: HTTP istek sayısı
- `http_request_duration_seconds`: Yanıt süreleri
- `errors_total`: Hata sayısı
- `database_connections`: Veritabanı bağlantıları

### Cloud Metrics
- `cloud_backups_total`: Cloud backup sayısı
- `cloud_storage_usage`: Cloud storage kullanımı

## 🐛 Troubleshooting

### Prometheus Bağlantı Sorunu
```bash
# Prometheus container'ını kontrol edin
docker logs prometheus

# Config dosyasını kontrol edin
docker exec -it prometheus cat /etc/prometheus/prometheus.yml
```

### Elasticsearch Bağlantı Sorunu
```bash
# Elasticsearch durumunu kontrol edin
curl http://localhost:9200/_cluster/health

# Container loglarını kontrol edin
docker logs elasticsearch
```

### Sentry Entegrasyon Sorunu
```bash
# Environment variable'ları kontrol edin
echo $SENTRY_DSN

# Test error'ı generate edin
python test_monitoring.py
```

## 📚 Ek Kaynaklar

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [ELK Stack Documentation](https://www.elastic.co/guide/)
- [Sentry Documentation](https://docs.sentry.io/)

## 🚀 Production Deployment

### Kubernetes
```bash
# Monitoring namespace'i oluşturun
kubectl apply -f deployment/k8s/monitoring/

# Prometheus operator'ı kurun
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/kube-prometheus/main/manifests/setup/0-namespace.yaml
```

### Docker Swarm
```bash
# Stack'i deploy edin
docker stack deploy -c docker-compose.monitoring.yml monitoring
```

## 📞 Support

Monitoring sistemi ile ilgili sorunlar için:
- **GitHub Issues**: https://github.com/ckempire/ck-empire-builder/issues
- **Email**: monitoring@ckempire.com
- **Slack**: #monitoring channel 