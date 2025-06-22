# Service Setup Guide

Essential configuration for external services and API credentials required to run the LLM Calendar Assistant. This guide walks you through setting up **Supabase**, **LLM providers**, and **Google Calendar API** authentication.

## Database Setup (Supabase)

### Create Project
1. Go to [Supabase](https://supabase.com/) and create account
2. Create new project: `llm-calendar-assistant`
3. Choose password and region

### Get Connection Details
1. Settings → Database → Connection info
2. Add to `.env`:
```bash
DATABASE_HOST=your_host.supabase.com
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_NAME=postgres
DATABASE_PORT=6543
```

## LLM Provider Setup

Choose at least one provider:

### OpenAI
1. [OpenAI Platform](https://platform.openai.com/) → API Keys → Create new key
2. Add to `.env`:
```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.0
OPENAI_MAX_TOKENS=2048
...
```

### Anthropic
1. [Anthropic Console](https://console.anthropic.com/) → API Keys → Create new key
2. Add to `.env`:
```bash
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
ANTHROPIC_TEMPERATURE=0.0
ANTHROPIC_MAX_TOKENS=2048
...
```

## Google Calendar Setup

### Create OAuth Credentials
1. [Google Cloud Console](https://console.cloud.google.com/) → New project
2. APIs & Services → Library → Enable "Google Calendar API"
3. APIs & Services → Credentials → Create OAuth 2.0 Client ID
4. Application type: "Desktop Application"
5. Download `credentials.json` to project root

### Generate Token
```bash
# Ensure Python environment is active
source .venv/bin/activate

# Generate OAuth token
./scripts/init_token.sh
```
Follow browser prompts to authorize calendar access.

## Environment Configuration

```bash
# Copy template in root directory
cp .env.sample .env
```
Edit the file with your service credentials and configuration values.
- Database connection (Supabase)
- LLM API keys (OpenAI/Anthropic)
- Calendar paths (credentials.json, token.json)


## Troubleshooting

### Database Issues
- Verify Supabase project is active
- Check connection details match exactly

### API Key Issues  
- Verify key format and validity
- Check API usage limits

### OAuth Token Issues
- Ensure Calendar API is enabled
- Re-run `./scripts/init_token.sh` if expired

---

**Next Steps**: Continue with [Quick Start Guide](quick-start.md) to deploy your application.