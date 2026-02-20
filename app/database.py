from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

async_engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)

sync_engine = create_engine(settings.database_url_sync, echo=False, pool_pre_ping=True)
sync_session_factory = sessionmaker(sync_engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


def get_sync_db() -> Session:
    """For use inside Celery workers (no async event loop)."""
    return sync_session_factory()
