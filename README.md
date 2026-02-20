# AI Product Team Dashboard

Multi-agent dashboard that runs role-based OpenClaw agents (PM, Engineer, Designer, Analyst) in structured "meetings" and produces investor-style memos.

## Prerequisites

### Required services

| Service    | Purpose         | Install (macOS)              |
|------------|-----------------|------------------------------|
| PostgreSQL | Database        | `brew install postgresql@16` |
| Redis      | Queue / pub-sub | `brew install redis`         |
| Python 3.11+ | Runtime       | `brew install python@3.11`   |
| OpenClaw   | Agent runtime   | See [OpenClaw Setup](#openclaw-setup) below |

### Option A: Run locally (no Docker)

```bash
# 1. Install Python dependencies
make local-setup

# 2. Start Postgres & Redis
brew services start postgresql@16
brew services start redis

# 3. Create the database
make local-db

# 4. Run migrations
make local-migrate

# 5. Seed demo data
make local-seed

# 6. Start the API (terminal 1)
make local-api

# 7. Start the Celery worker (terminal 2)
make local-worker
```

### Option B: Run with Docker

```bash
# Requires Docker Desktop: https://www.docker.com/products/docker-desktop/
make up        # builds + starts all services
make migrate   # run migrations
make seed      # seed demo data
```

---

## OpenClaw Setup

OpenClaw is the agent runtime that powers the AI agents. The dashboard calls it via its CLI. **You must have OpenClaw installed and configured on the same machine running the Celery worker.**

### Step 1: Install OpenClaw

Follow the official install guide: **https://openclaw.ai**

After installation, verify:

```bash
openclaw --version
openclaw health
```

### Step 2: Run the onboarding wizard

```bash
openclaw onboard
```

This will:
- Configure your API keys (Anthropic, OpenAI, etc.)
- Set up the agent workspace at `~/.openclaw/workspace`
- Start the Gateway service

### Step 3: Verify the Gateway is running

```bash
openclaw gateway status
openclaw health --json
```

You should see a healthy gateway on `ws://127.0.0.1:18789`.

### Step 4: (Optional) Configure a model

```bash
# List available models
openclaw models list

# Set your preferred default model
openclaw models set anthropic/claude-sonnet-4-20250514

# Verify auth
openclaw models status
```

### How the dashboard uses OpenClaw

The dashboard invokes OpenClaw from Celery workers using:

```bash
openclaw agent --message "<prompt>" --json --local --session-id <uuid>
```

Each meeting round calls this command with a role-specific prompt. The `--json` flag gives structured output that gets parsed into database records. The `--local` flag runs the agent embedded (no Gateway needed for basic usage, but Gateway enables richer features).

**Key files:**
- `app/openclaw/cli_adapter.py` — subprocess wrapper with timeout/error handling
- `app/openclaw/client.py` — high-level client (swap point for future Python SDK)
- `app/openclaw/base.py` — abstract adapter interface

### If OpenClaw is not installed

The dashboard handles this gracefully:
- Agent rounds return structured error results (never crash)
- Events record `"success": false` with the error message
- The meeting pipeline retries once, then marks the session as failed
- You can still use the REST API to create projects, agents, threads, and messages

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENCLAW_BIN` | `openclaw` | Path to the OpenClaw binary |
| `OPENCLAW_GATEWAY_URL` | `ws://127.0.0.1:18789` | Gateway WebSocket URL |
| `OPENCLAW_GATEWAY_TOKEN` | (empty) | Gateway auth token (if password-protected) |
| `OPENCLAW_WORKSPACE` | `~/.openclaw/workspace` | Agent workspace directory |
| `OPENCLAW_TIMEOUT_SECONDS` | `120` | Max seconds per agent invocation |
| `OPENCLAW_PROFILE` | (empty) | OpenClaw `--profile` flag for state isolation |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST   | `/projects` | Create a project |
| GET    | `/projects/{id}` | Get project details |
| POST   | `/projects/{id}/agents` | Create an agent |
| GET    | `/projects/{id}/agents` | List agents |
| POST   | `/projects/{id}/threads` | Create a thread |
| GET    | `/threads/{id}/messages` | List messages |
| POST   | `/threads/{id}/messages` | Add a user message |
| POST   | `/projects/{id}/sessions` | Start a meeting session (async) |
| GET    | `/projects/{id}/memos` | List memos |
| GET    | `/memos/{id}` | Read a memo |
| GET    | `/projects/{id}/events` | Event timeline |
| WS     | `/ws/projects/{id}` | Real-time event stream |
| GET    | `/health` | Health check |

## Demo Walkthrough

After seeding (`make local-seed`), the output will print a project ID. Use it:

```bash
PROJECT_ID=<from seed output>

# Start a meeting
curl -s -X POST http://localhost:8000/projects/$PROJECT_ID/sessions \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "We need to build a smart notification system that learns user preferences and reduces notification fatigue.",
    "thread_title": "Sprint Planning — Notifications"
  }' | python -m json.tool

# Watch events in real-time (install websocat: brew install websocat)
websocat ws://localhost:8000/ws/projects/$PROJECT_ID

# Poll events via REST
curl -s http://localhost:8000/projects/$PROJECT_ID/events | python -m json.tool

# Read the generated memo
curl -s http://localhost:8000/projects/$PROJECT_ID/memos | python -m json.tool
```
