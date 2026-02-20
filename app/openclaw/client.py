"""Unified OpenClaw client.

Usage from anywhere in the codebase::

    from app.openclaw import get_openclaw_client

    client = get_openclaw_client()
    result = client.run_agent(role="pm", instruction="...", context="...")

To swap between CLI and API adapters, edit ``_create_adapter()`` below.
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog

from app.config import settings
from app.openclaw.base import AgentInvocation, AgentResult, OpenClawAdapter
from app.openclaw.cli_adapter import CLIAdapter

logger = structlog.get_logger(__name__)


def _create_adapter() -> OpenClawAdapter:
    """Instantiate the concrete adapter.

    SWAP POINT: To use the future Python API adapter, change this to::

        from app.openclaw.api_adapter import APIAdapter
        return APIAdapter(gateway_url=settings.openclaw_gateway_url,
                          token=settings.openclaw_gateway_token)
    """
    return CLIAdapter(
        bin_path=settings.openclaw_bin,
        gateway_url=settings.openclaw_gateway_url,
        gateway_token=settings.openclaw_gateway_token,
        profile=settings.openclaw_profile,
    )


class OpenClawClient:
    """High-level wrapper around the OpenClaw adapter."""

    def __init__(self, adapter: OpenClawAdapter | None = None):
        self.adapter = adapter or _create_adapter()

    def run_agent(
        self,
        *,
        role: str,
        instruction: str,
        context: str = "",
        session_id: str | None = None,
        tool_profile: str = "full",
        tool_allow: list[str] | None = None,
        tool_deny: list[str] | None = None,
        model: str = "",
        timeout_seconds: int | None = None,
        workspace_dir: str = "",
        extra_config: dict[str, Any] | None = None,
    ) -> AgentResult:
        invocation = AgentInvocation(
            role=role,
            instruction=instruction,
            context=context,
            session_id=session_id or str(uuid.uuid4()),
            tool_profile=tool_profile,
            tool_allow=tool_allow or [],
            tool_deny=tool_deny or [],
            model=model,
            timeout_seconds=timeout_seconds or settings.openclaw_timeout_seconds,
            workspace_dir=workspace_dir,
            extra_config=extra_config or {},
        )
        logger.info("openclaw_run_agent", role=role, session_id=invocation.session_id)
        result = self.adapter.invoke(invocation)

        if not result.success:
            logger.error("openclaw_agent_failed", role=role, error=result.error)

        return result

    def health_check(self) -> bool:
        return self.adapter.health_check()


_client: OpenClawClient | None = None


def get_openclaw_client() -> OpenClawClient:
    global _client
    if _client is None:
        _client = OpenClawClient()
    return _client
