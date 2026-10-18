"""LLM Provider abstraction and adapters.

Supports:
1. GoogleGenAIProvider: Real adapter using Google Gemini REST API / official spec.
2. MockLLMProvider: Deterministic provider for CI, unit testing, and edge case simulations.
"""

from __future__ import annotations

import abc
import asyncio
import json
import logging
import re
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger("app.llm.provider")


class LLMProvider(abc.ABC):
    """Abstract provider interface for generative language models."""

    @abc.abstractmethod
    async def generate_response(
        self,
        prompt: str,
        system_instruction: str,
        timeout_ms: int = 1500,
    ) -> str:
        """Generate response text from LLM within bounded timeout."""
        pass


class MockLLMProvider(LLMProvider):
    """Deterministic mock provider with interactive learning dialogue for kids under 7."""

    def __init__(
        self,
        default_response: str | None = None,
        simulate_timeout: bool = False,
        simulate_error: str | None = None,
        simulate_rate_limit: bool = False,
    ) -> None:
        self.default_response = default_response
        self.simulate_timeout = simulate_timeout
        self.simulate_error = simulate_error
        self.simulate_rate_limit = simulate_rate_limit
        self.call_count = 0
        self.last_prompt: str | None = None
        self.last_system_instruction: str | None = None

    def _generate_interactive_response(self, prompt: str) -> str:
        """Generate age-appropriate, interactive dialogue for early learners."""
        # Extract ONLY the latest child message, ignoring previous turn history in prompt
        child_match = re.search(r'Child says:\s*"([^"]+)"', prompt, re.IGNORECASE)
        latest_msg = child_match.group(1).strip() if child_match else prompt
        p_lower = latest_msg.lower()

        if any(w in p_lower for w in ("talk", "people", "pepole", "cant", "can't")):
            text = "That is awesome! Talking like people is the best! 🌟 What is your favorite word to say?"
        elif "cat" in p_lower:
            text = "A cat says meow! 🐱 Can you make a cat sound?"
        elif "dog" in p_lower:
            text = "A happy dog says woof woof! 🐶 Can you bark like a dog?"
        elif any(w in p_lower for w in ("animal", "pet", "bird", "fish", "lion")):
            text = "Animals are so fun! 🦁 What animal do you like best?"
        elif "blue" in p_lower:
            text = "Blue is pretty like the ocean! 🌊 Can you find something red?"
        elif "red" in p_lower:
            text = "Red like a sweet apple! 🍎 What is your favorite color?"
        elif "yellow" in p_lower:
            text = "Yellow like the warm sun! ☀️ What is yellow in your room?"
        elif "green" in p_lower:
            text = "Green like leaves on a tree! 🍃 Can you say green?"
        elif "color" in p_lower:
            text = "I love colors! Do you like red, blue, or yellow?"
        elif "apple" in p_lower:
            text = "Yum, crunchy red apple! 🍎 Do you like eating apples?"
        elif any(w in p_lower for w in ("banana", "food", "eat", "fruit")):
            text = "Fruits give us energy! 🍌 What is your favorite snack?"
        elif any(w in p_lower for w in ("yes", "yeah", "yep", "sure", "ok", "okay")):
            text = "Hooray! 🌟 Let's learn fun words together! Can you say apple?"
        elif any(w in p_lower for w in ("no", "nope")):
            text = "That is totally okay! What fun word would you like to try?"
        elif any(w in p_lower for w in ("hello", "hi", "hey")):
            text = "Hello friend! 🌟 What animal do you like most?"
        elif any(w in p_lower for w in ("1", "2", "3", "4", "5", "one", "two", "three", "four", "five", "count")):
            text = "Great counting! 1, 2, 3! Can you count to four?"
        else:
            rotation = [
                "That is so neat! 🌟 Can you tell me what color you like?",
                "You are doing awesome! 🎈 What animal is your favorite?",
                "I love chatting with you! What is something yummy you like to eat?",
                "Super job! Can you show me a big happy smile?",
            ]
            text = rotation[self.call_count % len(rotation)]

        return json.dumps({"response_text": text})

    async def generate_response(
        self,
        prompt: str,
        system_instruction: str,
        timeout_ms: int = 1500,
    ) -> str:
        self.call_count += 1
        self.last_prompt = prompt
        self.last_system_instruction = system_instruction

        if self.simulate_timeout:
            await asyncio.sleep(timeout_ms / 1000.0 + 0.1)
            raise asyncio.TimeoutError("Mock provider timeout exceeded")

        if self.simulate_rate_limit:
            raise RuntimeError("HTTP 429 Too Many Requests: Rate limit exceeded")

        if self.simulate_error:
            raise RuntimeError(f"Mock provider error: {self.simulate_error}")

        if self.default_response is not None:
            return self.default_response

        return self._generate_interactive_response(prompt)


class GoogleGenAIProvider(LLMProvider):
    """Google Gemini API adapter via asynchronous HTTP endpoint."""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = (api_key or settings.effective_api_key or "").strip()
        self.model = model or settings.llm_model or "gemini-2.5-flash"

    async def generate_response(
        self,
        prompt: str,
        system_instruction: str,
        timeout_ms: int = 4000,
    ) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        timeout_seconds = timeout_ms / 1000.0

        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.7,
                "maxOutputTokens": 150,
            },
        }

        models_to_try = [self.model, "gemini-2.5-flash", "gemini-1.5-flash"]
        models_to_try = list(dict.fromkeys(m for m in models_to_try if m))

        last_error = None
        for mod in models_to_try:
            url = f"{self.BASE_URL}/{mod}:generateContent?key={self.api_key}"
            try:
                async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return str(parts[0].get("text", "")).strip()
                    last_error = f"{mod} -> HTTP {resp.status_code}: {resp.text}"
                    logger.warning("Gemini model %s returned status %d", mod, resp.status_code)
            except Exception as exc:
                last_error = f"{mod} -> {type(exc).__name__}: {exc}"

        raise ValueError(f"Gemini API request failed: {last_error}")


def get_llm_provider(force_provider: str | None = None) -> LLMProvider:
    """Factory creating configured LLM provider."""
    provider_name = (force_provider or settings.llm_provider or "").lower()

    if provider_name == "mock":
        return MockLLMProvider()

    api_key = settings.effective_api_key
    # Use Google provider if explicitly requested or if any Gemini key is present
    if provider_name in ("google", "gemini") or (api_key and len(api_key) > 5):
        return GoogleGenAIProvider(api_key=api_key)

    return MockLLMProvider()
