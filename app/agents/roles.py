"""Per-role tool permissions, personas, and execution instructions.

This is the single source of truth for what each agent role can do.
The execution pipeline reads these configs when invoking OpenClaw agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RoleConfig:
    """Capability profile for an agent role."""

    persona: str
    tools_allowed: list[str] = field(default_factory=list)
    tools_denied: list[str] = field(default_factory=list)
    tool_profile: str = "full"
    execution_preamble: str = ""
    can_modify_files: bool = False
    can_run_commands: bool = False
    can_git_push: bool = False


ROLE_CONFIGS: dict[str, RoleConfig] = {
    "ceo": RoleConfig(
        persona=(
            "You are the CEO / Chief Product Officer. You make final go/no-go "
            "decisions, set priorities, and ensure the team ships the right thing. "
            "You do NOT write code or designs yourself."
        ),
        tools_allowed=["read", "web_search"],
        tools_denied=["edit", "write", "exec"],
        tool_profile="full",
        execution_preamble=(
            "Review the decisions and action items below. For each decision, "
            "output APPROVED or REJECTED with a one-line rationale. "
            "Re-prioritize action items if needed. Be decisive and concise."
        ),
    ),
    "pm": RoleConfig(
        persona=(
            "You are a Senior Product Manager. You write PRDs, research "
            "competitors, define requirements, and create documentation."
        ),
        tools_allowed=["read", "write", "web_search"],
        tools_denied=["exec"],
        tool_profile="full",
        execution_preamble=(
            "Execute the task below by creating or updating documentation, "
            "specs, or research artifacts. Write files to the workspace."
        ),
        can_modify_files=True,
    ),
    "engineer": RoleConfig(
        persona=(
            "You are a Staff Software Engineer. You write production-quality "
            "code, run tests, and manage git operations."
        ),
        tools_allowed=["read", "edit", "write", "exec"],
        tool_profile="coding",
        execution_preamble=(
            "Execute the task below by writing or modifying code. "
            "After making changes, run any relevant tests. "
            "Stage and commit your changes with a clear commit message. "
            "Push to the remote if the task requires it."
        ),
        can_modify_files=True,
        can_run_commands=True,
        can_git_push=True,
    ),
    "designer": RoleConfig(
        persona=(
            "You are a Lead Product Designer. You create UI/UX designs, "
            "HTML/CSS mockups, component specs, and design system documentation."
        ),
        tools_allowed=["read", "edit", "write", "canvas", "browser"],
        tools_denied=["exec"],
        tool_profile="full",
        execution_preamble=(
            "Execute the task below by creating design artifacts: "
            "HTML/CSS mockups, component specifications, wireframe descriptions, "
            "or design system documentation. Write files to the workspace."
        ),
        can_modify_files=True,
    ),
    "analyst": RoleConfig(
        persona=(
            "You are a Senior Data Analyst. You run queries, build analysis "
            "reports, define metrics, and create data-driven recommendations."
        ),
        tools_allowed=["read", "write", "exec", "web_search"],
        tool_profile="full",
        execution_preamble=(
            "Execute the task below by running analysis, writing queries, "
            "or creating reports. Save outputs as files in the workspace."
        ),
        can_modify_files=True,
        can_run_commands=True,
    ),
    "memo_writer": RoleConfig(
        persona=(
            "You are an executive memo writer. You synthesize discussions "
            "into clear, investor-grade memos."
        ),
        tools_allowed=["read"],
        tools_denied=["edit", "write", "exec"],
        tool_profile="full",
    ),
}


def get_role_config(role: str) -> RoleConfig:
    """Return the config for a role, falling back to a minimal default."""
    return ROLE_CONFIGS.get(role, RoleConfig(persona=f"You are acting as {role}."))
