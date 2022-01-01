# CodeReview AI Assistant

[![CI/CD Pipeline](https://github.com/William9701/code-review-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/William9701/code-review-ai/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/docker-enabled-blue.svg)](docker-compose.yml)

> **Enterprise-grade AI-powered code review automation that catches security vulnerabilities, performance issues, and code smells before they reach production.**

## 🚀 Overview

CodeReview AI Assistant is an intelligent GitHub App that automatically reviews pull requests using a hybrid approach of static analysis and LLM reasoning. It provides actionable, context-aware feedback directly on your PRs with explanations and suggested fixes.

## ✨ Key Features

### 🔒 Security Analysis
- SQL injection, XSS, and CSRF detection
- Hardcoded secrets and credential scanning
- Insecure dependency identification
- OWASP Top 10 vulnerability checks

### ⚡ Performance Optimization
- N+1 query detection
- Inefficient algorithm identification
- Memory leak patterns
- React/Frontend performance anti-patterns

### 🎯 Code Quality
- Code smell detection
- Complexity analysis (cyclomatic, cognitive)
- Dead code identification
- Best practice enforcement

### 🤖 AI-Powered Intelligence
- Context-aware explanations
- False positive reduction
- Suggested code fixes
- Learning from team patterns

### ⚡ Instant Code Analysis
- Standalone web interface for immediate code review
- No GitHub integration required
- Support for Python, TypeScript, and JavaScript
- Real-time security vulnerability detection
- Detailed issue reports with severity levels

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   API Gateway (Kong)                     │
└─────────────────────────────────────────────────────────┘
                            ↓
┌──────────────┬──────────────┬──────────────┬────────────┐
│   Webhook    │   Analysis   │     LLM      │  GitHub    │
│   Service    │   Engine     │   Service    │  Service   │
└──────────────┴──────────────┴──────────────┴────────────┘
       ↓              ↓              ↓              ↓
┌──────────────────────────────────────────────────────────┐
│            Message Queue (RabbitMQ/Redis)                │
└──────────────────────────────────────────────────────────┘
       ↓              ↓              ↓              ↓
┌──────────────┬──────────────┬──────────────┬────────────┐
│   MongoDB    │    Redis     │   Prometheus │  Grafana   │
└──────────────┴──────────────┴──────────────┴────────────┘
```

### Microservices

- **Webhook Service**: Handles GitHub webhook events
- **Analysis Engine**: Runs static analysis workers in parallel
- **LLM Service**: AI-powered reasoning and suggestion generation
- **GitHub Service**: Manages all GitHub API interactions
- **Orchestrator**: Coordinates workflow between services
- **API Service**: REST API for dashboard and integrations
- **Notification Service**: Alerts and reporting

## 🚦 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ (for frontend)
- GitHub App credentials

### Installation

```bash
# Clone the repository
git clone git@github.com:William9701/code-review-ai.git
cd code-review-ai

# Copy environment template
cp .env.example .env

# Configure your GitHub App credentials
# Edit .env with your settings

# Start all services with Docker Compose
docker-compose up -d

# Or start services individually:
# Start MongoDB
docker run -d --name codereview-mongodb -p 27017:27017 mongo:7

# Start the API server
cd services/api
python main.py

# Start the frontend (in a new terminal)
cd frontend
npm install
npm run dev

# Check service health
curl http://localhost:8000/health

# Access the dashboard at http://localhost:3000
```

### Configuration

1. **Create a GitHub App** at https://github.com/settings/apps/new
2. **Set permissions**:
   - Pull requests: Read & Write
   - Contents: Read-only
   - Webhooks: Active
3. **Subscribe to events**: Pull Request, Push
4. **Add webhook URL**: `https://your-domain.com/webhooks/github`

## 📦 Project Structure

```
code-review-ai/
├── services/
│   ├── webhook/              # GitHub webhook handler
│   ├── analysis-engine/      # Static analysis workers
│   ├── llm-service/          # LLM integration
│   ├── github-service/       # GitHub API client
│   ├── orchestrator/         # Workflow coordination
│   ├── api/                  # REST API
│   └── notification/         # Alerts & reporting
├── shared/
│   ├── database/             # Database models & migrations
│   ├── messaging/            # Message queue utilities
│   ├── logging/              # Centralized logging
│   └── models/               # Shared data models
├── infrastructure/
│   ├── docker/               # Docker configurations
│   └── k8s/                  # Kubernetes manifests
├── frontend/                 # Dashboard (Next.js)
├── tests/                    # Integration & e2e tests
├── docs/                     # Documentation
└── scripts/                  # Utility scripts
```

## 🔧 Configuration Options

### Analysis Rules

Configure in `config/rules.yaml`:

```yaml
security:
  enabled: true
  severity_threshold: "medium"
  rules:
    - sql_injection
    - xss
    - secrets_detection

performance:
  enabled: true
  max_complexity: 15
  detect_n_plus_one: true

llm:
  provider: "anthropic"  # or "openai"
  model: "claude-3-5-sonnet"
  temperature: 0.2
  max_tokens: 2000
```

## 🧪 Development

### Run Tests

```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# E2E tests
pytest tests/e2e

# Coverage report
pytest --cov=services --cov-report=html
```

### Local Development

```bash
# Start individual services
cd services/webhook
python -m uvicorn main:app --reload

# Run linting
black . && flake8 && mypy .

# Type checking
pyright
```

## 📊 Monitoring & Observability

- **Metrics**: Prometheus + Grafana dashboards
- **Logging**: Structured JSON logs with ELK stack support
- **Tracing**: OpenTelemetry integration
- **Health checks**: `/health` and `/ready` endpoints on all services

## 🔐 Security

- **Secrets management**: Vault or AWS Secrets Manager
- **API authentication**: JWT tokens
- **GitHub webhook verification**: HMAC signature validation
- **Rate limiting**: Redis-based rate limiter
- **Data encryption**: At rest and in transit

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ using FastAPI, TypeScript, and Claude AI
- Inspired by the need for better code review automation
- Thanks to the open-source community

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/William9701/code-review-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/William9701/code-review-ai/discussions)

---

**Made with 🤖 by developers, for developers**
