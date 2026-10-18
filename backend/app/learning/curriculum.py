"""Curriculum taxonomy and skill definitions."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SkillDefinition:
    skill_id: str
    name: str
    level: str
    prerequisites: tuple[str, ...] = ()
    target_count: int = 3
    min_sessions: int = 2


L1_SKILLS: dict[str, SkillDefinition] = {
    "l1_colors": SkillDefinition("l1_colors", "Colors", "L1"),
    "l1_animals": SkillDefinition("l1_animals", "Animals", "L1"),
    "l1_numbers": SkillDefinition("l1_numbers", "Numbers 1-10", "L1"),
    "l1_body": SkillDefinition("l1_body", "Body Parts", "L1"),
    "l1_family": SkillDefinition("l1_family", "Family", "L1"),
    "l1_food": SkillDefinition("l1_food", "Food & Drink", "L1"),
}

L2_SKILLS: dict[str, SkillDefinition] = {
    "l2_phrases": SkillDefinition("l2_phrases", "Simple Phrases", "L2", prerequisites=tuple(L1_SKILLS.keys())),
    "l2_verbs": SkillDefinition("l2_verbs", "Action Verbs", "L2", prerequisites=tuple(L1_SKILLS.keys())),
    "l2_adjectives": SkillDefinition("l2_adjectives", "Descriptive Adjectives", "L2", prerequisites=tuple(L1_SKILLS.keys())),
    "l2_objects": SkillDefinition("l2_objects", "Daily Objects", "L2", prerequisites=tuple(L1_SKILLS.keys())),
    "l2_prepositions": SkillDefinition("l2_prepositions", "Basic Prepositions", "L2", prerequisites=tuple(L1_SKILLS.keys())),
}

L3_SKILLS: dict[str, SkillDefinition] = {
    "l3_dialogue": SkillDefinition("l3_dialogue", "Multi-turn Dialogue", "L3"),
    "l3_feelings": SkillDefinition("l3_feelings", "Feelings & Emotion Words", "L3"),
    "l3_connectors": SkillDefinition("l3_connectors", "Conjunctions & Connectors", "L3"),
    "l3_storytelling": SkillDefinition("l3_storytelling", "Sequencing & Storytelling", "L3"),
}

ALL_SKILLS: dict[str, SkillDefinition] = {**L1_SKILLS, **L2_SKILLS, **L3_SKILLS}
L1_REQUIRED_FOR_L2_COUNT = 3
L2_REQUIRED_FOR_L3_COUNT = 3
