# Dashboard Commands Reference

## Setup (one-time)

```bash
make local-setup          # Install Python deps + create .env
make local-db             # Create Postgres user + database (prompts for postgres password)
make local-migrate        # Run Alembic migrations
make local-seed           # Seed demo project with 4 agents
```

## Run the Stack (two terminals)

```bash
# Terminal 1 — API server
make local-api

# Terminal 2 — Celery worker (runs the agents)
make local-worker
```

## Start a Meeting Session

```bash
curl -X POST http://localhost:8000/projects/PROJECT_ID/sessions \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "YOUR PROMPT HERE", "thread_title": "Meeting Title"}'
```

## View Results

```bash
# View the generated memo (clean markdown)
curl -s http://localhost:8000/projects/PROJECT_ID/memos | python -m json.tool

# Read a specific memo by ID
curl -s http://localhost:8000/memos/MEMO_ID | python -m json.tool

# View the event timeline (all rounds, start/end, agent responses)
curl -s http://localhost:8000/projects/PROJECT_ID/events | python -m json.tool

# View all messages in a thread (the full conversation)
curl -s http://localhost:8000/threads/THREAD_ID/messages | python -m json.tool

# List all agents in a project
curl -s http://localhost:8000/projects/PROJECT_ID/agents | python -m json.tool
```

## Create Resources

```bash
# Create a new project
curl -X POST http://localhost:8000/projects \
  -H 'Content-Type: application/json' \
  -d '{"name": "My Project"}'

# Add an agent to a project
curl -X POST http://localhost:8000/projects/PROJECT_ID/agents \
  -H 'Content-Type: application/json' \
  -d '{"role": "pm", "name": "Alice (PM)", "config_json": {"tool_profile": "full"}}'

# Create a thread
curl -X POST http://localhost:8000/projects/PROJECT_ID/threads \
  -H 'Content-Type: application/json' \
  -d '{"title": "Sprint Planning"}'

# Post a user message to a thread
curl -X POST http://localhost:8000/threads/THREAD_ID/messages \
  -H 'Content-Type: application/json' \
  -d '{"content": "I think we should focus on mobile first."}'
```

## Real-time Event Stream (WebSocket)

```bash
# Requires: brew install websocat
websocat ws://localhost:8000/ws/projects/PROJECT_ID
```

## Save Latest Memo as Markdown File

```bash
curl -s http://localhost:8000/projects/PROJECT_ID/memos | python3 -c "
import sys, json
memos = json.load(sys.stdin)
if not memos:
    print('No memos found.')
    sys.exit(1)
memo = memos[0]
filename = memo['title'].replace(' ', '_').replace('—', '-') + '.md'
with open(filename, 'w') as f:
    f.write(memo['content_markdown'])
print(f'Saved: {filename}')
"
```

## Health Check

```bash
curl http://localhost:8000/health
```

## Interactive API Docs

Open in browser: **http://localhost:8000/docs**

## OpenClaw Commands

```bash
openclaw health           # Check if Gateway is running
openclaw models status    # Check configured model + auth
openclaw --version        # Print version
```

## Your Demo Project ID

```
9b7d36e6-b590-49f6-8439-2d702ac5a9f6
```
