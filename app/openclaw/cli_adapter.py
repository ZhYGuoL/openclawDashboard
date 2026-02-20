"""OpenClaw CLI subprocess adapter.

Invokes ``openclaw agent --message <prompt> --json`` as a subprocess,
parses the JSON output, and returns a structured ``AgentResult``.

This is the production adapter when OpenClaw is installed on the host
or accessible inside the Docker container.
"""

from __future__ import annotations

import json
import subprocess
import structlog
from typing import Any

from app.config import settings
from app.openclaw.base import AgentInvocation, AgentResult, OpenClawAdapter

logger = structlog.get_logger(__name__)


class CLIAdapter(OpenClawAdapter):
    """Invoke OpenClaw via its CLI binary."""

    def __init__(
        self,
        bin_path: str = "",
        gateway_url: str = "",
        gateway_token: str = "",
        profile: str = "",
    ):
        self.bin = bin_path or settings.openclaw_bin
        self.gateway_url = gateway_url or settings.openclaw_gateway_url
        self.gateway_token = gateway_token or settings.openclaw_gateway_token
        self.profile = profile or settings.openclaw_profile

    def _base_cmd(self) -> list[str]:
        cmd = [self.bin]
        if self.profile:
            cmd += ["--profile", self.profile]
        return cmd

    def _build_message(self, invocation: AgentInvocation) -> str:
        """Build the full prompt sent to the agent, combining role instruction and context."""
        parts: list[str] = []
        parts.append(f"[Role: {invocation.role}]")
        if invocation.context:
            parts.append(f"[Context]\n{invocation.context}")
        parts.append(f"[Instruction]\n{invocation.instruction}")
        return "\n\n".join(parts)

    def invoke(self, invocation: AgentInvocation) -> AgentResult:
        message = self._build_message(invocation)

        cmd = self._base_cmd() + [
            "agent",
            "--message", message,
            "--json",
            "--local",
            "--session-id", invocation.session_id,
        ]

        if invocation.timeout_seconds:
            cmd += ["--timeout", str(invocation.timeout_seconds)]

        logger.info(
            "openclaw_cli_invoke",
            role=invocation.role,
            session_id=invocation.session_id,
            timeout=invocation.timeout_seconds,
        )

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=invocation.timeout_seconds + 30,
                cwd=None,
            )
        except subprocess.TimeoutExpired:
            logger.error("openclaw_cli_timeout", session_id=invocation.session_id)
            return AgentResult(
                output="",
                exit_code=-1,
                success=False,
                error="OpenClaw CLI timed out",
                session_id=invocation.session_id,
            )
        except FileNotFoundError:
            logger.error("openclaw_cli_not_found", bin=self.bin)
            return AgentResult(
                output="",
                exit_code=-1,
                success=False,
                error=f"OpenClaw binary not found at '{self.bin}'",
                session_id=invocation.session_id,
            )

        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()

        if proc.returncode != 0:
            logger.error(
                "openclaw_cli_error",
                exit_code=proc.returncode,
                stderr=stderr[:500],
            )
            return AgentResult(
                output=stdout,
                raw_stdout=stdout,
                raw_stderr=stderr,
                exit_code=proc.returncode,
                success=False,
                error=stderr or f"Process exited with code {proc.returncode}",
                session_id=invocation.session_id,
            )

        output_text, tool_logs = self._parse_output(stdout)

        logger.info(
            "openclaw_cli_success",
            session_id=invocation.session_id,
            output_len=len(output_text),
            tool_log_count=len(tool_logs),
        )

        return AgentResult(
            output=output_text,
            raw_stdout=stdout,
            raw_stderr=stderr,
            exit_code=0,
            tool_logs=tool_logs,
            session_id=invocation.session_id,
            success=True,
        )

    def _parse_output(self, stdout: str) -> tuple[str, list[dict[str, Any]]]:
        """Parse JSON output from ``openclaw agent --json``.

        OpenClaw emits a JSON object with structure::

            {"payloads": [{"text": "...", "mediaUrl": ...}], "meta": {...}}

        We extract the text from each payload and capture meta as a tool log.
        Falls back to line-by-line JSONL parsing if the top-level parse fails.
        """
        tool_logs: list[dict[str, Any]] = []
        text_parts: list[str] = []

        # Strategy 1: try parsing the entire stdout as one JSON object
        # (OpenClaw's native --json format)
        try:
            obj = json.loads(stdout)
            if isinstance(obj, dict) and "payloads" in obj:
                for payload in obj["payloads"]:
                    if isinstance(payload, dict) and payload.get("text"):
                        text_parts.append(payload["text"])
                if obj.get("meta"):
                    tool_logs.append({"type": "openclaw_meta", **obj["meta"]})
                if text_parts:
                    return "\n".join(text_parts), tool_logs
        except json.JSONDecodeError:
            pass

        # Strategy 2: line-by-line JSONL fallback
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                text_parts.append(line)
                continue

            if isinstance(obj, dict):
                if "payloads" in obj:
                    for payload in obj["payloads"]:
                        if isinstance(payload, dict) and payload.get("text"):
                            text_parts.append(payload["text"])
                    if obj.get("meta"):
                        tool_logs.append({"type": "openclaw_meta", **obj["meta"]})
                elif obj.get("role") in ("assistant", "text"):
                    text_parts.append(obj.get("content") or obj.get("text", ""))
                elif obj.get("role") in ("tool_use", "tool_result", "tool_call", "tool"):
                    tool_logs.append(obj)
                elif "output" in obj:
                    text_parts.append(str(obj["output"]))
                elif "message" in obj and isinstance(obj["message"], str):
                    text_parts.append(obj["message"])
                else:
                    tool_logs.append(obj)

        output = "\n".join(text_parts) if text_parts else stdout
        return output, tool_logs

    def health_check(self) -> bool:
        try:
            proc = subprocess.run(
                self._base_cmd() + ["health", "--json"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            return proc.returncode == 0
        except Exception:
            return False
