"""Future OpenClaw Python API adapter (stub).

When OpenClaw ships a first-party Python SDK or HTTP/WebSocket API,
replace this stub with real calls.  The interface matches ``CLIAdapter``
exactly so the rest of the codebase requires zero changes — just swap
the adapter in ``client.py``.

SWAP POINT: change ``_create_adapter()`` in ``client.py`` to return
``APIAdapter(...)`` instead of ``CLIAdapter(...)`` once the SDK exists.
"""

from __future__ import annotations

import structlog

from app.openclaw.base import AgentInvocation, AgentResult, OpenClawAdapter

logger = structlog.get_logger(__name__)


class APIAdapter(OpenClawAdapter):
    """Placeholder for a future OpenClaw Python SDK / HTTP API adapter."""

    def __init__(self, gateway_url: str = "", token: str = ""):
        self.gateway_url = gateway_url
        self.token = token

    def invoke(self, invocation: AgentInvocation) -> AgentResult:
        # ---------------------------------------------------------------
        # FUTURE: replace with real SDK calls, e.g.:
        #
        #   from openclaw import Client
        #   client = Client(url=self.gateway_url, token=self.token)
        #   resp = client.agent.run(
        #       message=invocation.instruction,
        #       session_id=invocation.session_id,
        #       model=invocation.model,
        #       tools={"profile": invocation.tool_profile},
        #   )
        #   return AgentResult(output=resp.text, tool_logs=resp.tool_calls, ...)
        # ---------------------------------------------------------------
        raise NotImplementedError(
            "APIAdapter is a stub.  Use CLIAdapter or implement the "
            "OpenClaw Python SDK integration here."
        )

    def health_check(self) -> bool:
        raise NotImplementedError("APIAdapter.health_check is not implemented.")
