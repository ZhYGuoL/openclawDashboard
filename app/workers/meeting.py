"""Multi-agent meeting orchestration pipeline.

Rounds:
  0 — Context ingestion (system summarises user prompt + project state)
  1 — PM proposes feature ideas + PRD outline
  2 — Engineer critiques feasibility, risks, estimates
  3 — Designer critiques UX, suggests flows
  4 — Analyst defines metrics / experiments
  5 — PM reconciles into decisions + action items
  Final — Memo writer generates the investor-style memo
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any

import structlog
from sqlalchemy import select

from app.database import get_sync_db
from app.models import (
    ActionItem,
    ActionItemStatus,
    Agent,
    AgentRole,
    AgentStatus,
    AuthorType,
    Decision,
    DecisionStatus,
    Event,
    Memo,
    Message,
    Thread,
)
from app.openclaw import get_openclaw_client
from app.openclaw.base import AgentResult
from app.workers.celery_app import celery

logger = structlog.get_logger(__name__)

ROUND_CONFIG: list[dict[str, Any]] = [
    {
        "round": 0,
        "label": "Context Ingestion",
        "role": None,
        "instruction_template": (
            "Summarise the following user prompt and any existing project context "
            "into a concise brief that the product team can work from.\n\n"
            "User prompt: {prompt}\n\n"
            "Project context: {context}"
        ),
    },
    {
        "round": 1,
        "label": "PM — Feature Proposal & PRD",
        "role": AgentRole.PM,
        "instruction_template": (
            "You are the Product Manager. Based on the brief below, propose "
            "concrete feature ideas and write a PRD outline covering: problem, "
            "goals, user stories, scope, and open questions.\n\n"
            "Brief:\n{context}"
        ),
    },
    {
        "round": 2,
        "label": "Engineer — Feasibility & Risks",
        "role": AgentRole.ENGINEER,
        "instruction_template": (
            "You are the Staff Engineer. Review the PM's proposal below and "
            "provide a feasibility analysis: technical risks, architecture "
            "concerns, effort estimates, dependencies, and trade-offs.\n\n"
            "PM Proposal:\n{context}"
        ),
    },
    {
        "round": 3,
        "label": "Designer — UX Critique & Flows",
        "role": AgentRole.DESIGNER,
        "instruction_template": (
            "You are the Lead Designer. Review the discussion so far and "
            "critique the UX: user flows, accessibility, information architecture, "
            "visual design considerations, and potential usability issues.\n\n"
            "Discussion:\n{context}"
        ),
    },
    {
        "round": 4,
        "label": "Analyst — Metrics & Experiments",
        "role": AgentRole.ANALYST,
        "instruction_template": (
            "You are the Data Analyst. Based on the discussion, define success "
            "metrics, KPIs, experiment designs (A/B tests), and data requirements.\n\n"
            "Discussion:\n{context}"
        ),
    },
    {
        "round": 5,
        "label": "PM — Reconciliation",
        "role": AgentRole.PM,
        "instruction_template": (
            "You are the Product Manager wrapping up. Synthesize all feedback "
            "into:\n"
            "1. DECISIONS (format each as 'DECISION: <title> | <rationale>')\n"
            "2. ACTION_ITEMS (format each as 'ACTION: <owner_role> | <description>')\n\n"
            "Discussion:\n{context}"
        ),
    },
]


def _emit_event(
    db: Any,
    project_id: str,
    event_type: str,
    payload: dict[str, Any],
) -> Event:
    event = Event(
        project_id=uuid.UUID(project_id),
        type=event_type,
        payload_json=payload,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    _publish_event_to_redis(project_id, event)
    return event


def _publish_event_to_redis(project_id: str, event: Event) -> None:
    """Push event to Redis pub/sub so WebSocket subscribers get it."""
    try:
        import redis as redis_lib
        from app.config import settings

        r = redis_lib.Redis.from_url(settings.redis_url)
        r.publish(
            f"project:{project_id}:events",
            json.dumps({
                "id": str(event.id),
                "type": event.type,
                "payload_json": event.payload_json,
                "created_at": event.created_at.isoformat() if event.created_at else None,
            }),
        )
    except Exception as exc:
        logger.warning("redis_publish_failed", error=str(exc))


def _add_message(
    db: Any,
    thread_id: str,
    author_type: AuthorType,
    content: str,
    author_agent_id: str | None = None,
) -> Message:
    msg = Message(
        thread_id=uuid.UUID(thread_id),
        author_type=author_type,
        author_agent_id=uuid.UUID(author_agent_id) if author_agent_id else None,
        content=content,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def _get_agent_for_role(db: Any, project_id: str, role: AgentRole) -> Agent | None:
    result = db.execute(
        select(Agent).where(
            Agent.project_id == uuid.UUID(project_id),
            Agent.role == role,
        )
    )
    return result.scalars().first()


def _set_agent_status(db: Any, agent: Agent, status: AgentStatus) -> None:
    agent.status = status
    db.add(agent)
    db.commit()


def _build_context(messages: list[str], max_chars: int = 12000) -> str:
    combined = "\n\n---\n\n".join(messages)
    if len(combined) > max_chars:
        combined = combined[-max_chars:]
    return combined


def _parse_decisions(
    db: Any,
    project_id: str,
    thread_id: str,
    text: str,
) -> list[Decision]:
    """Extract DECISION lines from PM reconciliation output."""
    decisions = []
    for match in re.finditer(r"DECISION:\s*(.+?)\s*\|\s*(.+)", text):
        d = Decision(
            project_id=uuid.UUID(project_id),
            thread_id=uuid.UUID(thread_id),
            title=match.group(1).strip(),
            rationale=match.group(2).strip(),
            status=DecisionStatus.PROPOSED,
        )
        db.add(d)
        decisions.append(d)
    if decisions:
        db.commit()
    return decisions


def _parse_action_items(
    db: Any,
    project_id: str,
    text: str,
) -> list[ActionItem]:
    """Extract ACTION lines from PM reconciliation output."""
    role_map = {
        "pm": AgentRole.PM,
        "engineer": AgentRole.ENGINEER,
        "designer": AgentRole.DESIGNER,
        "analyst": AgentRole.ANALYST,
    }
    items = []
    for match in re.finditer(r"ACTION:\s*(\w+)\s*\|\s*(.+)", text):
        role_str = match.group(1).strip().lower()
        role = role_map.get(role_str, AgentRole.PM)
        ai = ActionItem(
            project_id=uuid.UUID(project_id),
            owner_role=role,
            description=match.group(2).strip(),
            status=ActionItemStatus.OPEN,
        )
        db.add(ai)
        items.append(ai)
    if items:
        db.commit()
    return items


@celery.task(name="app.workers.meeting.run_meeting_pipeline", bind=True, max_retries=1)
def run_meeting_pipeline(self, project_id: str, thread_id: str, prompt: str) -> dict[str, Any]:
    db = get_sync_db()
    client = get_openclaw_client()
    round_outputs: list[str] = []

    _emit_event(db, project_id, "SESSION_STARTED", {
        "thread_id": thread_id,
        "prompt": prompt,
    })

    _add_message(db, thread_id, AuthorType.USER, prompt)

    try:
        for rc in ROUND_CONFIG:
            round_num = rc["round"]
            label = rc["label"]
            role: AgentRole | None = rc["role"]

            _emit_event(db, project_id, "ROUND_STARTED", {
                "round": round_num,
                "label": label,
                "role": role.value if role else "system",
            })

            context = _build_context([prompt] + round_outputs)
            instruction = rc["instruction_template"].format(
                prompt=prompt,
                context=context,
            )

            agent: Agent | None = None
            agent_id_str: str | None = None

            if role:
                agent = _get_agent_for_role(db, project_id, role)
                if agent:
                    agent_id_str = str(agent.id)
                    _set_agent_status(db, agent, AgentStatus.RUNNING)

            extra_config = {}
            if agent and agent.config_json:
                extra_config = agent.config_json

            tool_profile = extra_config.pop("tool_profile", "full")
            model = extra_config.pop("model", "")

            result: AgentResult = client.run_agent(
                role=role.value if role else "system",
                instruction=instruction,
                context=context,
                tool_profile=tool_profile,
                model=model,
                extra_config=extra_config,
            )

            if agent:
                _set_agent_status(
                    db, agent,
                    AgentStatus.IDLE if result.success else AgentStatus.ERROR,
                )

            _emit_event(db, project_id, "AGENT_RESPONSE", {
                "round": round_num,
                "role": role.value if role else "system",
                "agent_id": agent_id_str,
                "success": result.success,
                "output_preview": result.output[:500],
                "tool_logs": result.tool_logs[:20],
                "error": result.error or None,
            })

            author_type = AuthorType.AGENT if role else AuthorType.SYSTEM
            _add_message(db, thread_id, author_type, result.output, agent_id_str)
            round_outputs.append(f"[{label}]\n{result.output}")

            if round_num == 5 and result.success:
                _parse_decisions(db, project_id, thread_id, result.output)
                _parse_action_items(db, project_id, result.output)

            _emit_event(db, project_id, "ROUND_ENDED", {
                "round": round_num,
                "label": label,
            })

        # Final: generate memo
        memo_content = _generate_memo(db, client, project_id, thread_id, prompt, round_outputs)

        _emit_event(db, project_id, "SESSION_COMPLETED", {
            "thread_id": thread_id,
            "memo_generated": bool(memo_content),
        })

        return {"status": "completed", "thread_id": thread_id}

    except Exception as exc:
        logger.exception("meeting_pipeline_failed", project_id=project_id)
        _emit_event(db, project_id, "SESSION_FAILED", {
            "thread_id": thread_id,
            "error": str(exc),
        })
        raise self.retry(exc=exc, countdown=30)
    finally:
        db.close()


def _generate_memo(
    db: Any,
    client: Any,
    project_id: str,
    thread_id: str,
    prompt: str,
    round_outputs: list[str],
) -> str:
    """Run the memo-writer agent to produce an investor-style memo."""
    context = _build_context(round_outputs, max_chars=16000)

    instruction = (
        "You are the Memo Writer. Produce an investor-style memo in Markdown "
        "summarizing what the product team discussed and decided. Use this exact structure:\n\n"
        "# <Title> — <date>\n\n"
        "## Executive Summary\n"
        "- (5 bullet points)\n\n"
        "## What We Decided\n"
        "(List each decision with rationale)\n\n"
        "## What We Considered\n"
        "(Alternatives and tradeoffs discussed)\n\n"
        "## Risks & Unknowns\n"
        "(Key risks identified)\n\n"
        "## Next Steps\n"
        "(Action items with owner roles)\n\n"
        "## Metrics to Watch\n"
        "(KPIs and success metrics)\n\n"
        "---\n\n"
        f"Original prompt: {prompt}\n\n"
        f"Discussion transcript:\n{context}"
    )

    _emit_event(db, project_id, "MEMO_GENERATION_STARTED", {"thread_id": thread_id})

    result = client.run_agent(
        role="memo_writer",
        instruction=instruction,
        context=context,
    )

    if not result.success:
        logger.error("memo_generation_failed", error=result.error)
        _emit_event(db, project_id, "MEMO_GENERATION_FAILED", {"error": result.error})
        return ""

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    title = f"Product Team Memo — {today}"

    memo = Memo(
        project_id=uuid.UUID(project_id),
        title=title,
        content_markdown=result.output,
    )
    db.add(memo)
    db.commit()
    db.refresh(memo)

    _add_message(db, thread_id, AuthorType.SYSTEM, f"Memo generated: {title}")

    _emit_event(db, project_id, "MEMO_GENERATION_COMPLETED", {
        "memo_id": str(memo.id),
        "title": title,
    })

    return result.output
