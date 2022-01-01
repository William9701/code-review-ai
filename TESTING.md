# Testing Guide

## Quick Test (Without Full Docker Setup)

### 1. Test Analyzers Only

```bash
cd code-review-ai
pip install radon
python test_analyzers.py
```

**Expected Output:**
- Python analyzer finds 2 issues
- TypeScript analyzer finds 4 issues
- Security analyzer finds 5 critical/high issues

### 2. Test Full Integration

```bash
python test_integration.py
```

**Expected Output:**
- Analyzes 3 files (Python + TypeScript)
- Finds 11 total issues
- Shows sample GitHub comment format
- Demonstrates complete flow

### 3. Run Unit Tests

```bash
python tests/unit/test_analyzers.py
```

**Expected Output:**
- 7/9 tests passing
- All security detections working
- CWE/OWASP mapping verified

## Full Docker Testing

### 1. Check Infrastructure

```bash
docker-compose ps
```

**Should show:**
- postgres (healthy)
- redis (healthy)
- rabbitmq (healthy)
- prometheus (running)
- grafana (running)

### 2. Test Database Connection

```bash
docker-compose exec postgres psql -U codereview -d codereview -c "SELECT version();"
```

### 3. Test Redis

```bash
docker-compose exec redis redis-cli ping
```

Should return: `PONG`

### 4. Test RabbitMQ

Open browser: http://localhost:15672
- Username: `codereview`
- Password: `changeme`

### 5. Test Monitoring

- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

## Testing with Real GitHub PR

### Prerequisites

1. Create GitHub App:
   - Go to https://github.com/settings/apps/new
   - Set webhook URL (use ngrok for local testing)
   - Generate private key
   - Install on a test repository

2. Configure `.env`:
   ```bash
   GITHUB_APP_ID=your-app-id
   GITHUB_PRIVATE_KEY="your-private-key"
   GITHUB_WEBHOOK_SECRET=your-secret
   ANTHROPIC_API_KEY=your-api-key
   ```

3. Start ngrok:
   ```bash
   ngrok http 8001
   ```

4. Update GitHub App webhook URL to ngrok URL

### Test Flow

1. **Create test branch**:
   ```bash
   git checkout -b test-codereview
   ```

2. **Add problematic code**:
   ```python
   # test_security.py
   password = "admin123"  # Hardcoded secret
   query = "SELECT * FROM users WHERE id = " + user_id  # SQL injection
   ```

3. **Commit and push**:
   ```bash
   git add test_security.py
   git commit -m "Test security issues"
   git push origin test-codereview
   ```

4. **Create Pull Request**

5. **Check Results**:
   - View webhook delivery in GitHub App settings
   - Check service logs: `docker-compose logs -f webhook-service`
   - Look for PR comments from CodeReview AI bot

## Manual API Testing

### Webhook Endpoint

```bash
curl -X POST http://localhost:8001/webhooks/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: ping" \
  -d '{"zen": "test"}'
```

### Health Checks

```bash
# Webhook service
curl http://localhost:8001/health

# API service (when running)
curl http://localhost:8000/health
```

## Test Scenarios

### Scenario 1: SQL Injection Detection

**Code:**
```python
query = "SELECT * FROM users WHERE email = '" + user_email + "'"
```

**Expected:**
- CRITICAL severity
- Rule: security_sql_injection
- CWE-89
- OWASP A03:2021

### Scenario 2: Hardcoded Secrets

**Code:**
```python
API_KEY = "sk-1234567890abcdef"
```

**Expected:**
- CRITICAL severity
- Rule: security_hardcoded_secret
- CWE-798
- OWASP A07:2021

### Scenario 3: Weak Cryptography

**Code:**
```python
import hashlib
hash = hashlib.md5(password.encode()).hexdigest()
```

**Expected:**
- HIGH severity
- Rule: security_weak_crypto
- CWE-327
- OWASP A02:2021

### Scenario 4: Complex Function

**Code:**
```python
def complex_func():
    for i in range(100):
        for j in range(100):
            for k in range(100):
                if i > 50:
                    if j > 50:
                        # Many nested conditions...
```

**Expected:**
- MEDIUM/HIGH severity
- Rule: python_high_complexity
- Cyclomatic complexity > 15

## Troubleshooting Tests

### Analyzers not detecting issues

```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install radon
```

### Docker services not starting

```bash
# Check Docker is running
docker ps

# Restart services
docker-compose restart

# View logs
docker-compose logs -f
```

### Database connection errors

```bash
# Check PostgreSQL is healthy
docker-compose exec postgres pg_isready -U codereview

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

## Performance Testing

### Analyze Large File

```bash
# Create large test file
python -c "
code = 'def func{i}(): pass\\n' * 1000
with open('large_test.py', 'w') as f:
    f.write(code)
"

# Time the analysis
time python -c "
import sys
sys.path.insert(0, 'services/analysis-engine')
from analyzers.python_analyzer import PythonAnalyzer
analyzer = PythonAnalyzer()
with open('large_test.py') as f:
    issues = analyzer.analyze('large_test.py', f.read())
print(f'Found {len(issues)} issues')
"
```

## Expected Test Results

```
✓ Infrastructure: All services running
✓ Analyzers: 7/9 unit tests passing
✓ Integration: Complete flow working
✓ Security: All OWASP detections working
✓ Performance: < 1s for typical file
```

## CI/CD Testing

Tests run automatically on:
- Every push to main/develop
- Every pull request
- Security scan on dependencies

View results in GitHub Actions tab.
