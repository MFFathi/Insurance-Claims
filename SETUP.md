# Insurance Claims System Setup Guide

This guide provides detailed instructions for setting up the Insurance Claims Processing System, including development, testing, and production environments.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Development Setup](#development-setup)
3. [Database Setup](#database-setup)
4. [ML Model Setup](#ml-model-setup)
5. [Testing Setup](#testing-setup)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware Requirements
- Minimum 4GB RAM
- 10GB free disk space
- Multi-core processor

### Software Requirements
- Python 3.8 or higher
- PostgreSQL 12 or higher
- Docker and Docker Compose
- Git
- Virtual Environment (venv or conda)

## Development Setup

### 1. Clone the Repository
```bash
git clone [repository-url]
cd Insurance-Claims
```

### 2. Create and Activate Virtual Environment

#### Using venv (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Unix/MacOS
source venv/bin/activate
```

#### Using conda
```bash
conda create -n insurance-claims python=3.8
conda activate insurance-claims
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root with the following variables:
```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DATABASE_URL=postgres://user:password@localhost:5432/insurance_claims

# ML Model Settings
ML_MODEL_PATH=./MLModel/
MODEL_VERSION=0.4

# Email Settings (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

### 5. Database Setup

#### Local PostgreSQL Setup
1. Install PostgreSQL
2. Create database and user:
```sql
CREATE DATABASE insurance_claims;
CREATE USER insurance_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE insurance_claims TO insurance_user;
```

#### Using Docker
```bash
docker-compose up -d postgres
```

### 6. Run Migrations
```bash
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```

## ML Model Setup

### 1. Model Directory Setup
```bash
mkdir -p MLModel/
```

### 2. Model Training (Optional)
```bash
python manage.py train_models
```

### 3. Model Verification
```bash
python manage.py verify_models
```

## Testing Setup

### 1. Install Test Dependencies
```bash
pip install -r requirements-test.txt
```

### 2. Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=InsuranceClaimsML
```

## Production Deployment

### 1. Environment Preparation
- Set `DEBUG=False`
- Configure proper `ALLOWED_HOSTS`
- Set up SSL certificates
- Configure production database

### 2. Static Files Collection
```bash
python manage.py collectstatic
```

### 3. Using Docker Compose
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check database credentials
   - Ensure database exists and user has permissions

2. **ML Model Loading Issues**
   - Verify model files exist in correct directory
   - Check model version compatibility
   - Ensure required ML dependencies are installed

3. **Static Files Not Loading**
   - Run `collectstatic` command
   - Check static files directory permissions
   - Verify Nginx configuration

4. **Docker Issues**
   - Check Docker service status
   - Verify container logs
   - Ensure ports are not in use

### Getting Help

For additional support:
1. Check the project's issue tracker
2. Review the documentation
3. Contact the development team

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [scikit-learn Documentation](https://scikit-learn.org/stable/documentation.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/) 