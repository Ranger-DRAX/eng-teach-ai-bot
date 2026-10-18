"""Unit tests for LLMResponseService, OutputValidator, and mock providers.

Tests:
1. Valid constrained JSON output parsed and accepted.
2. Malformed JSON triggers safe fallback without crashing.
3. Empty output triggers safe fallback.
4. Output exceeding level word cap triggers fallback.
5. Diagnostic / psychiatric language rejected.
6. Scary / unsafe content rejected.
7. PII solicitation rejected.
8. Provider timeout triggers fallback.
9. Provider rate limit (429) triggers fallback.
10. Provider outage / error triggers fallback.
11. Deterministic path makes ZERO provider calls.
12. Backend owns mode, level, and fallback_used flags.
"""

from __future__ import annotations

import pytest

from app.llm.provider import MockLLMProvider
from app.llm.response_service import LLMResponseService
from app.safety.output_validator import OutputValidator


@pytest.mark.asyncio
async def test_valid_json_response_accepted():
    mock = MockLLMProvider(default_response='{"response_text": "Good job! The apple is red!"}')
    service = LLMResponseService(provider=mock)

    result = await service.generate_response(
        child_message="Red apple!",
        current_level="L1",
        mode="learning",
        child_pseudonym="Leo",
    )

    assert result.response_text == "Good job! The apple is red!"
    assert result.fallback_used is False
    assert result.validation_passed is True
    assert result.level == "L1"
    assert result.mode == "learning"
    assert mock.call_count == 1


@pytest.mark.asyncio
async def test_deterministic_path_makes_zero_provider_calls():
    mock = MockLLMProvider()
    service = LLMResponseService(provider=mock)

    result = await service.generate_response(
        child_message="I'm done",
        current_level="L1",
        mode="support",
        child_pseudonym="Leo",
        deterministic_response="You did great today! Bye bye! 🌟",
    )

    assert result.response_text == "You did great today! Bye bye! 🌟"
    assert result.fallback_used is False
    assert mock.call_count == 0  # Zero provider calls!


@pytest.mark.asyncio
async def test_malformed_json_triggers_safe_fallback():
    mock = MockLLMProvider(default_response="Not valid JSON at all {broken: text")
    service = LLMResponseService(provider=mock)

    result = await service.generate_response(
        child_message="Hello",
        current_level="L1",
        mode="conversation",
    )

    assert result.fallback_used is True
    assert result.validation_passed is False
    assert "learn" in result.response_text.lower() or "hello" in result.response_text.lower()
    assert result.error_reason == "empty_or_malformed_output"


@pytest.mark.asyncio
async def test_empty_output_triggers_fallback():
    mock = MockLLMProvider(default_response="")
    service = LLMResponseService(provider=mock)

    result = await service.generate_response(
        child_message="Hi",
        current_level="L1",
        mode="learning",
    )

    assert result.fallback_used is True
    assert result.validation_passed is False


@pytest.mark.asyncio
async def test_output_too_long_triggers_fallback():
    # L1 max is 15 words. This has 20 words.
    long_text = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty"
    mock = MockLLMProvider(default_response=f'{{"response_text": "{long_text}"}}')
    service = LLMResponseService(provider=mock)

    result = await service.generate_response(
        child_message="Tell me a story",
        current_level="L1",
        mode="learning",
    )

    assert result.fallback_used is True
    assert result.validation_passed is False
    assert "length_exceeded" in (result.error_reason or "")


@pytest.mark.asyncio
async def test_diagnostic_language_triggers_fallback():
    mock = MockLLMProvider(default_response='{"response_text": "You seem to have anxiety about this."}')
    service = LLMResponseService(provider=mock)

    result = await service.generate_response(
        child_message="I'm scared",
        current_level="L2",
        mode="support",
    )

    assert result.fallback_used is True
    assert result.validation_passed is False
    assert result.error_reason == "diagnostic_language_detected"
    assert "anxiety" not in result.response_text.lower()


@pytest.mark.asyncio
async def test_unsafe_violent_content_triggers_fallback():
    mock = MockLLMProvider(default_response='{"response_text": "The monster will hurt you."}')
    service = LLMResponseService(provider=mock)

    result = await service.generate_response(
        child_message="Monster!",
        current_level="L1",
        mode="learning",
    )

    assert result.fallback_used is True
    assert result.validation_passed is False
    assert result.error_reason == "unsafe_content_detected"


@pytest.mark.asyncio
async def test_pii_solicitation_triggers_fallback():
    mock = MockLLMProvider(default_response='{"response_text": "Where do you live, my friend?"}')
    service = LLMResponseService(provider=mock)

    result = await service.generate_response(
        child_message="I am home",
        current_level="L2",
        mode="conversation",
    )

    assert result.fallback_used is True
    assert result.validation_passed is False
    assert result.error_reason == "pii_solicitation_detected"


@pytest.mark.asyncio
async def test_provider_timeout_triggers_fallback():
    mock = MockLLMProvider(simulate_timeout=True)
    service = LLMResponseService(provider=mock)

    result = await service.generate_response(
        child_message="Hello",
        current_level="L1",
        mode="learning",
        timeout_ms=50,
    )

    assert result.fallback_used is True
    assert result.error_reason == "provider_timeout"
    assert len(result.response_text) > 0


@pytest.mark.asyncio
async def test_provider_rate_limit_triggers_fallback():
    mock = MockLLMProvider(simulate_rate_limit=True)
    service = LLMResponseService(provider=mock)

    result = await service.generate_response(
        child_message="Hello",
        current_level="L1",
        mode="learning",
    )

    assert result.fallback_used is True
    assert "RuntimeError" in (result.error_reason or "")


@pytest.mark.asyncio
async def test_provider_error_triggers_fallback():
    mock = MockLLMProvider(simulate_error="Internal 500 error")
    service = LLMResponseService(provider=mock)

    result = await service.generate_response(
        child_message="Hello",
        current_level="L1",
        mode="learning",
    )

    assert result.fallback_used is True
    assert "error" in (result.error_reason or "").lower()


def test_markdown_json_fence_parsed_correctly():
    raw = """Here is your response:
```json
{
  "response_text": "Look at the big blue dog!"
}
```
Hope you like it!"""
    parsed = OutputValidator.parse_payload(raw)
    assert parsed == "Look at the big blue dog!"
