@echo off
REM CodeReview AI - Quick Start Script for Windows

echo.
echo 🤖 CodeReview AI - Quick Start
echo ================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo    Visit: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo.
    echo ⚠️  Please edit .env file with your configuration:
    echo    - GitHub App credentials GITHUB_APP_ID, GITHUB_PRIVATE_KEY, GITHUB_WEBHOOK_SECRET
    echo    - LLM API key ANTHROPIC_API_KEY or OPENAI_API_KEY
    echo    - Change default passwords
    echo.
    pause
)

REM Build images
echo.
echo 🔨 Building Docker images...
docker-compose build

REM Start services
echo.
echo 🚀 Starting services...
docker-compose up -d

REM Wait for services to be healthy
echo.
echo ⏳ Waiting for services to be ready...
timeout /t 15 /nobreak >nul

REM Check service health
echo.
echo 🏥 Checking service health...
docker-compose ps

echo.
echo ✨ Services started!
echo.
echo 📊 Access your services:
echo    - API Service:      http://localhost:8000
echo    - Webhook Service:  http://localhost:8001
echo    - Grafana:          http://localhost:3001 (admin/admin)
echo    - Prometheus:       http://localhost:9090
echo    - RabbitMQ:         http://localhost:15672 (codereview/changeme)
echo.
echo 📚 Next steps:
echo    1. Configure your GitHub App webhook URL
echo    2. Install the GitHub App on your repositories
echo    3. Open a Pull Request to trigger analysis
echo.
echo 📖 Documentation: docs\SETUP.md
echo 🐛 View logs: docker-compose logs -f
echo 🛑 Stop services: docker-compose down
echo.
pause
