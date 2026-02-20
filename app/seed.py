"""Demo seed script.

Creates a sample project with 4 agents and one thread.
Run via: ``python -m app.seed`` or ``make seed``.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.database import sync_engine, sync_session_factory
from app.models import (
    Agent,
    AgentRole,
    AuthorType,
    Base,
    Event,
    Message,
    Project,
    Thread,
)


def seed() -> None:
    with sync_session_factory() as db:
        existing = db.query(Project).filter(Project.name == "Demo Product").first()
        if existing:
            print(f"Seed already exists: project {existing.id}")
            return

        project = Project(name="Demo Product")
        db.add(project)
        db.flush()

        agents_data = [
            {
                "role": AgentRole.CEO,
                "name": "Eve (CEO)",
                "config_json": {
                    "tool_profile": "full",
                    "model": "",
                    "persona": "Startup CEO focused on strategy, prioritization, and shipping fast.",
                },
            },
            {
                "role": AgentRole.PM,
                "name": "Alice (PM)",
                "config_json": {
                    "tool_profile": "full",
                    "model": "",
                    "persona": "Senior Product Manager focused on user outcomes and business impact.",
                },
            },
            {
                "role": AgentRole.ENGINEER,
                "name": "Bob (Engineer)",
                "config_json": {
                    "tool_profile": "coding",
                    "model": "",
                    "persona": "Staff Engineer focused on architecture, scalability, and technical debt.",
                },
            },
            {
                "role": AgentRole.DESIGNER,
                "name": "Carol (Designer)",
                "config_json": {
                    "tool_profile": "full",
                    "model": "",
                    "persona": "Lead Designer focused on UX, accessibility, and design systems.",
                },
            },
            {
                "role": AgentRole.ANALYST,
                "name": "Dave (Analyst)",
                "config_json": {
                    "tool_profile": "full",
                    "model": "",
                    "persona": "Data Analyst focused on metrics, experiments, and data-driven decisions.",
                },
            },
        ]

        for ad in agents_data:
            agent = Agent(project_id=project.id, **ad)
            db.add(agent)

        thread = Thread(project_id=project.id, title="Sprint Planning")
        db.add(thread)
        db.flush()

        welcome = Message(
            thread_id=thread.id,
            author_type=AuthorType.SYSTEM,
            content="Welcome to Sprint Planning. Start a work session to kick off the meeting.",
        )
        db.add(welcome)

        event = Event(
            project_id=project.id,
            type="PROJECT_SEEDED",
            payload_json={"agents": [a["name"] for a in agents_data]},
        )
        db.add(event)

        db.commit()

        print(f"Seeded project: {project.id}")
        print(f"Thread: {thread.id}")
        print()
        print("Sample 'start session' (discuss only):")
        print(f'  POST http://localhost:8000/projects/{project.id}/sessions')
        print('  {"prompt": "Build a notification system", "thread_title": "Sprint Planning"}')
        print()
        print("Sample 'start session' (discuss + auto-execute):")
        print(f'  POST http://localhost:8000/projects/{project.id}/sessions')
        print('  {"prompt": "Build a notification system", "auto_execute": true}')
        print()
        print("Sample 'direct task' (skip meeting, just do it):")
        print(f'  POST http://localhost:8000/projects/{project.id}/tasks')
        print('  {"agent_role": "engineer", "title": "Add health check endpoint",')
        print('   "description": "Add GET /healthz returning JSON status", "task_type": "code"}')
        print()
        print("Then execute: POST http://localhost:8000/tasks/<TASK_ID>/execute")


if __name__ == "__main__":
    seed()
