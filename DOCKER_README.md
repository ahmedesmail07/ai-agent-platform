# Docker Setup for AI Agent Platform

This guide explains how to run both the backend and frontend using Docker.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (usually included with Docker Desktop)

## Quick Start

### Option 1: Using the provided scripts

**Windows:**

```bash
run-docker.bat
```

**Linux/Mac:**

```bash
chmod +x run-docker.sh
./run-docker.sh
```

### Option 2: Manual Docker commands

```bash
# Build and start all services
docker-compose up --build -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Services

The Docker setup includes two services:

### Backend Service

- **Port**: 8000
- **Image**: Built from the root Dockerfile
- **Health Check**: `http://localhost:8000/health`
- **Features**: FastAPI backend with SQLite database

### Frontend Service

- **Port**: 3000
- **Image**: Built from `frontend/Dockerfile`
- **Health Check**: `http://localhost:3000/health`
- **Features**: React frontend with nginx proxy

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │
│   (Port 3000)   │◄──►│   (Port 8000)   │
│   React + Nginx │    │   FastAPI       │
└─────────────────┘    └─────────────────┘
         │                       │
         └─── Proxy API calls ───┘
```

## Network Configuration

- **Frontend**: Serves React app on port 3000
- **Backend**: Runs FastAPI on port 8000
- **Proxy**: Frontend nginx proxies `/api/*` and `/audio/*` requests to backend
- **Internal Network**: Services communicate via Docker network `ai-agent-network`

## Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# Database URL (optional, defaults to SQLite)
DATABASE_URL=sqlite+aiosqlite:///./ai_agent_platform.db

# Debug mode (optional)
DEBUG=False

# Log level (optional)
LOG_LEVEL=info
```

## Volumes

- **Audio Files**: Persistent storage for audio files at `/app/audio_files`
- **Source Code**: Development volume for live code changes

## Useful Commands

```bash
# Start services in background
docker-compose up -d

# Start services with logs
docker-compose up

# Rebuild and start
docker-compose up --build

# Stop services
docker-compose down

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Access backend shell
docker-compose exec backend bash

# Access frontend shell
docker-compose exec frontend sh

# Check service health
curl http://localhost:8000/health
curl http://localhost:3000/health
```

## Troubleshooting

### Services not starting

```bash
# Check Docker is running
docker info

# Check service logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache
```

### Port conflicts

If ports 3000 or 8000 are already in use:

```bash
# Stop conflicting services
docker-compose down

# Or modify ports in docker-compose.yml
```

### Frontend not connecting to backend

- Check that both services are running: `docker-compose ps`
- Verify nginx proxy configuration in `frontend/nginx.conf`
- Check backend logs: `docker-compose logs backend`

### Database issues

```bash
# Reset database (WARNING: This will delete all data)
docker-compose down -v
docker-compose up --build
```

## Development vs Production

### Development

- Source code is mounted as volumes for live changes
- Debug mode enabled
- Hot reloading available

### Production

- Build optimized images
- No source code mounting
- Production nginx configuration
- Optimized for performance

## Security Notes

- Services run as non-root users
- Health checks implemented
- Proper network isolation
- Environment variables for sensitive data

## Performance

- Multi-stage builds for smaller images
- Nginx compression enabled
- Optimized React build
- Efficient Docker layer caching
