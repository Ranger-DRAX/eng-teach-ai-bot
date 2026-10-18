"""Health and readiness endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check() -> dict[str, str]:
    """Readiness check."""
    return {"status": "ready"}
