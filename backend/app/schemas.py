"""Pydantic request/response schemas for the API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# --- Guardian / Auth ---


class GuardianCreate(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class GuardianOut(BaseModel):
    id: str
    email: str
    consent_timestamp: datetime | None = None
    consent_version: str | None = None

    model_config = {"from_attributes": True}


# --- Child ---


class ChildCreate(BaseModel):
    pseudonym: str = Field(..., min_length=1, max_length=50)
    birth_month_year: str | None = Field(None, pattern=r"^\d{4}-\d{2}$")


class ChildOut(BaseModel):
    id: str
    guardian_id: str
    pseudonym: str
    birth_month_year: str | None = None
    current_level: str

    model_config = {"from_attributes": True}


# --- Session ---


class SessionCreate(BaseModel):
    child_id: str


class SessionOut(BaseModel):
    id: str
    child_id: str
    active_mode: str
    started_at: datetime
    turn_count: int

    model_config = {"from_attributes": True}


# --- Turn ---


class TurnRequest(BaseModel):
    session_id: str
    child_message: str = Field(..., min_length=1, max_length=500)
    idempotency_key: str | None = Field(None, max_length=64)


class TurnResponse(BaseModel):
    turn_id: str
    response_text: str
    mode: str
    level: str
    session_id: str
    fallback_used: bool = False
    latency_ms: int | None = None

    model_config = {"from_attributes": True}


# --- Dashboard / Progress ---


class SkillProgress(BaseModel):
    skill_id: str
    state: str
    successful_events: int

    model_config = {"from_attributes": True}


class DashboardOut(BaseModel):
    child_id: str
    pseudonym: str
    current_level: str
    skills: list[SkillProgress]
    total_sessions: int
