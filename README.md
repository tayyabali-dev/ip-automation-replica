# JWHD IP Automation - ADS Auto-fill System

This project automates the extraction of inventor information from patent application cover sheets and generates USPTO Application Data Sheets (ADS).

## Project Structure

- `frontend/`: Next.js application (App Router)
- `backend/`: FastAPI application
- `worker/`: Celery worker for background processing (code located in `backend/`)

## Cloud-Native Architecture

The system uses a **4-service cloud-native architecture** with external managed services:

### Core Services
- **Frontend**: Next.js app (Port 3000)
- **Backend**: FastAPI app (Port 8000)
- **Worker**: Celery worker for document extraction
- **Redis**: Upstash Redis (managed service) for message broker and result backend

### External Managed Services
- **Database**: MongoDB Atlas
- **Storage**: Google Cloud Storage
- **Message Broker**: Upstash Redis with SSL support

## Local Development Setup (3-Terminal)

### Prerequisites
- Python 3.9+
- Node.js 18+
- Environment files configured (see `.env.example` files)

### Terminal 1: Backend API
```bash
cd backend
pip install -r requirements.txt

# Development mode (with auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
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

# Development mode
npm run dev

# Production mode
npm run build && npm start
```

## Environment Configuration

### Backend Environment (`backend/.env`)
```env
# Database
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority

# Redis (Upstash with SSL support)
REDIS_URL=rediss://default:password@host:port

# Security
SECRET_KEY=your_secret_key_here

# APIs
GOOGLE_API_KEY=your_gemini_api_key
```

### Frontend Environment (`frontend/.env`)
```env
# Backend API endpoint
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# For production:
# NEXT_PUBLIC_API_URL=https://your-backend-domain.com/api/v1
```

## Production Deployment

### Cloud Services Setup
1. **MongoDB Atlas**: Create cluster and get connection string
2. **Upstash Redis**: Create Redis instance with SSL enabled
3. **Google Cloud Storage**: Setup bucket for document storage
4. **Gemini API**: Get API key for document extraction

### Deployment Commands
Each service can be deployed independently:

**Frontend:**
```bash
cd frontend
npm install
npm run build
npm start
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Worker:**
```bash
cd backend
celery -A app.core.celery_app worker --loglevel=info
```

## Access Points
- **Frontend**: http://localhost:3000 (development) or your frontend domain
- **Backend API**: http://localhost:8000/docs (development) or your backend domain
- **Health Check**: `GET /health` endpoint on backend

## Monitoring & Logs

### Viewing Logs
Each service runs on its own server. Check logs using standard system logging or application-specific log files.

### Celery Worker Logs
The background worker logs can be found on the worker server where the Celery process is running.

### Backend API Logs
Backend API logs can be found on the backend server where the FastAPI application is running.

## Development

- **Frontend**: `cd frontend && npm run dev`
- **Backend**: `cd backend && uvicorn app.main:app --reload`
- **Worker**: `cd backend && celery -A app.core.celery_app worker --loglevel=info`

## Critical Path Components

| Component | Implementation |
|-----------|----------------|
| **Backend API** | FastAPI, CORS, Health Checks |
| **Authentication** | JWT (15m access / 7d refresh) |
| **Database** | MongoDB Atlas, Motor, Indexes |
| **Storage** | GCS with Presigned URLs |
| **Task Queue** | Celery + Redis |
| **Frontend** | Next.js + Protected Routes |