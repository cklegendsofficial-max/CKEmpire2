# CK Empire Builder - Backend

Advanced Digital Empire Management Backend API

## 🚀 Overview

CK Empire Builder is a comprehensive digital empire management platform that provides:

- **Project Management**: Organize and track digital projects
- **Revenue Tracking**: Monitor income streams and financial metrics
- **AI Integration**: Advanced AI features for content generation
- **Ethics Monitoring**: Built-in ethical AI monitoring
- **Performance Analytics**: Real-time metrics and insights
- **Cloud Integration**: AWS/GCP integration with auto-scaling
- **Backup & Recovery**: Automated backup and disaster recovery

## 📁 Project Structure

```
backend/
├── config.py              # Central configuration management
├── utils.py               # Common utilities and helpers
├── exceptions.py          # Custom exceptions and handlers
├── main.py               # FastAPI application entry point
├── database.py           # Database models and operations
├── ai.py                 # AI module for content generation
├── ethics.py             # Ethics monitoring module
├── finance.py            # Financial analysis module
├── performance.py        # Performance monitoring
├── monitoring.py         # System monitoring
├── middleware/           # Custom middleware
│   └── common.py        # Common middleware functions
├── routers/             # API route handlers
│   ├── base.py          # Base router with common functionality
│   ├── auth.py          # Authentication routes
│   ├── projects.py      # Project management routes
│   ├── revenue.py       # Revenue tracking routes
│   ├── ai.py            # AI features routes
│   ├── ethics.py        # Ethics monitoring routes
│   ├── performance.py   # Performance routes
│   ├── cloud.py         # Cloud integration routes
│   └── ...              # Other route modules
├── tests/               # Test suite
│   └── conftest.py      # Test configuration and fixtures
└── requirements.txt      # Python dependencies
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- SQLite (or PostgreSQL/MySQL)
- Redis (optional, for caching)
- Docker (optional)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python -m alembic upgrade head
   ```

6. **Run the application**
   ```bash
   python main.py
   # Or with uvicorn
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## ⚙️ Configuration

The application uses a centralized configuration system in `config.py`. Key configuration options:

### Environment Variables

```bash
# Application
CK_ENVIRONMENT=development
CK_DEBUG=true
CK_HOST=0.0.0.0
CK_PORT=8000

# Database
CK_DATABASE_URL=sqlite:///./ckempire.db
CK_DATABASE_TYPE=sqlite

# Security
CK_SECRET_KEY=your-secret-key-here
CK_ALGORITHM=HS256
CK_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Configuration
CK_OPENAI_API_KEY=your-openai-api-key
CK_AI_MODEL=gpt-4
CK_AI_MAX_TOKENS=2000

# Cloud Configuration
CK_CLOUD_PROVIDER=none
CK_AWS_ACCESS_KEY_ID=your-aws-key
CK_AWS_SECRET_ACCESS_KEY=your-aws-secret

# Stripe Payments
CK_STRIPE_SECRET_KEY=your-stripe-secret
CK_STRIPE_PUBLISHABLE_KEY=your-stripe-publishable

# Redis
CK_REDIS_URL=redis://localhost:6379
```

### Configuration Classes

- `Settings`: Main application settings
- `Constants`: Application constants
- `Environment`: Environment types
- `DatabaseType`: Database types
- `CloudProvider`: Cloud providers

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - User logout

### Projects
- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Create new project
- `GET /api/v1/projects/{project_id}` - Get project details
- `PUT /api/v1/projects/{project_id}` - Update project
- `DELETE /api/v1/projects/{project_id}` - Delete project

### Revenue
- `GET /api/v1/revenue` - Get revenue analytics
- `POST /api/v1/revenue` - Add revenue entry
- `GET /api/v1/revenue/analytics` - Get revenue analytics
- `GET /api/v1/revenue/trends` - Get revenue trends

### AI Features
- `POST /api/v1/ai/ideas` - Generate AI ideas
- `POST /api/v1/ai/content` - Generate AI content
- `GET /api/v1/ai/agi-state` - Get AGI state
- `POST /api/v1/ai/analyze` - Analyze content with AI

### Ethics
- `POST /api/v1/ethics/check` - Check content ethics
- `GET /api/v1/ethics/reports` - Get ethics reports
- `POST /api/v1/ethics/flag` - Flag content for review

### Performance
- `GET /api/v1/performance/metrics` - Get performance metrics
- `GET /api/v1/performance/health` - Health check
- `GET /api/v1/performance/status` - System status

### Cloud
- `GET /api/v1/cloud/config` - Get cloud configuration
- `POST /api/v1/cloud/backup` - Create backup
- `GET /api/v1/cloud/backups` - List backups
- `POST /api/v1/cloud/restore` - Restore from backup

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control
- Session management
- Password hashing with bcrypt

### Data Protection
- End-to-end encryption for sensitive data
- Input validation and sanitization
- SQL injection prevention
- XSS protection

### Rate Limiting
- Per-user rate limiting
- Per-IP rate limiting
- Configurable limits

### Security Headers
- Content Security Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Strict-Transport-Security

## 📊 Monitoring & Logging

### Structured Logging
- JSON-formatted logs
- Request/response logging
- Error tracking
- Performance metrics

### Health Checks
- Database connectivity
- External service status
- System resources
- Custom health checks

### Metrics Collection
- Prometheus metrics
- Custom business metrics
- Performance monitoring
- Error tracking

## 🧪 Testing

### Test Structure
```
tests/
├── conftest.py          # Test configuration
├── test_auth.py         # Authentication tests
├── test_projects.py     # Project management tests
├── test_ai.py           # AI functionality tests
├── test_ethics.py       # Ethics monitoring tests
├── test_performance.py  # Performance tests
└── integration/         # Integration tests
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=backend

# Run integration tests
pytest tests/integration/

# Run performance tests
pytest -m performance
```

### Test Fixtures
- Database session management
- Authentication helpers
- Mock external services
- Sample data generators

## 🚀 Deployment

### Docker Deployment
```bash
# Build image
docker build -t ckempire-backend .

# Run container
docker run -p 8000:8000 ckempire-backend
```

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/ckempire
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: ckempire
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass

  redis:
    image: redis:6-alpine
```

### Kubernetes Deployment
```bash
# Apply Kubernetes manifests
kubectl apply -f deployment/k8s/

# Check deployment status
kubectl get pods -n ckempire
```

## 🔧 Development

### Code Style
- Follow PEP 8
- Use type hints
- Document all functions
- Write comprehensive tests

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Code Quality Tools
- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Bandit**: Security scanning
- **Safety**: Dependency scanning

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📈 Performance

### Optimization Features
- Database connection pooling
- Redis caching
- Query optimization
- Async/await patterns
- Background task processing

### Monitoring
- Response time tracking
- Error rate monitoring
- Resource usage tracking
- Custom business metrics

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database URL
   - Verify database is running
   - Check network connectivity

2. **Authentication Issues**
   - Verify JWT secret key
   - Check token expiration
   - Validate user credentials

3. **AI Service Errors**
   - Check OpenAI API key
   - Verify API quota
   - Check network connectivity

4. **Performance Issues**
   - Monitor database queries
   - Check Redis connectivity
   - Review log files

### Debug Mode
```bash
# Enable debug mode
export CK_DEBUG=true

# Run with debug logging
python main.py --debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Development Guidelines
- Write clear commit messages
- Follow the existing code style
- Add documentation for new features
- Include tests for new functionality
- Update this README if needed

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/ckempire/ck-empire-builder/issues)
- **Email**: support@ckempire.com

## 🔄 Changelog

### v1.0.0
- Initial release
- Core API functionality
- Authentication system
- AI integration
- Ethics monitoring
- Performance tracking
- Cloud integration
- Comprehensive testing suite 