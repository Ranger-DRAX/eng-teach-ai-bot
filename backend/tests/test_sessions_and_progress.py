"""Tests for chat sessions, turns, and learning dashboard."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ChildSkill


@pytest.mark.asyncio
async def test_session_lifecycle_and_turn(client: AsyncClient) -> None:
    # Create child
    child_resp = await client.post(
        "/api/v1/children",
        json={"pseudonym": "Emma"},
        headers={"guardian-id": "g_001"},
    )
    child_id = child_resp.json()["id"]

    # Start session
    sess_resp = await client.post(
        "/api/v1/sessions",
        json={"child_id": child_id},
        headers={"guardian-id": "g_001"},
    )
    assert sess_resp.status_code == 201
    sess_data = sess_resp.json()
    assert sess_data["child_id"] == child_id
    assert sess_data["active_mode"] == "learning"
    session_id = sess_data["id"]

    # Retrieve session
    get_sess_resp = await client.get(f"/api/v1/sessions/{session_id}", headers={"guardian-id": "g_001"})
    assert get_sess_resp.status_code == 200

    # Cross-guardian session access denied
    cross_sess_resp = await client.get(f"/api/v1/sessions/{session_id}", headers={"guardian-id": "g_other"})
    assert cross_sess_resp.status_code == 403

    # Send chat turn
    turn_resp = await client.post(
        "/api/v1/chat/turn",
        json={"session_id": session_id, "child_message": "Hello!"},
        headers={"guardian-id": "g_001"},
    )
    assert turn_resp.status_code == 200
    turn_data = turn_resp.json()
    assert turn_data["session_id"] == session_id
    assert turn_data["level"] == "L1"
    assert "response_text" in turn_data


@pytest.mark.asyncio
async def test_dashboard_progress(client: AsyncClient, db_session: AsyncSession) -> None:
    # Create child
    child_resp = await client.post(
        "/api/v1/children",
        json={"pseudonym": "Noah"},
        headers={"guardian-id": "g_002"},
    )
    child_id = child_resp.json()["id"]

    # Seed skill progress
    skill = ChildSkill(child_id=child_id, skill_id="l1_colors", state="mastered", successful_events=4)
    db_session.add(skill)
    await db_session.flush()

    # Read dashboard
    dash_resp = await client.get(f"/api/v1/dashboard/{child_id}", headers={"guardian-id": "g_002"})
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert dash_data["child_id"] == child_id
    assert dash_data["pseudonym"] == "Noah"
    assert len(dash_data["skills"]) == 1
    assert dash_data["skills"][0]["skill_id"] == "l1_colors"
    assert dash_data["skills"][0]["state"] == "mastered"
