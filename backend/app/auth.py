"""Authorization helpers — enforce guardian ↔ child ownership."""

from __future__ import annotations

from fastapi import Header, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Child


def get_guardian_id(
    guardian_id_header: str | None = Header(None, alias="guardian-id"),
    guardian_id_header_alt: str | None = Header(None, alias="guardian_id"),
    guardian_id_query: str | None = Query(None, alias="guardian_id"),
) -> str:
    """Extract guardian_id from header (guardian-id / guardian_id) or query parameter."""
    gid = guardian_id_header or guardian_id_header_alt or guardian_id_query
    if not gid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing guardian_id")
    return gid


async def verify_child_ownership(db: AsyncSession, child_id: str, guardian_id: str) -> Child:
    """Return the Child if it belongs to guardian_id, else raise 403/404."""
    result = await db.execute(select(Child).where(Child.id == child_id))
    child = result.scalar_one_or_none()
    if child is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")
    if child.guardian_id != guardian_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return child
