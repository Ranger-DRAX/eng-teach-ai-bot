"""Initial schema for guardians, children, skills, assessments, sessions, and turns.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-10-18 10:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. guardians
    op.create_table(
        "guardians",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("consent_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consent_version", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_guardians_email"), "guardians", ["email"], unique=True)

    # 2. children
    op.create_table(
        "children",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("guardian_id", sa.String(length=36), nullable=False),
        sa.Column("pseudonym", sa.String(length=50), nullable=False),
        sa.Column("birth_month_year", sa.String(length=7), nullable=True),
        sa.Column("current_level", sa.String(length=2), nullable=False, server_default="L1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["guardian_id"], ["guardians.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_children_guardian_id"), "children", ["guardian_id"], unique=False)

    # 3. child_skills
    op.create_table(
        "child_skills",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("child_id", sa.String(length=36), nullable=False),
        sa.Column("skill_id", sa.String(length=50), nullable=False),
        sa.Column("state", sa.Enum("unassessed", "developing", "mastered", "review", name="skill_state"), nullable=False, server_default="unassessed"),
        sa.Column("successful_events", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sessions_with_success", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_child_skills_child_id"), "child_skills", ["child_id"], unique=False)
    op.create_index("ix_child_skill_unique", "child_skills", ["child_id", "skill_id"], unique=True)

    # 4. assessment_events
    op.create_table(
        "assessment_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("child_id", sa.String(length=36), nullable=False),
        sa.Column("skill_id", sa.String(length=50), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("result", sa.Enum("pass", "retry", name="assessment_result"), nullable=False),
        sa.Column("idempotency_key", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index(op.f("ix_assessment_events_child_id"), "assessment_events", ["child_id"], unique=False)

    # 5. chat_sessions
    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("child_id", sa.String(length=36), nullable=False),
        sa.Column("active_mode", sa.String(length=20), nullable=False, server_default="learning"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("turn_count", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_chat_sessions_child_id"), "chat_sessions", ["child_id"], unique=False)

    # 6. chat_turns
    op.create_table(
        "chat_turns",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("child_message", sa.Text(), nullable=False),
        sa.Column("response_text", sa.Text(), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("level", sa.String(length=2), nullable=False),
        sa.Column("fallback_used", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("idempotency_key", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index(op.f("ix_chat_turns_session_id"), "chat_turns", ["session_id"], unique=False)


def downgrade() -> None:
    op.drop_table("chat_turns")
    op.drop_table("chat_sessions")
    op.drop_table("assessment_events")
    op.drop_table("child_skills")
    op.drop_table("children")
    op.drop_table("guardians")
