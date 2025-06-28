@echo off
echo Starting AI Agent Platform with Docker...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Build and start the services
echo Building and starting services...
docker-compose up --build -d

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check service status
echo Checking service status...
docker-compose ps

echo.
echo AI Agent Platform is running!
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo Health Check: http://localhost:8000/health
echo.
echo To stop the services, run: docker-compose down
echo To view logs, run: docker-compose logs -f
pause 