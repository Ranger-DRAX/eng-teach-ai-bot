"""SQLAlchemy ORM models for the English Learning Chatbot."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""

    pass


class Guardian(Base):
    """Parent/guardian account — the authentication and consent authority."""

    __tablename__ = "guardians"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    consent_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consent_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    children: Mapped[list[Child]] = relationship("Child", back_populates="guardian", cascade="all, delete-orphan")


class Child(Base):
    """Child profile — minimal PII, linked to a guardian."""

    __tablename__ = "children"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    guardian_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("guardians.id", ondelete="CASCADE"), nullable=False, index=True
    )
    pseudonym: Mapped[str] = mapped_column(String(50), nullable=False)
    birth_month_year: Mapped[str | None] = mapped_column(String(7), nullable=True)  # YYYY-MM
    current_level: Mapped[str] = mapped_column(String(2), nullable=False, default="L1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    guardian: Mapped[Guardian] = relationship("Guardian", back_populates="children")
    skills: Mapped[list[ChildSkill]] = relationship("ChildSkill", back_populates="child", cascade="all, delete-orphan")
    sessions: Mapped[list[ChatSession]] = relationship(
        "ChatSession", back_populates="child", cascade="all, delete-orphan"
    )


class ChildSkill(Base):
    """Per-child skill mastery tracking."""

    __tablename__ = "child_skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[str] = mapped_column(String(50), nullable=False)
    state: Mapped[str] = mapped_column(
        Enum("unassessed", "developing", "mastered", "review", name="skill_state"),
        nullable=False,
        default="unassessed",
    )
    successful_events: Mapped[int] = mapped_column(default=0, nullable=False)
    sessions_with_success: Mapped[int] = mapped_column(default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    child: Mapped[Child] = relationship("Child", back_populates="skills")

    __table_args__ = (Index("ix_child_skill_unique", "child_id", "skill_id", unique=True),)


class AssessmentEvent(Base):
    """Individual assessment evidence record."""

    __tablename__ = "assessment_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[str] = mapped_column(String(50), nullable=False)
    session_id: Mapped[str] = mapped_column(String(36), nullable=False)
    result: Mapped[str] = mapped_column(Enum("pass", "retry", name="assessment_result"), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ChatSession(Base):
    """Chat session lifecycle record."""

    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True
    )
    active_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="learning")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    turn_count: Mapped[int] = mapped_column(default=0, nullable=False)

    child: Mapped[Child] = relationship("Child", back_populates="sessions")
    turns: Mapped[list[ChatTurn]] = relationship("ChatTurn", back_populates="session", cascade="all, delete-orphan")


class ChatTurn(Base):
    """Individual conversational turn."""

    __tablename__ = "chat_turns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    child_message: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    level: Mapped[str] = mapped_column(String(2), nullable=False)
    fallback_used: Mapped[bool] = mapped_column(default=False, nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session: Mapped[ChatSession] = relationship("ChatSession", back_populates="turns")
