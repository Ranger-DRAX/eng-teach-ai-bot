"""Tests for guardian/child authorization boundaries and profile management."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Child


@pytest.mark.asyncio
async def test_create_and_get_child(client: AsyncClient) -> None:
    # Create child for Guardian 1
    create_resp = await client.post(
        "/api/v1/children",
        json={"pseudonym": "Leo", "birth_month_year": "2021-05"},
        headers={"guardian-id": "guardian_1"},
    )
    assert create_resp.status_code == 201
    child_data = create_resp.json()
    assert child_data["pseudonym"] == "Leo"
    assert child_data["current_level"] == "L1"
    child_id = child_data["id"]

    # Retrieve child by same guardian
    get_resp = await client.get(f"/api/v1/children/{child_id}", headers={"guardian-id": "guardian_1"})
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == child_id


@pytest.mark.asyncio
async def test_cross_child_authorization_denied(client: AsyncClient) -> None:
    # Guardian 1 creates a child
    create_resp = await client.post(
        "/api/v1/children",
        json={"pseudonym": "Mia"},
        headers={"guardian-id": "guardian_1"},
    )
    assert create_resp.status_code == 201
    child_id = create_resp.json()["id"]

    # Guardian 2 attempts to read Guardian 1's child -> 403 Forbidden
    cross_read_resp = await client.get(f"/api/v1/children/{child_id}", headers={"guardian-id": "guardian_2"})
    assert cross_read_resp.status_code == 403
    assert cross_read_resp.json()["detail"] == "Access denied"

    # Guardian 2 attempts to delete Guardian 1's child -> 403 Forbidden
    cross_delete_resp = await client.delete(
        f"/api/v1/children/{child_id}",
        headers={"guardian-id": "guardian_2"},
    )
    assert cross_delete_resp.status_code == 403


@pytest.mark.asyncio
async def test_missing_child_returns_404(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/children/nonexistent_id", headers={"guardian-id": "guardian_1"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_missing_auth_header_returns_401(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/children", json={"pseudonym": "Sam"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_cascading_delete_child(client: AsyncClient, db_session: AsyncSession) -> None:
    # Create child
    create_resp = await client.post(
        "/api/v1/children",
        json={"pseudonym": "Lucas"},
        headers={"guardian-id": "guardian_1"},
    )
    child_id = create_resp.json()["id"]

    # Delete child
    del_resp = await client.delete(f"/api/v1/children/{child_id}", headers={"guardian-id": "guardian_1"})
    assert del_resp.status_code == 204

    # Verify child is removed from DB
    result = await db_session.execute(select(Child).where(Child.id == child_id))
    assert result.scalar_one_or_none() is None
