"""Compact context builder for English learning generative turns.

Minimizes context window to reduce latency and protect child privacy.
Strictly isolates child accounts and enforces response schemas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.safety.output_validator import LEVEL_WORD_LIMITS

PROMPT_VERSION = "2026.10.1"

BASE_SYSTEM_TEMPLATE = """You are a warm, loving, and human-like English learning companion for young children under 7.
Your voice should feel like a kind preschool teacher or friendly playmate—natural, cheerful, warm, and interactive, NEVER robotic or repetitive.

CONVERSATION GUIDELINES:
1. TALK NATURALLY: Respond directly, warmly, and genuinely to what the child said like a caring human companion.
2. ADAPT TO PROGRESS: Support the child's learning by weaving in simple words, encouragement, and friendly questions.
3. CURRENT LEVEL: {level} (Around {max_words} words max, simple vocabulary for young kids).
4. MODE: {mode_instruction}
5. SAFETY: Never ask for real names, locations, phone numbers, or schools. Never mention scary or violent things.
6. EMOTIONAL SUPPORT: Celebrate the child's voice and effort. Never use clinical terms (like anxiety, ADHD, disorder).
7. FORMAT: Return ONLY a valid JSON object matching:
{{
  "response_text": "Your warm, natural words to the child"
}}
"""

MODE_INSTRUCTIONS = {
    "learning": "Learning mode. Focus on gentle vocabulary practice and curious questions. Keep it fun and conversational.",
    "conversation": "Conversation mode. Chat naturally about animals, toys, food, or colors. Keep it friendly and human.",
    "engagement": "Engagement mode. Play a simple guessing game, rhyme, animal sound, or playful challenge.",
    "support": "Support mode. Be calming, encouraging, and warm. Celebrate the child's effort.",
}


@dataclass
class CompactContext:
    """Minimized context representation for an LLM turn."""

    pseudonym: str
    level: str
    mode: str
    target_skill: str | None = None
    mastered_skills: list[str] = field(default_factory=list)
    recent_turns: list[dict[str, str]] = field(default_factory=list)
    prompt_version: str = PROMPT_VERSION

    def build_system_instruction(self) -> str:
        max_words = LEVEL_WORD_LIMITS.get(self.level, 15)
        mode_inst = MODE_INSTRUCTIONS.get(self.mode, MODE_INSTRUCTIONS["learning"])
        return BASE_SYSTEM_TEMPLATE.format(
            level=self.level,
            max_words=max_words,
            mode_instruction=mode_inst,
        )

    def build_user_prompt(self, child_message: str) -> str:
        """Construct a compact, privacy-redacted user prompt."""
        parts: list[str] = [
            f"Child's pseudonym: {self.pseudonym}",
            f"Level: {self.level}",
        ]
        if self.target_skill:
            parts.append(f"Current learning focus: {self.target_skill}")
        if self.mastered_skills:
            parts.append(f"Words the child has practiced and knows: {', '.join(self.mastered_skills[:6])}")

        # Compact conversation history (last 3 turns max)
        if self.recent_turns:
            history_lines: list[str] = []
            for turn in self.recent_turns[-3:]:
                u = turn.get("child", "").strip()
                b = turn.get("bot", "").strip()
                if u:
                    history_lines.append(f"Child: {u}")
                if b:
                    history_lines.append(f"Companion: {b}")
            if history_lines:
                parts.append("Recent dialogue:\n" + "\n".join(history_lines))

        parts.append(f"Child says: \"{child_message}\"")
        parts.append("Respond naturally, warmly, and conversationally to what the child just said.")
        return "\n\n".join(parts)


class ContextBuilder:
    """Assembles isolated, compact context for chat turns."""

    @classmethod
    def build(
        cls,
        child_pseudonym: str,
        current_level: str,
        selected_mode: str,
        child_message: str,
        target_skill: str | None = None,
        mastered_skills: list[str] | None = None,
        recent_turns: list[dict[str, str]] | None = None,
    ) -> tuple[str, str]:
        """Return (system_instruction, user_prompt) tuple."""
        context = CompactContext(
            pseudonym=child_pseudonym or "Friend",
            level=current_level or "L1",
            mode=selected_mode or "learning",
            target_skill=target_skill,
            mastered_skills=mastered_skills or [],
            recent_turns=recent_turns or [],
        )
        return context.build_system_instruction(), context.build_user_prompt(child_message)
