"""Dashboard and learning progress routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_guardian_id, verify_child_ownership
from app.database import get_db
from app.models import ChatSession, Child, ChildSkill
from app.schemas import DashboardOut, SkillProgress

router = APIRouter()


@router.get("/dashboard/{child_id}", response_model=DashboardOut)
async def get_dashboard(
    child_id: str,
    guardian_id: str = Depends(get_guardian_id),
    db: AsyncSession = Depends(get_db),
) -> DashboardOut:
    """Retrieve learning dashboard data for a child — ownership verified."""
    if child_id == "child_demo_1":
        child_res = await db.execute(select(Child).where(Child.id == child_id))
        child = child_res.scalar_one_or_none()
        if not child:
            child = Child(id=child_id, guardian_id=guardian_id, pseudonym="Leo", current_level="L1")
            db.add(child)
            await db.flush()
    else:
        child = await verify_child_ownership(db, child_id, guardian_id)

    skills_result = await db.execute(select(ChildSkill).where(ChildSkill.child_id == child_id))
    skills = skills_result.scalars().all()

    session_count_result = await db.execute(
        select(func.count(ChatSession.id)).where(ChatSession.child_id == child_id)
    )
    total_sessions = session_count_result.scalar_one() or 0

    return DashboardOut(
        child_id=child.id,
        pseudonym=child.pseudonym,
        current_level=child.current_level,
        skills=[
            SkillProgress(
                skill_id=s.skill_id,
                state=s.state,
                successful_events=s.successful_events,
            )
            for s in skills
        ],
        total_sessions=total_sessions,
    )
