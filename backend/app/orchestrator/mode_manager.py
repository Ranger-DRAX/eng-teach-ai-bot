"""Interaction Mode Manager.

Deterministically selects and manages interaction modes:
- learning: structured curriculum activities and vocabulary practice
- conversation: open-ended chat, sharing, topics of interest
- engagement: games, rhymes, playful interaction
- support: break requests, comforting encouragement, graceful exits

The LLM NEVER determines the interaction mode.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModeDecision:
    """Structured decision explaining mode selection and routing."""

    mode: str
    reason: str
    llm_needed: bool
    deterministic_response: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "mode": self.mode,
            "reason": self.reason,
            "llm_needed": self.llm_needed,
        }
        if self.deterministic_response is not None:
            result["deterministic_response"] = self.deterministic_response
        return result


class ModeManager:
    """Selects interaction mode based on explicit child intent, context, and safety signals."""

    STOP_PATTERNS = [
        r"\b(stop|done|quit|exit|bye|goodbye|break|pause)\b",
        r"i['’]?m done",
        r"i want to stop",
        r"bye\s*bye",
    ]

    FRUSTRATION_PATTERNS = [
        r"too hard",
        r"i can['’]?t do this",
        r"i hate this",
        r"give up",
        r"frustrated",
        r"so hard",
        r"angry",
    ]

    GAME_PATTERNS = [
        r"\b(game|play)\b",
        r"let['’]?s play",
    ]

    LEARNING_PATTERNS = [
        r"\b(teach|learn|lesson|practice|study)\b",
        r"teach me",
    ]

    AMBIGUOUS_PATTERNS = [
        r"^hmm\s*ok\b",
        r"^hmm+$",
        r"^uh+$",
        r"^um+$",
        r"^ok$",
        r"^okay$",
    ]

    TOPIC_SHARE_PATTERNS = [
        r"\b(my dog|my cat|my pet|i like|do you like|i had|i have|look at|today i)\b",
    ]

    @classmethod
    def select_mode(
        cls,
        child_message: str,
        current_mode: str = "learning",
        session_context: dict[str, Any] | None = None,
    ) -> ModeDecision:
        """Select interaction mode deterministically from text message and session context."""
        context = session_context or {}
        active_exercise = bool(context.get("active_exercise", False))
        normalized = child_message.strip().lower()

        # 1. Stop / Break / Bye — Safety and child autonomy always takes highest priority
        for pat in cls.STOP_PATTERNS:
            if re.search(pat, normalized):
                return ModeDecision(
                    mode="support",
                    reason="explicit_stop_request",
                    llm_needed=False,
                    deterministic_response="It is totally okay to take a break! You did great today. See you next time! 🌟",
                )

        # 2. Frustration / Distress — Supportive SEL response, non-diagnostic
        for pat in cls.FRUSTRATION_PATTERNS:
            if re.search(pat, normalized):
                return ModeDecision(
                    mode="support",
                    reason="frustration_signal_detected",
                    llm_needed=False,
                    deterministic_response=(
                        "That is totally okay! Learning new things can be tricky. "
                        "Take a deep breath. We can try something fun whenever you are ready! 💖"
                    ),
                    metadata={"sentiment_stored_permanently": False},
                )

        # 3. Explicit Game / Engagement Request
        for pat in cls.GAME_PATTERNS:
            if re.search(pat, normalized):
                return ModeDecision(
                    mode="engagement",
                    reason="explicit_game_intent",
                    llm_needed=True,
                )

        # 4. Explicit Learning Request
        for pat in cls.LEARNING_PATTERNS:
            if re.search(pat, normalized):
                return ModeDecision(
                    mode="learning",
                    reason="explicit_learning_intent",
                    llm_needed=True,
                )

        # 5. Ambiguous Signals — continue current mode, do not persist mood as fact
        for pat in cls.AMBIGUOUS_PATTERNS:
            if re.search(pat, normalized):
                return ModeDecision(
                    mode=current_mode,
                    reason="ambiguous_continue_current_mode",
                    llm_needed=True,
                    metadata={"sentiment_stored_permanently": False},
                )

        # 6. Active Exercise in Session Context
        if active_exercise:
            # Check if child is overriding the exercise with a new topic
            for pat in cls.TOPIC_SHARE_PATTERNS:
                if re.search(pat, normalized):
                    return ModeDecision(
                        mode="conversation",
                        reason="topic_change_overrides_exercise",
                        llm_needed=True,
                    )
            # Otherwise child is responding to the exercise
            return ModeDecision(
                mode="learning",
                reason="exercise_response_continues",
                llm_needed=False,
                deterministic_response="Great effort! Let's keep going!",
            )

        # 7. Topic Share / Chat in Non-Exercise Context
        for pat in cls.TOPIC_SHARE_PATTERNS:
            if re.search(pat, normalized):
                if current_mode == "learning":
                    return ModeDecision(
                        mode="conversation",
                        reason="topic_share_detected",
                        llm_needed=True,
                    )
                return ModeDecision(
                    mode="conversation",
                    reason="conversation_continues",
                    llm_needed=True,
                )

        # 8. Conversation Continues
        if current_mode == "conversation":
            return ModeDecision(
                mode="conversation",
                reason="conversation_continues",
                llm_needed=True,
            )

        # Default fallback
        return ModeDecision(
            mode=current_mode,
            reason="default_continue_mode",
            llm_needed=True,
        )
