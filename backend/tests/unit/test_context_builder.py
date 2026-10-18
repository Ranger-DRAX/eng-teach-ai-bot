"""Unit tests for ContextBuilder.

Tests:
1. Child isolation: no context leaks across child profiles.
2. Context minimization: historical turns are strictly capped.
3. Level-dependent word count rules.
4. Mode-specific instruction formatting.
"""

from __future__ import annotations

import pytest

from app.context.context_builder import ContextBuilder


def test_child_isolation_no_data_leakage():
    """Verify context for Child A contains zero information about Child B."""
    sys_a, prompt_a = ContextBuilder.build(
        child_pseudonym="ChildA_Leo",
        current_level="L1",
        selected_mode="learning",
        child_message="Cat!",
        target_skill="l1_animals",
        mastered_skills=["l1_colors"],
        recent_turns=[{"child": "Red!", "bot": "Good job!"}],
    )

    sys_b, prompt_b = ContextBuilder.build(
        child_pseudonym="ChildB_Mia",
        current_level="L2",
        selected_mode="conversation",
        child_message="I like dogs",
        target_skill="l2_verbs",
        mastered_skills=["l1_food"],
        recent_turns=[{"child": "Apple", "bot": "Yummy!"}],
    )

    # Child A's prompt must contain Child A's info and NOT Child B's info
    assert "ChildA_Leo" in prompt_a
    assert "ChildB_Mia" not in prompt_a
    assert "l1_animals" in prompt_a
    assert "l2_verbs" not in prompt_a
    assert "Red!" in prompt_a
    assert "Apple" not in prompt_a

    # Child B's prompt must contain Child B's info and NOT Child A's info
    assert "ChildB_Mia" in prompt_b
    assert "ChildA_Leo" not in prompt_b
    assert "l2_verbs" in prompt_b
    assert "l1_animals" not in prompt_b
    assert "Apple" in prompt_b
    assert "Red!" not in prompt_b


def test_context_minimization_caps_recent_history():
    """Verify that history is capped to the last 3 turns even if 20 turns exist."""
    many_turns = [{"child": f"word_{i}", "bot": f"reply_{i}"} for i in range(20)]
    _, prompt = ContextBuilder.build(
        child_pseudonym="Sam",
        current_level="L1",
        selected_mode="learning",
        child_message="Blue",
        recent_turns=many_turns,
    )

    # Turns from earlier in the session must NOT be included in prompt
    assert "word_0" not in prompt
    assert "word_10" not in prompt
    assert "word_16" not in prompt

    # Only last 3 turns (17, 18, 19) should appear
    assert "word_17" in prompt
    assert "word_18" in prompt
    assert "word_19" in prompt


@pytest.mark.parametrize(
    "level,expected_max_words",
    [
        ("L1", 15),
        ("L2", 30),
        ("L3", 50),
    ],
)
def test_level_dependent_word_caps(level: str, expected_max_words: int):
    """Verify system instruction explicitly specifies the word cap for the level."""
    sys_inst, _ = ContextBuilder.build(
        child_pseudonym="Alex",
        current_level=level,
        selected_mode="learning",
        child_message="Hello",
    )
    assert f"Maximum {expected_max_words} words" in sys_inst
    assert f"CURRENT LEVEL: {level}" in sys_inst


@pytest.mark.parametrize(
    "mode,expected_guidance",
    [
        ("learning", "Learning mode. Focus on vocabulary practice"),
        ("conversation", "Conversation mode. Chat naturally"),
        ("engagement", "Engagement mode. Play a simple guessing game"),
        ("support", "Support mode. Be calming, encouraging"),
    ],
)
def test_mode_specific_instructions(mode: str, expected_guidance: str):
    """Verify system instruction contains correct guidance for each mode."""
    sys_inst, _ = ContextBuilder.build(
        child_pseudonym="Tara",
        current_level="L1",
        selected_mode=mode,
        child_message="Hi",
    )
    assert expected_guidance in sys_inst
