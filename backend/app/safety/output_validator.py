"""Output validation for LLM generative responses.

Enforces:
1. Constrained JSON schema extraction (`{"response_text": "..."}`)
2. Age-appropriate word count caps (L1: ≤15, L2: ≤30, L3: ≤50)
3. Content safety: no violence, adult themes, psychological diagnoses, or PII elicitation
4. No external links or code execution payloads
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

LEVEL_WORD_LIMITS: dict[str, int] = {
    "L1": 15,
    "L2": 30,
    "L3": 50,
}

DIAGNOSTIC_TERMS = [
    "anxiety",
    "depression",
    "adhd",
    "autism",
    "bipolar",
    "disorder",
    "diagnosis",
    "therapy",
    "pathology",
    "trauma",
    "psychiatric",
]

UNSAFE_TERMS = [
    "kill",
    "death",
    "blood",
    "weapon",
    "gun",
    "knife",
    "die",
    "hurt",
    "murder",
    "poison",
    "monster",
    "frightened",
]

PII_PATTERNS = [
    r"where do you live",
    r"what is your (real )?name",
    r"what is your address",
    r"your phone number",
    r"what school do you go to",
    r"tell me your last name",
]


@dataclass
class ValidationResult:
    """Outcome of validating a model response."""

    is_valid: bool
    response_text: str
    error_reason: str | None = None
    word_count: int = 0


class OutputValidator:
    """Validates raw LLM output before it can ever be displayed to a child."""

    @classmethod
    def parse_payload(cls, raw_output: str) -> str | None:
        """Extract response_text from JSON or cleaned string."""
        if not raw_output or not raw_output.strip():
            return None

        text = raw_output.strip()

        # Handle markdown fenced code blocks: ```json ... ```
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fence_match:
            text = fence_match.group(1).strip()

        # Try to parse as JSON
        if text.startswith("{") and text.endswith("}"):
            try:
                data = json.loads(text)
                if isinstance(data, dict) and "response_text" in data:
                    res = data["response_text"]
                    return str(res).strip() if res else None
            except json.JSONDecodeError:
                return None

        # If not structured JSON, accept raw string if it's not JSON syntax
        if not text.startswith("{"):
            return text

        return None

    @classmethod
    def validate(cls, raw_output: str, level: str = "L1") -> ValidationResult:
        """Validate raw model output against schema, word limits, and safety rules."""
        parsed_text = cls.parse_payload(raw_output)

        if parsed_text is None or not parsed_text.strip():
            return ValidationResult(
                is_valid=False,
                response_text="",
                error_reason="empty_or_malformed_output",
            )

        words = parsed_text.split()
        word_count = len(words)
        max_words = LEVEL_WORD_LIMITS.get(level, 15)

        # 1. Enforce length cap
        if word_count > max_words:
            return ValidationResult(
                is_valid=False,
                response_text=parsed_text,
                error_reason=f"length_exceeded_max_{max_words}_words",
                word_count=word_count,
            )

        lowered = parsed_text.lower()

        # 2. Check diagnostic terms
        for term in DIAGNOSTIC_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", lowered):
                return ValidationResult(
                    is_valid=False,
                    response_text=parsed_text,
                    error_reason="diagnostic_language_detected",
                    word_count=word_count,
                )

        # 3. Check unsafe/scary terms
        for term in UNSAFE_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", lowered):
                return ValidationResult(
                    is_valid=False,
                    response_text=parsed_text,
                    error_reason="unsafe_content_detected",
                    word_count=word_count,
                )

        # 4. Check PII elicitation patterns
        for pattern in PII_PATTERNS:
            if re.search(pattern, lowered):
                return ValidationResult(
                    is_valid=False,
                    response_text=parsed_text,
                    error_reason="pii_solicitation_detected",
                    word_count=word_count,
                )

        # 5. Check URLs and executable code
        if re.search(r"https?://|www\.", lowered):
            return ValidationResult(
                is_valid=False,
                response_text=parsed_text,
                error_reason="url_detected",
                word_count=word_count,
            )

        if re.search(r"<script|javascript:|eval\(", lowered):
            return ValidationResult(
                is_valid=False,
                response_text=parsed_text,
                error_reason="executable_code_detected",
                word_count=word_count,
            )

        return ValidationResult(
            is_valid=True,
            response_text=parsed_text,
            error_reason=None,
            word_count=word_count,
        )
