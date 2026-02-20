from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Memo
from app.schemas import MemoRead

router = APIRouter(tags=["memos"])


@router.get("/projects/{project_id}/memos", response_model=list[MemoRead])
async def list_memos(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Memo).where(Memo.project_id == project_id).order_by(Memo.created_at.desc())
    )
    return result.scalars().all()


@router.get("/memos/{memo_id}", response_model=MemoRead)
async def get_memo(memo_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    memo = await db.get(Memo, memo_id)
    if not memo:
        raise HTTPException(404, "Memo not found")
    return memo
