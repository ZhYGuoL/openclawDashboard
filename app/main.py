from __future__ import annotations

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import agents, events, memos, projects, sessions, threads
from app.websocket import router as ws_router

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

app = FastAPI(
    title="AI Product Team Dashboard",
    description="Multi-agent dashboard powered by OpenClaw",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(agents.router)
app.include_router(threads.router)
app.include_router(sessions.router)
app.include_router(memos.router)
app.include_router(events.router)
app.include_router(ws_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
