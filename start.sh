#!/bin/bash

# CodeReview AI - Quick Start Script

set -e

echo "🤖 CodeReview AI - Quick Start"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration:"
    echo "   - GitHub App credentials (GITHUB_APP_ID, GITHUB_PRIVATE_KEY, GITHUB_WEBHOOK_SECRET)"
    echo "   - LLM API key (ANTHROPIC_API_KEY or OPENAI_API_KEY)"
    echo "   - Change default passwords"
    echo ""
    read -p "Press Enter after you've configured .env file..."
fi

# Build images
echo ""
echo "🔨 Building Docker images..."
docker-compose build

# Start services
echo ""
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "🏥 Checking service health..."

services=("webhook-service:8001" "api-service:8000" "postgres:5432" "redis:6379" "rabbitmq:5672")
all_healthy=true

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if docker-compose ps | grep -q "$name.*Up"; then
        echo "✅ $name is running"
    else
        echo "❌ $name is not running"
        all_healthy=false
    fi
done

if [ "$all_healthy" = true ]; then
    echo ""
    echo "✨ All services are running!"
    echo ""
    echo "📊 Access your services:"
    echo "   - API Service:      http://localhost:8000"
    echo "   - Webhook Service:  http://localhost:8001"
    echo "   - Grafana:          http://localhost:3001 (admin/admin)"
    echo "   - Prometheus:       http://localhost:9090"
    echo "   - RabbitMQ:         http://localhost:15672 (codereview/changeme)"
    echo ""
    echo "📚 Next steps:"
    echo "   1. Configure your GitHub App webhook URL"
    echo "   2. Install the GitHub App on your repositories"
    echo "   3. Open a Pull Request to trigger analysis"
    echo ""
    echo "📖 Documentation: docs/SETUP.md"
    echo "🐛 View logs: docker-compose logs -f"
    echo "🛑 Stop services: docker-compose down"
else
    echo ""
    echo "⚠️  Some services failed to start. Check logs:"
    echo "   docker-compose logs"
fi
