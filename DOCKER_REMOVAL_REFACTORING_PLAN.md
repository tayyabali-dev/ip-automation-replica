# Docker Removal and Cloud-Native Refactoring Plan

## Overview
This document outlines the complete refactoring plan to remove Docker dependencies and transition to a cloud-native architecture with external managed services for MongoDB and Redis (Upstash).

## Current State Analysis
✅ **Already Cloud-Native Ready:**
- No Docker files found in the project
- FastAPI backend with environment-based configuration
- Next.js frontend with environment variables
- 3-terminal setup already documented in README
- Requirements.txt includes gunicorn, redis, and celery

## Required Changes

### 1. Backend Configuration Updates

#### A. Update `backend/app/core/config.py`
**Current Issue:** Uses individual `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB` variables
**Required Change:** Switch to single `REDIS_URL` environment variable for Upstash compatibility

```python
# REPLACE the Redis Configuration section (lines 22-26):
# OLD:
# REDIS_HOST: str = "localhost"
# REDIS_PORT: int = 6379
# REDIS_DB: int = 0

# NEW:
REDIS_URL: str = "redis://localhost:6379/0"  # Default for local development
```

**Update Celery properties (lines 66-72):**
```python
# OLD:
@property
def CELERY_BROKER_URL(self) -> str:
    return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

@property
def CELERY_RESULT_BACKEND(self) -> str:
    return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

# NEW:
@property
def CELERY_BROKER_URL(self) -> str:
    return self.REDIS_URL

@property
def CELERY_RESULT_BACKEND(self) -> str:
    return self.REDIS_URL
```

#### B. Update `backend/app/core/celery_app.py`
**Add SSL support for Upstash Redis:**

```python
# ADD after line 4:
import ssl
from urllib.parse import urlparse

# UPDATE celery_app configuration (lines 6-17):
# Parse Redis URL to determine if SSL is needed
redis_url = settings.REDIS_URL
parsed_url = urlparse(redis_url)
use_ssl = parsed_url.scheme == 'rediss'

# Configure broker with SSL support if needed
broker_transport_options = {}
if use_ssl:
    broker_transport_options = {
        'ssl_cert_reqs': ssl.CERT_NONE,
        'ssl_ca_certs': None,
        'ssl_certfile': None,
        'ssl_keyfile': None,
    }

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_transport_options=broker_transport_options,
    redis_backend_use_ssl=broker_transport_options if use_ssl else {},
    # Add compatibility settings for Python 3.14
    worker_pool="solo",  # Use solo pool for Windows compatibility
    worker_concurrency=1,  # Single worker process
    task_always_eager=False,  # Ensure tasks run asynchronously
    task_eager_propagates=True,  # Propagate exceptions in eager mode
)
```

### 2. Environment Configuration Updates

#### A. Update `backend/.env.example`
```env
# Database Configuration
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority
SECRET_KEY=your_secret_key_here_generate_with_openssl_rand_hex_32

# Redis Configuration (Upstash or local)
REDIS_URL=redis://localhost:6379/0
# For Upstash Redis with SSL:
# REDIS_URL=rediss://default:password@host:port

# Frontend Configuration
FRONTEND_URL=http://localhost:3000

# Google Cloud Storage (Service Account JSON content)
GOOGLE_APPLICATION_CREDENTIALS_JSON='{...}'
GCP_BUCKET_NAME=jwhd-ip-automation

# Gemini
GOOGLE_API_KEY=your_google_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp
```

#### B. Update `frontend/.env.example`
```env
# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# For production deployment:
# NEXT_PUBLIC_API_URL=https://your-backend-domain.com/api/v1

# Environment Configuration
NODE_ENV=development

# Optional: Additional frontend configuration
NEXT_PUBLIC_APP_NAME=JWHD IP Automation
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### 3. Requirements Verification

#### Check `backend/requirements.txt`
✅ **Already includes required packages:**
- `gunicorn>=0.27.1` ✅
- `celery>=5.3.6` ✅
- `redis>=5.0.1` ✅

### 4. Frontend Package.json Verification

#### Check `frontend/package.json`
✅ **Already has correct scripts:**
- `"dev": "next dev"` ✅
- `"build": "next build"` ✅
- `"start": "next start"` ✅

### 5. Documentation Updates

#### Update `README.md`
**Current Status:** Already shows 3-terminal setup without Docker
**Required:** Enhance with specific Upstash Redis configuration and cloud deployment notes

## 3-Terminal Local Development Setup

### Terminal 1: Backend API
```bash
cd backend
pip install -r requirements.txt
# For development:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# For production:
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Terminal 2: Celery Worker
```bash
cd backend
celery -A app.core.celery_app worker --loglevel=info
```

### Terminal 3: Frontend
```bash
cd frontend
npm install
# For development:
npm run dev
# For production:
npm run build && npm start
```

## Upstash Redis Configuration

### Redis URL Format
```bash
# Local Redis (development)
REDIS_URL=redis://localhost:6379/0

# Upstash Redis (production)
REDIS_URL=rediss://default:AaphAAIncDJiN2MxYzMzNmI0NDE0OWIxOTRiZmJlOTA3OWVmOTQ0ZXAyNDM2MTc@crack-doe-43617.upstash.io:6379
```

### SSL Configuration
The Celery configuration automatically detects `rediss://` URLs and applies SSL settings:
- `ssl_cert_reqs=ssl.CERT_NONE` - Disables certificate verification for Upstash
- Handles SSL handshake properly for cloud Redis services

## Deployment Architecture

```mermaid
graph TB
    subgraph "Cloud Infrastructure"
        FE[Frontend Server<br/>Next.js]
        BE[Backend Server<br/>FastAPI]
        CW[Celery Worker<br/>Background Tasks]
        
        subgraph "Managed Services"
            DB[(MongoDB Atlas)]
            RD[(Upstash Redis)]
            GCS[Google Cloud Storage]
        end
    end
    
    FE --> BE
    BE --> DB
    BE --> RD
    CW --> RD
    BE --> GCS
    CW --> GCS
```

## Environment Variables Summary

### Backend (.env)
- `MONGO_URI` - MongoDB connection string
- `REDIS_URL` - Redis connection URL (supports SSL)
- `SECRET_KEY` - JWT secret key
- `GOOGLE_API_KEY` - Gemini API key
- `GCP_*` - Google Cloud Storage credentials

### Frontend (.env)
- `NEXT_PUBLIC_API_URL` - Backend API endpoint
- `NODE_ENV` - Environment (development/production)

## Testing the Configuration

### 1. Test Redis Connection
```python
# Test script to verify Redis SSL connection
import redis
from urllib.parse import urlparse

redis_url = "rediss://default:password@host:port"
parsed = urlparse(redis_url)

if parsed.scheme == 'rediss':
    r = redis.Redis.from_url(redis_url, ssl_cert_reqs=None)
else:
    r = redis.Redis.from_url(redis_url)

try:
    r.ping()
    print("Redis connection successful!")
except Exception as e:
    print(f"Redis connection failed: {e}")
```

### 2. Test Celery Worker
```bash
# Start worker and verify it connects to Redis
cd backend
celery -A app.core.celery_app worker --loglevel=debug
```

### 3. Test Full Pipeline
```bash
# Terminal 1: Start backend
cd backend && uvicorn app.main:app --reload

# Terminal 2: Start worker
cd backend && celery -A app.core.celery_app worker --loglevel=info

# Terminal 3: Start frontend
cd frontend && npm run dev
```

## Implementation Priority

1. ✅ **High Priority - Backend Redis Configuration**
   - Update config.py to use REDIS_URL
   - Add SSL support in celery_app.py
   
2. ✅ **High Priority - Environment Files**
   - Update .env.example files with new format
   
3. ✅ **Medium Priority - Documentation**
   - Update README with enhanced setup instructions
   
4. ✅ **Low Priority - Verification**
   - Test all configurations work properly

## Success Criteria

- ✅ No Docker dependencies remain
- ✅ Backend uses REDIS_URL environment variable
- ✅ SSL support for Upstash Redis works correctly
- ✅ 3-terminal setup runs without issues
- ✅ Environment examples are updated and accurate
- ✅ Documentation reflects cloud-native architecture