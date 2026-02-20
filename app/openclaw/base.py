"""Abstract adapter interface for OpenClaw agent invocation.

To swap between CLI and future Python API adapters, change the concrete
class instantiated in ``client.py``.  Both adapters implement the same
``invoke`` contract so the rest of the codebase is adapter-agnostic.
"""

from __future__ import annotations

import abc
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AgentInvocation:
    """Parameters for a single OpenClaw agent turn."""

    role: str
    instruction: str
    context: str = ""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tool_profile: str = "full"
    tool_allow: list[str] = field(default_factory=list)
    tool_deny: list[str] = field(default_factory=list)
    model: str = ""
    timeout_seconds: int = 120
    workspace_dir: str = ""
    extra_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from an OpenClaw agent turn."""

    output: str
    raw_stdout: str = ""
    raw_stderr: str = ""
    exit_code: int = 0
    tool_logs: list[dict[str, Any]] = field(default_factory=list)
    session_id: str = ""
    success: bool = True
    error: str = ""


class OpenClawAdapter(abc.ABC):
    """Abstract base for OpenClaw integration adapters."""

    @abc.abstractmethod
    def invoke(self, invocation: AgentInvocation) -> AgentResult:
        """Run a single agent turn synchronously and return the result."""
        ...

    @abc.abstractmethod
    def health_check(self) -> bool:
        """Return True if the OpenClaw runtime is reachable."""
        ...
