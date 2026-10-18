"""Child profile management routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_guardian_id, verify_child_ownership
from app.database import get_db
from app.models import AssessmentEvent, ChatSession, ChatTurn, Child, ChildSkill
from app.schemas import ChildCreate, ChildOut

router = APIRouter()


@router.post("/children", response_model=ChildOut, status_code=status.HTTP_201_CREATED)
async def create_child(
    body: ChildCreate,
    guardian_id: str = Depends(get_guardian_id),
    db: AsyncSession = Depends(get_db),
) -> Child:
    """Create a child profile under the authenticated guardian."""
    child = Child(guardian_id=guardian_id, pseudonym=body.pseudonym, birth_month_year=body.birth_month_year)
    db.add(child)
    await db.flush()
    return child


@router.get("/children/{child_id}", response_model=ChildOut)
async def get_child(
    child_id: str,
    guardian_id: str = Depends(get_guardian_id),
    db: AsyncSession = Depends(get_db),
) -> Child:
    """Get a child profile — ownership verified."""
    return await verify_child_ownership(db, child_id, guardian_id)


@router.delete("/children/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_child(
    child_id: str,
    guardian_id: str = Depends(get_guardian_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete child and all associated data — cascading purge."""
    child = await verify_child_ownership(db, child_id, guardian_id)
    # Cascade deletes via FK constraints, but explicit for clarity
    await db.execute(delete(ChatTurn).where(ChatTurn.session_id.in_(select(ChatSession.id).where(ChatSession.child_id == child.id))))  # noqa: E501
    await db.execute(delete(ChatSession).where(ChatSession.child_id == child.id))
    await db.execute(delete(AssessmentEvent).where(AssessmentEvent.child_id == child.id))
    await db.execute(delete(ChildSkill).where(ChildSkill.child_id == child.id))
    await db.delete(child)
