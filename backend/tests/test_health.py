"""Tests for health and readiness endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_ready_check(client: AsyncClient) -> None:
    response = await client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


@pytest.mark.asyncio
async def test_correlation_id_header(client: AsyncClient) -> None:
    response = await client.get("/health", headers={"X-Correlation-ID": "test-trace-123"})
    assert response.headers.get("X-Correlation-ID") == "test-trace-123"
