## CodeReview AI - Architecture Documentation

## Overview

CodeReview AI is a microservices-based application that provides automated code review for GitHub pull requests using a hybrid approach of static analysis and AI-powered reasoning.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         GitHub                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓ webhooks
┌─────────────────────────────────────────────────────────────────┐
│                      Webhook Service                             │
│  - Receives GitHub events                                        │
│  - Validates webhook signatures                                  │
│  - Stores PR metadata in database                                │
│  - Publishes events to message queue                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓ RabbitMQ
┌─────────────────────────────────────────────────────────────────┐
│                     Analysis Engine                              │
│  - Consumes PR analysis jobs                                     │
│  - Performs static code analysis                                 │
│    • Python analyzer (complexity, smells)                        │
│    • TypeScript analyzer (patterns, best practices)              │
│    • Security analyzer (vulnerabilities, OWASP)                  │
│  - Stores findings in database                                   │
│  - Publishes results for LLM processing                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓ RabbitMQ
┌─────────────────────────────────────────────────────────────────┐
│                        LLM Service                               │
│  - Enhances static analysis findings                             │
│  - Generates explanations using Claude/GPT-4                     │
│  - Creates suggested fixes                                       │
│  - Reduces false positives                                       │
│  - Publishes enhanced results                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓ RabbitMQ
┌─────────────────────────────────────────────────────────────────┐
│                      GitHub Service                              │
│  - Posts review comments on PR                                   │
│  - Posts summary comment                                         │
│  - Updates PR status checks                                      │
│  - Handles GitHub API rate limiting                              │
└─────────────────────────────────────────────────────────────────┘
```

## Services

### 1. Webhook Service

**Responsibility**: Entry point for GitHub webhooks

**Technology**: FastAPI, Python 3.11

**Key Functions**:
- Webhook signature verification (HMAC-SHA256)
- Event routing (pull_request, push, installation)
- Repository and PR metadata persistence
- Message queue publishing

**Endpoints**:
- `POST /webhooks/github` - Receive GitHub webhooks
- `GET /health` - Health check
- `GET /ready` - Readiness check

**Database Tables Used**:
- `repositories`
- `pull_requests`

### 2. Analysis Engine

**Responsibility**: Static code analysis

**Technology**: Python 3.11, AST parsing, Radon

**Key Functions**:
- Multi-language code analysis
- Parallel analysis workers
- Issue detection and classification
- Metrics calculation

**Analyzers**:
1. **Python Analyzer**
   - Cyclomatic complexity (via Radon)
   - Maintainability index
   - Code smells (long functions, too many params)
   - AST-based pattern matching

2. **TypeScript Analyzer**
   - Type safety issues (`any` usage)
   - Console statements
   - Loose equality operators
   - Missing error handling

3. **Security Analyzer**
   - SQL injection patterns
   - Hardcoded secrets
   - Path traversal
   - XSS vulnerabilities
   - Weak cryptography
   - OWASP Top 10 mapping

**Database Tables Used**:
- `analyses`
- `issues`
- `analysis_rules`

### 3. LLM Service

**Responsibility**: AI-powered code review enhancement

**Technology**: Python 3.11, Anthropic Claude/OpenAI GPT-4

**Key Functions**:
- Issue explanation generation
- Suggested fix creation
- Context-aware reasoning
- False positive reduction

**LLM Providers**:
- Anthropic Claude (primary)
- OpenAI GPT-4 (alternative)

**Prompt Engineering**:
- Structured JSON output
- Few-shot learning
- Context injection (file path, severity, code snippet)

### 4. GitHub Service

**Responsibility**: GitHub API interactions

**Technology**: Python 3.11, PyGithub

**Key Functions**:
- GitHub App authentication (JWT)
- Installation access tokens
- Review comment posting
- Summary comment generation
- Rate limit handling

**Comment Format**:
- Severity and category emojis
- Detailed explanation
- Suggested fix with code blocks
- OWASP/CWE references

### 5. Orchestrator Service

**Responsibility**: Workflow coordination and scheduling

**Technology**: Python 3.11, Celery (optional)

**Key Functions**:
- Workflow state management
- Retry logic
- Dead letter queue handling
- Database migrations (Alembic)

### 6. API Service

**Responsibility**: REST API for dashboard and integrations

**Technology**: FastAPI, Python 3.11

**Endpoints**:
- `GET /repositories` - List repositories
- `GET /analyses/{id}` - Get analysis details
- `GET /issues` - List issues with filtering
- `GET /metrics` - Analytics and metrics

**Authentication**: JWT-based

### 7. Notification Service

**Responsibility**: Alerts and reporting

**Technology**: Python 3.11, SMTP

**Key Functions**:
- Email notifications
- Slack integration (optional)
- Daily/weekly reports
- Critical issue alerts

## Data Flow

### Pull Request Analysis Flow

```
1. Developer opens PR
   ↓
2. GitHub sends webhook → Webhook Service
   ↓
3. Webhook Service stores PR metadata
   ↓
4. Publishes "pr.opened" event → RabbitMQ
   ↓
5. Analysis Engine consumes event
   ↓
6. Fetches PR files from GitHub
   ↓
7. Runs static analysis (Python, TS, Security)
   ↓
8. Stores issues in database
   ↓
9. Publishes "analysis.completed" → RabbitMQ
   ↓
10. LLM Service consumes event
   ↓
11. Enhances issues with AI explanations
   ↓
12. Updates database with enhancements
   ↓
13. Publishes "github.comment.create" → RabbitMQ
   ↓
14. GitHub Service consumes event
   ↓
15. Posts review comments on PR
   ↓
16. Posts summary comment
```

## Database Schema

### Core Tables

**repositories**
- id, github_id, name, full_name, owner
- installation_id, default_branch
- is_active, config (JSON)
- created_at, updated_at

**pull_requests**
- id, github_id, repository_id, pr_number
- title, description, author
- base_branch, head_branch, base_sha, head_sha
- state, is_draft
- files_changed, additions, deletions
- created_at, updated_at

**analyses**
- id, pull_request_id, status
- started_at, completed_at
- total_issues, critical_issues, high_issues, etc.
- analysis_duration_seconds
- error_message, metadata

**issues**
- id, analysis_id, file_path
- line_start, line_end, column_start, column_end
- severity, category, rule_id
- title, description, code_snippet
- suggested_fix, explanation
- github_comment_id
- is_false_positive

## Message Queue Architecture

### Exchanges

1. **pr.events** (topic)
   - Routing keys: `pr.opened`, `pr.synchronized`, `pr.closed`

2. **analysis.events** (topic)
   - Routing keys: `analysis.static.*`, `analysis.llm.*`, `analysis.completed`

3. **github.events** (topic)
   - Routing keys: `github.comment.*`, `github.status.*`

4. **notifications** (fanout)
   - Broadcasts to all notification channels

### Queues

- `webhook.pr.opened`
- `webhook.pr.synchronized`
- `analysis.static`
- `analysis.llm`
- `analysis.results`
- `github.comments`
- `notifications.email`
- `dlq` (dead letter queue)

## Scalability Considerations

### Horizontal Scaling

- **Analysis Engine**: Multiple workers for parallel analysis
- **LLM Service**: Multiple instances with load balancing
- **Message Queue**: RabbitMQ clustering

### Caching Strategy

- **Redis**:
  - GitHub API responses (rate limit optimization)
  - Analysis rules
  - Session data

### Performance Optimization

- Database connection pooling
- Async I/O where applicable
- Batch GitHub API calls
- Analysis result caching

## Security

### Authentication & Authorization

- GitHub App authentication (private key + JWT)
- Webhook signature verification (HMAC-SHA256)
- API service JWT tokens
- Environment-based secrets

### Data Protection

- Secrets management (AWS Secrets Manager/Vault)
- Database encryption at rest
- TLS for all external communication
- Input validation and sanitization

### Rate Limiting

- GitHub API: 5000 req/hour (authenticated)
- API Service: Redis-based rate limiter
- Webhook: Queue-based backpressure

## Monitoring & Observability

### Metrics (Prometheus)

- Request rates and latencies
- Analysis processing time
- Queue depths
- Error rates
- GitHub API usage

### Logging (Structured JSON)

- Centralized logging (ELK stack compatible)
- Request tracing
- Error tracking
- Audit logs

### Dashboards (Grafana)

- System health overview
- Service-specific metrics
- Business metrics (PRs analyzed, issues found)
- Cost tracking (LLM API usage)

## Deployment

### Docker Compose (Development)

```bash
docker-compose up -d
```

### Kubernetes (Production)

- Helm charts available
- Auto-scaling based on queue depth
- Health checks and readiness probes
- Resource limits and requests

## Technology Stack

**Backend**: Python 3.11, FastAPI
**Database**: PostgreSQL 16
**Cache**: Redis 7
**Message Queue**: RabbitMQ 3.12
**Monitoring**: Prometheus + Grafana
**CI/CD**: GitHub Actions
**Container**: Docker, Kubernetes
**LLM**: Anthropic Claude 3.5 Sonnet / OpenAI GPT-4
