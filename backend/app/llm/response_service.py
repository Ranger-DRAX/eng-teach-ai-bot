"""LLM Response Service.

Orchestrates context building, single generative LLM calls, output validation,
and deterministic fallbacks.
Enforces the core rule:
- Backend owns mode, progression, level, and fallback metadata.
- Deterministic paths make zero LLM calls.
- Validated response text is guaranteed before returning to the child.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any

from app.config import settings
from app.context.context_builder import ContextBuilder
from app.llm.provider import LLMProvider, get_llm_provider
from app.safety.output_validator import OutputValidator

logger = logging.getLogger("app.llm.response_service")

FALLBACK_RESPONSES: dict[str, str] = {
    "L1": "Hello! Let us learn and have fun!",
    "L2": "Great try! What animal do you like best?",
    "L3": "That sounds fun! Can you tell me more about it?",
}


@dataclass
class ServiceTurnResult:
    """Validated result of a conversational turn."""

    response_text: str
    fallback_used: bool
    mode: str
    level: str
    latency_ms: int
    error_reason: str | None = None
    validation_passed: bool = True


class LLMResponseService:
    """Service generating and validating responses for child chat turns."""

    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or get_llm_provider()

    @classmethod
    def get_fallback_for_level(cls, level: str, child_message: str = "") -> str:
        msg = (child_message or "").lower()
        if any(w in msg for w in ("talk", "people", "pepole", "cant", "can't")):
            return "Talking like people is amazing! You speak so clearly! 🌟 What is your favorite word?"
        if "cat" in msg:
            return "A cat says meow! 🐱 Can you make a cat sound?"
        if "dog" in msg:
            return "A happy dog says woof woof! 🐶 Can you bark like a dog?"
        if "blue" in msg:
            return "Blue is pretty like the ocean! 🌊 Can you find something red?"
        if "red" in msg:
            return "Red like a sweet apple! 🍎 What is your favorite color?"
        if any(w in msg for w in ("yes", "yeah", "ok", "okay")):
            return "Hooray! 🌟 Let's learn fun words together! Can you say apple?"
        if "apple" in msg:
            return "Yum, crunchy red apple! 🍎 Do you like eating apples?"
        return FALLBACK_RESPONSES.get(level, FALLBACK_RESPONSES["L1"])

    async def generate_response(
        self,
        child_message: str,
        current_level: str,
        mode: str,
        child_pseudonym: str = "Friend",
        target_skill: str | None = None,
        mastered_skills: list[str] | None = None,
        recent_turns: list[dict[str, str]] | None = None,
        deterministic_response: str | None = None,
        timeout_ms: int | None = None,
    ) -> ServiceTurnResult:
        """Process a turn: if deterministic, return immediately; otherwise call LLM and validate."""
        start_time = time.monotonic()
        timeout = timeout_ms or settings.llm_timeout_ms

        # 1. Deterministic path: zero LLM calls
        if deterministic_response is not None:
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            return ServiceTurnResult(
                response_text=deterministic_response,
                fallback_used=False,
                mode=mode,
                level=current_level,
                latency_ms=elapsed_ms,
                validation_passed=True,
            )

        # 2. Generative path: Assemble compact context
        system_instruction, user_prompt = ContextBuilder.build(
            child_pseudonym=child_pseudonym,
            current_level=current_level,
            selected_mode=mode,
            child_message=child_message,
            target_skill=target_skill,
            mastered_skills=mastered_skills,
            recent_turns=recent_turns,
        )

        raw_output: str | None = None
        error_reason: str | None = None

        # 3. Exactly one bounded LLM call
        try:
            raw_output = await self.provider.generate_response(
                prompt=user_prompt,
                system_instruction=system_instruction,
                timeout_ms=timeout,
            )
        except asyncio.TimeoutError:
            logger.warning("LLM request timed out after %d ms", timeout)
            error_reason = "provider_timeout"
        except Exception as exc:
            logger.warning("LLM request failed (%s): %s", type(exc).__name__, exc)
            error_reason = f"provider_error_{type(exc).__name__}"

        # 4. Validate output before display
        if raw_output and not error_reason:
            validation = OutputValidator.validate(raw_output, level=current_level)
            if validation.is_valid:
                elapsed_ms = int((time.monotonic() - start_time) * 1000)
                return ServiceTurnResult(
                    response_text=validation.response_text,
                    fallback_used=False,
                    mode=mode,
                    level=current_level,
                    latency_ms=elapsed_ms,
                    validation_passed=True,
                )
            error_reason = validation.error_reason or "validation_failed"

        # 5. Safe deterministic fallback on any error or rejection
        elapsed_ms = int((time.monotonic() - start_time) * 1000)
        return ServiceTurnResult(
            response_text=self.get_fallback_for_level(current_level, child_message),
            fallback_used=True,
            mode=mode,
            level=current_level,
            latency_ms=elapsed_ms,
            error_reason=error_reason,
            validation_passed=False,
        )
