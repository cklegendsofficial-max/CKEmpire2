# Advanced CK Empire Builder 🏛️

**Dijital İmparatorluk Yönetimi Aracı**

Advanced CK Empire Builder, modern teknolojilerle güçlendirilmiş kapsamlı bir dijital imparatorluk yönetimi platformudur. Bu proje, gelişmiş veritabanı yönetimi, AI entegrasyonları, video üretimi, NFT otomasyonu ve etik modülleri ile birlikte tam özellikli bir yönetim sistemi sunar.

## 🚀 Özellikler

### 🔧 Teknik Özellikler
- **Mikroservis Mimarisi**: FastAPI tabanlı modüler yapı
- **Gelişmiş Veritabanı**: PostgreSQL ve SQLite desteği
- **Güvenlik**: End-to-end şifreleme ve güvenlik protokolleri
- **AI Entegrasyonu**: OpenAI API entegrasyonu
- **Video Üretimi**: Otomatik video içerik üretimi
- **NFT Otomasyonu**: Blockchain tabanlı NFT yönetimi
- **Etik Modülü**: AI destekli etik karar verme sistemi

### 📊 Dashboard Özellikleri
- **React Tabanlı UI**: Modern ve responsive dashboard
- **Gerçek Zamanlı Veriler**: Canlı veri görselleştirme
- **Gelişmiş Grafikler**: Recharts ile interaktif grafikler
- **Kullanıcı Yönetimi**: Rol tabanlı erişim kontrolü

## 🏗️ Mimari

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React Dashboard]
        B[User Interface]
        C[Real-time Updates]
    end
    
    subgraph "API Gateway"
        D[FastAPI Gateway]
        E[Authentication]
        F[Rate Limiting]
    end
    
    subgraph "Microservices"
        G[Database Service]
        H[AI Service]
        I[Ethics Service]
        J[Video Service]
        K[NFT Service]
    end
    
    subgraph "External APIs"
        L[OpenAI API]
        M[Blockchain APIs]
        N[Video APIs]
    end
    
    subgraph "Data Layer"
        O[PostgreSQL]
        P[Redis Cache]
        Q[File Storage]
    end
    
    A --> D
    B --> D
    C --> D
    D --> G
    D --> H
    D --> I
    D --> J
    D --> K
    H --> L
    K --> M
    J --> N
    G --> O
    G --> P
    J --> Q
```

## 📁 Proje Yapısı

```
CKEmpire/
├── backend/                 # FastAPI mikroservisler
│   ├── db_service/         # Veritabanı yönetimi
│   ├── ethics_service/     # Etik modülü
│   ├── ai_service/         # AI entegrasyonları
│   ├── video_service/      # Video üretimi
│   └── nft_service/        # NFT otomasyonu
├── frontend/               # React uygulaması
├── deployment/             # Docker ve Kubernetes
├── docs/                   # Sphinx dokümantasyonu
└── tests/                  # Pytest testleri
```

## 🛠️ Kurulum

### Gereksinimler
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Docker & Docker Compose

### Backend Kurulumu

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Kurulumu

```bash
cd frontend
npm install
npm start
```

### Docker ile Kurulum

```bash
docker-compose up -d
```

## 🔧 Konfigürasyon

### Çevre Değişkenleri

```bash
# .env dosyası oluşturun
DATABASE_URL=postgresql://user:password@localhost:5432/ckempire
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key
REDIS_URL=redis://localhost:6379
```

## 🧪 Test

```bash
# Backend testleri
cd backend
pytest

# Frontend testleri
cd frontend
npm test
```

## 📚 API Dokümantasyonu

API dokümantasyonu FastAPI otomatik olarak oluşturulur:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🆘 Destek

- 📧 Email: support@ckempire.com
- 💬 Discord: [CK Empire Community](https://discord.gg/ckempire)
- 📖 Dokümantasyon: [docs.ckempire.com](https://docs.ckempire.com)

---

**Advanced CK Empire Builder** - Dijital İmparatorlukların Geleceği 🏛️✨ 