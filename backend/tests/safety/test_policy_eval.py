"""Automated policy evaluation for child safety and adversarial inputs."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.llm.provider import MockLLMProvider
from app.llm.response_service import LLMResponseService
from app.orchestrator.mode_manager import ModeManager
from app.safety.output_validator import OutputValidator

SCENARIOS_PATH = Path(__file__).resolve().parent / "scenarios.jsonl"


def load_scenarios():
    scenarios = []
    with open(SCENARIOS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                scenarios.append(json.loads(line))
    return [(s["id"], s) for s in scenarios]


@pytest.mark.asyncio
@pytest.mark.parametrize("scenario_id,scenario", load_scenarios())
async def test_safety_scenario_handling(scenario_id: str, scenario: dict):
    input_message = scenario["input_message"]
    forbidden_terms = scenario.get("forbidden_terms", [])

    # 1. Evaluate mode routing
    mode_decision = ModeManager.select_mode(
        child_message=input_message,
        current_mode="learning",
    )

    # 2. Evaluate service response
    mock_provider = MockLLMProvider(
        default_response='{"response_text": "Hello friend! Let us learn and have fun!"}'
    )
    service = LLMResponseService(provider=mock_provider)

    result = await service.generate_response(
        child_message=input_message,
        current_level="L1",
        mode=mode_decision.mode,
        deterministic_response=mode_decision.deterministic_response,
    )

    response_text = result.response_text.lower()

    # Assert no forbidden terms appear in response
    for term in forbidden_terms:
        assert term.lower() not in response_text, (
            f"Scenario {scenario_id} leaked forbidden term '{term}' in response: {result.response_text}"
        )

    # Autonomy assertions
    if scenario["category"] == "child_autonomy":
        assert result.mode == "support"
        assert not result.fallback_used  # handled deterministically
