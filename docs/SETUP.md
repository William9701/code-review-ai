# Setup Guide

Complete guide to set up CodeReview AI for development and production.

## Prerequisites

- **Docker** & **Docker Compose** v2.0+
- **Python** 3.11+
- **Node.js** 18+ (for frontend, optional)
- **Git**
- **GitHub Account** with admin access to create GitHub Apps

## 1. Create GitHub App

### Step 1: Create a New GitHub App

1. Go to GitHub Settings → Developer settings → GitHub Apps
2. Click "New GitHub App"

### Step 2: Configure the App

**Basic Information:**
- **GitHub App name**: `CodeReview AI` (or your preferred name)
- **Homepage URL**: `https://your-domain.com`
- **Webhook URL**: `https://your-domain.com/webhooks/github`
- **Webhook secret**: Generate a random string (save this!)

**Permissions:**

Repository permissions:
- **Pull requests**: Read & write
- **Contents**: Read-only
- **Metadata**: Read-only
- **Checks**: Read & write (optional)

**Subscribe to events:**
- ✅ Pull request
- ✅ Pull request review
- ✅ Push

### Step 3: Generate Private Key

1. After creating the app, scroll to "Private keys"
2. Click "Generate a private key"
3. Save the `.pem` file securely

### Step 4: Install the App

1. Go to "Install App" tab
2. Install on your account/organization
3. Select repositories to enable
4. Note the **Installation ID** from the URL

## 2. Get LLM API Keys

### Anthropic Claude (Recommended)

1. Go to https://console.anthropic.com/
2. Create API key
3. Save the key (starts with `sk-ant-`)

### OpenAI (Alternative)

1. Go to https://platform.openai.com/api-keys
2. Create API key
3. Save the key (starts with `sk-`)

## 3. Clone and Configure

```bash
# Clone repository
git clone https://github.com/yourusername/code-review-ai.git
cd code-review-ai

# Copy environment template
cp .env.example .env
```

## 4. Configure Environment Variables

Edit `.env` file:

```bash
# Database
DB_USER=codereview
DB_PASSWORD=your-secure-password-here
DATABASE_URL=postgresql://codereview:your-secure-password-here@postgres:5432/codereview

# Redis
REDIS_PASSWORD=your-redis-password-here
REDIS_URL=redis://:your-redis-password-here@redis:6379/0

# RabbitMQ
RABBITMQ_USER=codereview
RABBITMQ_PASSWORD=your-rabbitmq-password-here
RABBITMQ_URL=amqp://codereview:your-rabbitmq-password-here@rabbitmq:5672/

# GitHub App (from Step 1)
GITHUB_APP_ID=123456
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=your-webhook-secret-here

# LLM Provider (from Step 2)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
# OR for OpenAI:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-your-api-key-here

# API Service
JWT_SECRET=your-jwt-secret-min-32-chars-random-string
CORS_ORIGINS=http://localhost:3000

# Application
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## 5. Start Services

### Option A: Using Docker Compose (Recommended)

```bash
# Build and start all services
make build
make up

# Check status
make status

# View logs
make logs
```

### Option B: Manual Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

## 6. Verify Installation

### Check Service Health

```bash
# Webhook service
curl http://localhost:8001/health

# API service
curl http://localhost:8000/health

# Access Grafana
open http://localhost:3001
# Default credentials: admin/admin

# Access Prometheus
open http://localhost:9090

# Access RabbitMQ Management
open http://localhost:15672
# Credentials from .env (default: codereview/changeme)
```

### Run Database Migrations

```bash
make db-migrate
```

## 7. Configure Webhook Endpoint

For development, use **ngrok** or **Cloudflare Tunnel** to expose your local server:

### Using ngrok:

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/download

# Start tunnel
ngrok http 8001

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Update GitHub App webhook URL to:
# https://abc123.ngrok.io/webhooks/github
```

### Using Cloudflare Tunnel:

```bash
# Install cloudflared
brew install cloudflared  # macOS

# Start tunnel
cloudflared tunnel --url http://localhost:8001

# Use the provided HTTPS URL
```

## 8. Test the Integration

1. **Open a test PR** in a repository where the app is installed
2. **Check webhook delivery** in GitHub App settings
3. **View logs**: `make logs`
4. **Check database**: `make db-shell`
   ```sql
   SELECT * FROM pull_requests ORDER BY created_at DESC LIMIT 1;
   SELECT * FROM analyses ORDER BY created_at DESC LIMIT 1;
   ```
5. **Verify PR comments** appear on GitHub

## 9. Development Setup

### Install Development Dependencies

```bash
make setup-dev

# This will:
# - Install Python dev dependencies
# - Set up pre-commit hooks
# - Configure environment
```

### Run Tests

```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# With coverage
pytest --cov=services --cov-report=html
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Run all checks
make test && make lint
```

## 10. Production Deployment

### Using Docker Swarm

```bash
docker stack deploy -c docker-compose.yml codereview-ai
```

### Using Kubernetes

```bash
# Apply configurations
kubectl apply -f infrastructure/k8s/

# Check status
kubectl get pods -n codereview-ai
```

### Environment Variables for Production

**Important**: Change all default passwords and secrets!

```bash
# Generate secure passwords
openssl rand -base64 32  # For DB_PASSWORD
openssl rand -hex 32     # For JWT_SECRET
```

## Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs [service-name]

# Restart services
make restart

# Clean restart
make clean
make build
make up
```

### Database connection errors

```bash
# Check PostgreSQL
docker-compose exec postgres psql -U codereview -d codereview

# Reset database
docker-compose down -v
docker-compose up -d postgres
make db-migrate
```

### Webhook not receiving events

1. Check GitHub App webhook delivery logs
2. Verify webhook URL is accessible
3. Check webhook secret matches
4. View webhook service logs: `docker-compose logs webhook-service`

### LLM service errors

1. Verify API key is correct
2. Check API quota/billing
3. View logs: `docker-compose logs llm-service`

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- Check [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute
- Customize analysis rules in `config/rules.yaml`
- Set up monitoring alerts in Grafana

## Support

- 📚 [Documentation](https://docs.codereview-ai.dev)
- 💬 [GitHub Discussions](https://github.com/yourusername/code-review-ai/discussions)
- 🐛 [Report Issues](https://github.com/yourusername/code-review-ai/issues)
