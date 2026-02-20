from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://dashboard:dashboard@localhost:5432/openclaw_dashboard"
    database_url_sync: str = "postgresql://dashboard:dashboard@localhost:5432/openclaw_dashboard"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    openclaw_bin: str = "openclaw"
    openclaw_gateway_url: str = "ws://127.0.0.1:18789"
    openclaw_gateway_token: str = ""
    openclaw_workspace: str = "~/.openclaw/workspace"
    openclaw_timeout_seconds: int = 120
    openclaw_profile: str = ""

    agent_workspace_dir: str = "."

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "info"


settings = Settings()
