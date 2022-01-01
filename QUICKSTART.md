# 🚀 Quick Start Guide

Get CodeReview AI running in 5 minutes!

## Prerequisites

- Docker Desktop installed
- GitHub account
- LLM API key (Anthropic or OpenAI)

## Step 1: Run the Startup Script

### Windows:
```cmd
start.bat
```

### Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

## Step 2: Configure Environment

Edit the `.env` file that was created:

```bash
# Minimum required configuration:

# 1. GitHub App (create at https://github.com/settings/apps/new)
GITHUB_APP_ID=your-app-id
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=your-webhook-secret

# 2. LLM Provider (get key from console.anthropic.com or platform.openai.com)
ANTHROPIC_API_KEY=sk-ant-your-key-here
# OR
OPENAI_API_KEY=sk-your-key-here

# 3. Change default passwords
DB_PASSWORD=change-this-password
REDIS_PASSWORD=change-this-password
RABBITMQ_PASSWORD=change-this-password
```

## Step 3: Start Services

```bash
# Windows
start.bat

# Linux/Mac
./start.sh

# Or using Make
make up
```

## Step 4: Verify Installation

Open in browser:
- API: http://localhost:8000/health
- Grafana: http://localhost:3001 (admin/admin)
- RabbitMQ: http://localhost:15672 (codereview/changeme)

## Step 5: Setup GitHub Webhook

For local testing, use ngrok:

```bash
# Install ngrok
# Download from https://ngrok.com/download

# Start tunnel
ngrok http 8001

# Copy the HTTPS URL and update your GitHub App webhook URL
```

## Step 6: Test with a Pull Request

1. Install your GitHub App on a test repository
2. Create a new branch and make some code changes
3. Open a Pull Request
4. Watch CodeReview AI analyze and comment!

## Common Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Clean everything
docker-compose down -v
```

## Troubleshooting

**Services won't start?**
```bash
docker-compose logs
```

**No comments on PR?**
- Check GitHub App installation
- Verify webhook URL is accessible
- Check webhook delivery in GitHub App settings
- View webhook service logs: `docker-compose logs webhook-service`

**LLM errors?**
- Verify API key is correct
- Check API quota/billing
- View logs: `docker-compose logs llm-service`

## Next Steps

- Read [docs/SETUP.md](docs/SETUP.md) for detailed setup
- Check [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) to understand the system
- Customize analysis rules
- Set up production deployment

## Support

- 📖 [Full Documentation](docs/SETUP.md)
- 💬 [GitHub Discussions](https://github.com/yourusername/code-review-ai/discussions)
- 🐛 [Report Issues](https://github.com/yourusername/code-review-ai/issues)

---

**That's it! You're ready to go! 🎉**
