# Mode Policy Specification

**Document Version:** 1.0.0  
**Status:** Baseline (Phase 2)  
**Authority:** Backend mode manager — the LLM does not select, change, or route modes.

---

## 1. Mode Definitions

| Mode | Purpose | Typical Behavior |
|---|---|---|
| **`learning`** | Explicit pedagogical practice | Vocabulary drills, phrase completion, guided Q&A, assessment activities |
| **`conversation`** | Open, child-led dialogue | Friendly discussion about topics the child raises; no forced exercises |
| **`engagement`** | Playful interaction | Word games, rhymes, riddles, roleplay, creative activities |
| **`support`** | Emotional comfort and breaks | Encouragement, reassurance, calming responses, offering to pause or change topic |

---

## 2. Mode Selection Priority Rules

The mode manager evaluates signals in strict priority order. The first matching rule wins:

### Priority 1 — Safety / Support Triggers (Highest)
* If child input contains explicit distress signals (`"I want to cry"`, `"I'm scared"`, `"help me"`, `"too hard"`, `"I can't do this"`): → **`support`**
* If child input contains explicit stop/break requests (`"stop"`, `"I'm done"`, `"no more"`, `"bye"`, `"quit"`): → **`support`**
* Rationale: Child wellbeing and autonomy always override curriculum goals.

### Priority 2 — Explicit Child Intent
* If child input contains explicit learning request (`"teach me"`, `"let's learn"`, `"quiz me"`, `"practice"`): → **`learning`**
* If child input contains explicit play/game request (`"let's play"`, `"play a game"`, `"tell me a riddle"`, `"let's pretend"`): → **`engagement`**
* If child input shares a topic or asks a question (`"I like cats"`, `"what's your name?"`, `"do you like pizza?"`): → **`conversation`**

### Priority 3 — Session Context
* If the current session has an active learning exercise in progress and the child provides a response to that exercise: → **`learning`** (continue exercise)
* If the previous turn was `engagement` and the child responds within the game context: → **`engagement`** (continue game)

### Priority 4 — Default Behavior
* If no explicit intent is detected and no session context applies: → **`learning`** (default to pedagogical practice)
* Rationale: The default serves the educational mission while remaining overridable by any explicit child request.

---

## 3. Mode Transition Rules

### 3.1 Explicit Requests Always Override
A clear child request to stop, play, learn, or talk about something **immediately overrides** the current mode, even mid-exercise:
* Child says "I want to play a game" during a vocabulary drill → switch to **`engagement`**
* Child says "stop" during a story activity → switch to **`support`**
* Child says "teach me more words" during conversation → switch to **`learning`**

### 3.2 Topic Change Overrides Lesson
If a child introduces a new topic unrelated to the current exercise (e.g., "My dog is fluffy!" during a numbers drill), the mode manager:
1. Treats this as a **`conversation`** intent
2. Switches mode to **`conversation`**
3. Does **not** force the child back into the exercise immediately

### 3.3 Ordinary Messages Are Not Forced Into Quizzes
When mode is `conversation`, a casual statement like "I had pasta today" is responded to conversationally. The backend does **not** inject vocabulary quizzes or assessment activities into every conversational turn.

---

## 4. Ambiguous Signal Handling

### 4.1 Ambiguous Mood Signals
Text like "hmm", "ok", "I don't know", or "maybe" without clear emotional distress:
* Treated as **neutral continuation** of the current mode
* **Not** stored as a permanent emotional state or personality trait
* **Not** escalated to `support` mode unless combined with explicit distress language

### 4.2 Uncertain Intent
If the mode manager cannot confidently classify intent:
* Default to the current active mode (continuation)
* If no mode is active (first turn), default to **`learning`**
* Log the ambiguous input for potential pattern review (pseudonymous, no raw text in logs)

### 4.3 Frustration vs. Learning Struggle
* A single incorrect answer is **not** frustration — it is normal learning
* Multiple incorrect answers trigger **review behavior** in the progression engine, not an automatic mode switch
* Only explicit frustration language ("this is too hard", "I hate this", "I can't") triggers **`support`** mode

---

## 5. Support Mode Behavior

When in `support` mode:
1. **Acknowledge the child's feelings** with empathetic language: "It is okay to feel that way."
2. **Offer choices**: "Would you like to try something easier, play a game, or take a break?"
3. **Do not diagnose**: Never label a child as anxious, depressed, hyperactive, or assign any clinical term.
4. **Do not force return to learning**: The child must explicitly indicate readiness to resume.
5. **Session boundary**: If the child remains in support mode for 3+ consecutive turns without re-engaging, gently suggest coming back later: "We can play again whenever you are ready!"

---

## 6. Non-Diagnostic Emotional Handling

| Principle | Implementation |
|---|---|
| **Transient signals only** | Detected sentiment (e.g., "frustrated", "happy") is held only in the current turn's ephemeral context |
| **No permanent labels** | The PostgreSQL child profile schema has no mood, personality, or diagnosis columns |
| **No clinical terminology** | Generated responses never include words like "anxiety", "depression", "ADHD", "disorder", "diagnosis" |
| **No secondary profiling** | Emotional signals are never aggregated, trended, or used for non-educational purposes |
| **Human escalation path** | If a child consistently expresses severe distress across multiple sessions, the system surfaces a recommendation to the parent dashboard suggesting they consult a qualified professional |

---

## 7. Safe Fallback Behavior

If the mode manager encounters an error or cannot determine any mode:
* Default to **`learning`** mode
* Use a safe, pre-written greeting appropriate to the child's current level
* Log the fallback event with correlation ID
* Set `fallback_used: true` in the turn response
