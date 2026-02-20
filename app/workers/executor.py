"""Task execution pipeline.

Executes Tasks by invoking OpenClaw agents with role-appropriate tool
permissions and workspace directories. Captures artifacts produced.

Celery tasks:
  - execute_task        : run a single Task row
  - execute_action_items: batch-convert ActionItems → Tasks and execute them
"""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any

import structlog
from sqlalchemy import select

from app.agents.roles import get_role_config
from app.config import settings
from app.database import get_sync_db
from app.models import (
    ActionItem,
    ActionItemStatus,
    Agent,
    AgentRole,
    AgentStatus,
    Artifact,
    ArtifactType,
    AuthorType,
    Event,
    Message,
    Task,
    TaskSource,
    TaskStatus,
    TaskType,
    Thread,
)
from app.openclaw import get_openclaw_client
from app.openclaw.base import AgentResult
from app.workers.celery_app import celery

logger = structlog.get_logger(__name__)

# Maps action-item owner roles to likely task types (best-effort heuristic)
_ROLE_TASK_TYPE: dict[str, TaskType] = {
    "engineer": TaskType.CODE,
    "designer": TaskType.DESIGN,
    "analyst": TaskType.ANALYSIS,
    "pm": TaskType.DOCUMENT,
    "ceo": TaskType.REVIEW,
}


def _emit_event(db: Any, project_id: str, event_type: str, payload: dict) -> Event:
    event = Event(
        project_id=uuid.UUID(project_id),
        type=event_type,
        payload_json=payload,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    _publish_event(project_id, event)
    return event


def _publish_event(project_id: str, event: Event) -> None:
    try:
        import redis as redis_lib
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


def _resolve_workspace(task: Task) -> str:
    """Return the absolute workspace path for a task."""
    if task.workspace_dir:
        return os.path.expanduser(task.workspace_dir)
    return os.path.expanduser(settings.agent_workspace_dir)


def _get_agent_for_role(db: Any, project_id: str, role: AgentRole) -> Agent | None:
    result = db.execute(
        select(Agent).where(
            Agent.project_id == uuid.UUID(project_id),
            Agent.role == role,
        )
    )
    return result.scalars().first()


def _build_execution_prompt(
    role_name: str,
    task: Task,
    workspace: str,
) -> str:
    """Build a detailed execution prompt for the agent."""
    rc = get_role_config(role_name)

    parts = [
        rc.persona,
        "",
        rc.execution_preamble or "Execute the task described below.",
        "",
        f"## Task: {task.title}",
        "",
        task.description,
        "",
        f"Working directory: {workspace}",
    ]

    if rc.tools_allowed:
        parts.append(f"You have access to these tools: {', '.join(rc.tools_allowed)}")
    if rc.tools_denied:
        parts.append(f"Do NOT use these tools: {', '.join(rc.tools_denied)}")

    if rc.can_git_push:
        parts.append(
            "After making code changes, stage and commit with a clear message. "
            "Push to the remote only if the task explicitly asks for it."
        )

    parts.append(
        "\nWhen you finish, output a section '## Artifacts' listing every "
        "file you created or modified (one per line, as a file path)."
    )

    return "\n".join(parts)


def _parse_artifacts(
    db: Any,
    project_id: str,
    task_id: str,
    output: str,
    tool_logs: list[dict],
) -> list[Artifact]:
    """Extract artifacts from agent output and tool logs."""
    artifacts: list[Artifact] = []

    # 1. Parse explicit "## Artifacts" section from output
    artifact_section = re.split(r"##\s*Artifacts", output, flags=re.IGNORECASE)
    if len(artifact_section) > 1:
        for line in artifact_section[1].splitlines():
            line = line.strip().lstrip("- ").strip()
            if not line or line.startswith("#"):
                break
            path = line.split()[0] if line.split() else line
            if path:
                art = Artifact(
                    project_id=uuid.UUID(project_id),
                    task_id=uuid.UUID(task_id),
                    artifact_type=_guess_artifact_type(path),
                    path_or_url=path,
                    description=line,
                )
                db.add(art)
                artifacts.append(art)

    # 2. Detect git commits in tool logs
    for log_entry in tool_logs:
        if isinstance(log_entry, dict):
            content = json.dumps(log_entry)
            commit_match = re.search(r"([0-9a-f]{7,40})\s", content)
            if "commit" in content.lower() and commit_match:
                art = Artifact(
                    project_id=uuid.UUID(project_id),
                    task_id=uuid.UUID(task_id),
                    artifact_type=ArtifactType.COMMIT,
                    path_or_url=commit_match.group(1),
                    description="Git commit detected in tool logs",
                    metadata_json=log_entry,
                )
                db.add(art)
                artifacts.append(art)

    if artifacts:
        db.commit()

    return artifacts


def _guess_artifact_type(path: str) -> ArtifactType:
    if path.startswith("http://") or path.startswith("https://"):
        return ArtifactType.URL
    ext = os.path.splitext(path)[1].lower()
    if ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"):
        return ArtifactType.IMAGE
    if ext in (".md", ".txt", ".pdf", ".doc", ".docx"):
        return ArtifactType.DOCUMENT
    return ArtifactType.FILE


@celery.task(name="app.workers.executor.execute_task", bind=True, max_retries=1)
def execute_task(self, task_id: str) -> dict[str, Any]:
    """Execute a single Task by invoking the appropriate OpenClaw agent."""
    db = get_sync_db()
    client = get_openclaw_client()

    try:
        task = db.get(Task, uuid.UUID(task_id))
        if not task:
            return {"status": "error", "error": "Task not found"}

        project_id = str(task.project_id)
        role_name = task.agent_role.value
        rc = get_role_config(role_name)
        workspace = _resolve_workspace(task)

        # Mark task running
        task.status = TaskStatus.RUNNING
        db.commit()

        _emit_event(db, project_id, "TASK_STARTED", {
            "task_id": task_id,
            "title": task.title,
            "role": role_name,
            "workspace": workspace,
        })

        # Find the project agent for status tracking
        agent = _get_agent_for_role(db, project_id, task.agent_role)
        if agent:
            agent.status = AgentStatus.RUNNING
            db.commit()

        # Build prompt and invoke
        instruction = _build_execution_prompt(role_name, task, workspace)
        extra_config = {}
        if agent and agent.config_json:
            extra_config = dict(agent.config_json)
            extra_config.pop("tool_profile", None)
            extra_config.pop("model", None)

        result: AgentResult = client.run_agent(
            role=role_name,
            instruction=instruction,
            context=task.description,
            tool_profile=rc.tool_profile,
            tool_allow=list(rc.tools_allowed),
            tool_deny=list(rc.tools_denied),
            workspace_dir=workspace,
            model=extra_config.pop("model", "") if extra_config else "",
            extra_config=extra_config,
        )

        # Update agent status
        if agent:
            agent.status = AgentStatus.IDLE if result.success else AgentStatus.ERROR
            db.commit()

        # Parse artifacts
        artifacts = _parse_artifacts(
            db, project_id, task_id, result.output, result.tool_logs,
        )

        # Update task
        task.status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
        task.result_summary = result.output[:4000] if result.output else result.error
        task.completed_at = datetime.now(timezone.utc)
        db.commit()

        _emit_event(db, project_id, "TASK_COMPLETED", {
            "task_id": task_id,
            "status": task.status.value,
            "success": result.success,
            "artifact_count": len(artifacts),
            "output_preview": result.output[:500],
            "error": result.error or None,
        })

        return {
            "status": task.status.value,
            "task_id": task_id,
            "artifacts": len(artifacts),
        }

    except Exception as exc:
        logger.exception("execute_task_failed", task_id=task_id)
        try:
            task = db.get(Task, uuid.UUID(task_id))
            if task:
                task.status = TaskStatus.FAILED
                task.result_summary = str(exc)[:2000]
                task.completed_at = datetime.now(timezone.utc)
                db.commit()
                _emit_event(db, str(task.project_id), "TASK_FAILED", {
                    "task_id": task_id,
                    "error": str(exc),
                })
        except Exception:
            pass
        raise self.retry(exc=exc, countdown=30)
    finally:
        db.close()


@celery.task(name="app.workers.executor.execute_action_items", bind=True)
def execute_action_items(self, project_id: str, thread_id: str | None = None) -> dict[str, Any]:
    """Convert open ActionItems into Tasks and execute them sequentially."""
    db = get_sync_db()

    try:
        query = select(ActionItem).where(
            ActionItem.project_id == uuid.UUID(project_id),
            ActionItem.status == ActionItemStatus.OPEN,
        )
        items = db.execute(query).scalars().all()

        if not items:
            return {"status": "no_items", "count": 0}

        _emit_event(db, project_id, "EXECUTION_BATCH_STARTED", {
            "action_item_count": len(items),
            "thread_id": thread_id,
        })

        task_ids: list[str] = []

        for item in items:
            role_str = item.owner_role.value
            task_type = _ROLE_TASK_TYPE.get(role_str, TaskType.DOCUMENT)

            task = Task(
                project_id=uuid.UUID(project_id),
                agent_role=item.owner_role,
                title=f"Execute: {item.description[:80]}",
                description=item.description,
                task_type=task_type,
                status=TaskStatus.PENDING,
                source=TaskSource.MEETING,
                action_item_id=item.id,
                workspace_dir=settings.agent_workspace_dir,
            )
            db.add(task)
            db.commit()
            db.refresh(task)

            item.status = ActionItemStatus.IN_PROGRESS
            db.commit()

            tid = str(task.id)
            task_ids.append(tid)

            # Execute synchronously within this worker to maintain ordering
            execute_task(tid)

            # Mark the action item done
            db.refresh(item)
            item.status = ActionItemStatus.DONE
            db.commit()

        _emit_event(db, project_id, "EXECUTION_BATCH_COMPLETED", {
            "tasks_executed": len(task_ids),
            "task_ids": task_ids,
        })

        # Write execution summary as a message if we have a thread
        if thread_id:
            summary_parts = [f"**Execution complete.** {len(task_ids)} tasks executed:"]
            for tid in task_ids:
                t = db.get(Task, uuid.UUID(tid))
                if t:
                    status_icon = "done" if t.status == TaskStatus.COMPLETED else "failed"
                    summary_parts.append(f"- [{status_icon}] {t.title}")
            summary = "\n".join(summary_parts)
            msg = Message(
                thread_id=uuid.UUID(thread_id),
                author_type=AuthorType.SYSTEM,
                content=summary,
            )
            db.add(msg)
            db.commit()

        return {"status": "completed", "tasks_executed": len(task_ids)}

    except Exception as exc:
        logger.exception("execute_action_items_failed", project_id=project_id)
        _emit_event(db, project_id, "EXECUTION_BATCH_FAILED", {"error": str(exc)})
        raise
    finally:
        db.close()
