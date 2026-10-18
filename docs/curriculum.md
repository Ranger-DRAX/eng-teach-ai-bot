# Curriculum Specification

**Document Version:** 1.0.0  
**Status:** Baseline (Phase 2)  
**Target Audience:** Children under 7 years old  
**Reviewer Requirement:** An accredited early-childhood educator must review and sign off on level objectives, vocabulary lists, and activity types before pilot launch.

---

## 1. Curriculum Philosophy

The curriculum is a structured, progressive English-language acquisition pathway for pre-literate and early-literate children. It follows a scaffolded approach where each level builds on observable, assessable skills from the preceding level. All content must be age-appropriate, culturally neutral, non-frightening, and free of adult concepts.

---

## 2. Level Definitions

### Level 1 (L1) — Early Beginner

**Target Profile:** Children with no or minimal English exposure.

| Dimension | Specification |
|---|---|
| **Core Objective** | Recognize and produce single English words for common objects, colors, animals, and numbers 1–10 |
| **Prompt Length** | 1–5 words |
| **Response Cap** | 15 words maximum |
| **Vocabulary Scope** | ~50 high-frequency words: colors (red, blue, green, yellow, orange, purple, pink, black, white, brown), animals (cat, dog, bird, fish, bear, rabbit, frog, duck, cow, horse), numbers (1–10), body parts (hand, eye, nose, mouth, ear), family (mom, dad, baby, friend), food (apple, banana, milk, water, bread) |
| **Activity Types** | Vocabulary flashcard matching ("What color is this?"), single-word repetition drills, yes/no identification ("Is this a cat?"), simple rhyming games |
| **Prerequisite Skills** | None |
| **Observable Mastery Indicators** | Child correctly identifies ≥ 3 distinct L1 skills across ≥ 2 separate sessions with ≥ 3 successful assessment events per skill |

### Level 2 (L2) — Emerging Beginner

**Target Profile:** Children who can recognize and produce common single English words.

| Dimension | Specification |
|---|---|
| **Core Objective** | Construct 2–4 word phrases and simple subject-verb-object sentences using familiar vocabulary |
| **Prompt Length** | 3–8 words |
| **Response Cap** | 30 words maximum |
| **Vocabulary Scope** | L1 vocabulary plus ~40 additional words: common verbs (run, jump, eat, drink, sleep, play, read, draw, sing, dance), adjectives (big, small, happy, sad, fast, slow, hot, cold), prepositions (in, on, under), daily objects (ball, book, table, chair, bed, door, shoe, hat, cup, tree) |
| **Activity Types** | Phrase completion ("The cat is ___"), simple sentence building ("I like ___"), picture description prompts ("Tell me about the dog"), guided question-answer ("What do you eat for breakfast?") |
| **Prerequisite Skills** | All L1 prerequisite skills mastered; minimum 3 L1 skills in `mastered` state |
| **Observable Mastery Indicators** | Child correctly produces ≥ 3 distinct L2 skills across ≥ 2 separate sessions with ≥ 3 successful assessment events per skill |

### Level 3 (L3) — Early Communicator

**Target Profile:** Children who can form simple English sentences.

| Dimension | Specification |
|---|---|
| **Core Objective** | Engage in multi-turn dialogue, use compound sentences, descriptive language, and basic storytelling |
| **Prompt Length** | 5–15 words |
| **Response Cap** | 50 words maximum |
| **Vocabulary Scope** | L1 + L2 vocabulary plus ~30 additional words: feelings (excited, scared, surprised, tired, brave), connectors (and, but, because, then), time words (today, tomorrow, yesterday, morning, night), question words (who, what, where, when, why) |
| **Activity Types** | Open-ended conversation ("Tell me a story about a bear"), descriptive prompts ("What happened at the park?"), sequencing activities ("First... then... finally..."), creative word games, guided roleplay |
| **Prerequisite Skills** | All L1 skills mastered; minimum 3 L2 skills in `mastered` state |
| **Observable Mastery Indicators** | Child engages in coherent multi-turn exchanges, uses connectors and descriptive words, demonstrates sequencing ability across ≥ 2 sessions |

---

## 3. Skill Taxonomy

Each level contains a defined set of assessable skills:

| Level | Skill ID | Skill Name | Description |
|---|---|---|---|
| L1 | `l1_colors` | Color identification | Name basic colors when prompted |
| L1 | `l1_animals` | Animal vocabulary | Identify and name common animals |
| L1 | `l1_numbers` | Number recognition | Count and identify numbers 1–10 |
| L1 | `l1_body` | Body parts | Name basic body parts |
| L1 | `l1_family` | Family words | Use family-related vocabulary |
| L1 | `l1_food` | Food vocabulary | Name common foods and drinks |
| L2 | `l2_phrases` | Phrase construction | Form 2–4 word phrases |
| L2 | `l2_verbs` | Action verbs | Use common verbs in context |
| L2 | `l2_adjectives` | Descriptive words | Apply adjectives to nouns |
| L2 | `l2_sentences` | Simple sentences | Build subject-verb-object sentences |
| L2 | `l2_questions` | Question responses | Answer simple what/where/who questions |
| L3 | `l3_conversation` | Multi-turn dialogue | Sustain coherent conversation across turns |
| L3 | `l3_storytelling` | Basic storytelling | Narrate simple sequential events |
| L3 | `l3_connectors` | Connector usage | Use and, but, because in sentences |
| L3 | `l3_description` | Descriptive language | Describe objects, scenes, or events |

---

## 4. Content Boundaries

The following categories of content are **strictly prohibited** in all curriculum materials, chatbot prompts, and generated responses:

* Violence, weapons, fighting, or physical harm
* Death, dying, ghosts, or frightening supernatural concepts
* Medical procedures, illness details, or clinical terminology
* Adult romantic or sexual content
* Political, religious, or culturally controversial topics
* Real-world news events, disasters, or tragedies
* Complex abstract concepts beyond early-childhood developmental stage
* Profanity, slang, or derogatory language
* References to specific commercial brands or products

---

## 5. SEL Integration in Curriculum

### 5.1 SEL Principles
Social and Emotional Learning is integrated as a supportive overlay on language instruction:
* **Self-awareness:** "How do you feel today?" prompts in L2/L3 conversational modes
* **Self-management:** Encouraging persistence: "Let us try again! You are doing great!"
* **Social awareness:** Cooperative language: "What does your friend like?"
* **Relationship skills:** Polite interaction modeling: "Please", "Thank you", "Good job!"

### 5.2 SEL Boundaries
* SEL is supportive education, not therapy or clinical intervention.
* The chatbot does not diagnose emotions, learning disabilities, or behavioral conditions.
* Detected frustration or sadness triggers a supportive mode switch — never a stored label.
* Human educator or counselor escalation pathways should be documented for parents.

### 5.3 Sample SEL Responses

| Detected Signal | Example Response | What It Is NOT |
|---|---|---|
| "I can't do this" | "It is okay! Let us try something easier. You are learning!" | A diagnosis of inability |
| "I'm sad" | "I hear you. Would you like to talk about something fun?" | A therapy session |
| "This is boring" | "Let us play a game instead! What animal do you like?" | A behavioral judgment |
| "I don't want to" | "That is fine! We can take a break. What do you want to do?" | A coercive override |

### 5.4 Human Review Criteria
An educator or SEL specialist must verify before pilot launch:
1. Response tone is warm, encouraging, and non-judgmental
2. No clinical or diagnostic language appears in any response template
3. Emotional cues are handled as transient signals, not permanent labels
4. Escalation guidance for persistent distress is documented for parents
