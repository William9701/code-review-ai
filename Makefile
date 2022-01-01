.PHONY: help build up down logs clean test lint format setup-dev

help:
	@echo "CodeReview AI - Makefile Commands"
	@echo ""
	@echo "  make build       - Build all Docker images"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linters"
	@echo "  make format      - Format code"
	@echo "  make setup-dev   - Setup development environment"
	@echo "  make db-migrate  - Run database migrations"
	@echo "  make db-shell    - Open MongoDB shell"

build:
	@echo "Building Docker images..."
	docker-compose build

up:
	@echo "Starting services..."
	docker-compose up -d
	@echo "Services started! Access:"
	@echo "  - API: http://localhost:8000"
	@echo "  - Webhook: http://localhost:8001"
	@echo "  - Grafana: http://localhost:3001"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - RabbitMQ: http://localhost:15672"

down:
	@echo "Stopping services..."
	docker-compose down

logs:
	docker-compose logs -f

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	docker system prune -f

test:
	@echo "Running tests..."
	pytest tests/ -v --cov=services --cov-report=html

lint:
	@echo "Running linters..."
	black --check .
	flake8 .
	mypy .

format:
	@echo "Formatting code..."
	black .
	isort .

setup-dev:
	@echo "Setting up development environment..."
	cp .env.example .env
	@echo "Please edit .env with your configuration"
	pip install -r requirements-dev.txt
	pre-commit install

db-migrate:
	@echo "Running database migrations..."
	docker-compose exec orchestrator alembic upgrade head

db-shell:
	@echo "Opening MongoDB shell..."
	docker-compose exec mongodb mongosh codereview

restart:
	@echo "Restarting services..."
	docker-compose restart

status:
	@echo "Service status:"
	docker-compose ps
