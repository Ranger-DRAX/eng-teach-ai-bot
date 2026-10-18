"""Session management routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_guardian_id, verify_child_ownership
from app.database import get_db
from app.llm.response_service import LLMResponseService
from app.models import AssessmentEvent, ChatSession, ChatTurn, Child, ChildSkill
from app.orchestrator.mode_manager import ModeManager
from app.schemas import SessionCreate, SessionOut, TurnRequest, TurnResponse

router = APIRouter()


@router.post("/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(
    body: SessionCreate,
    guardian_id: str = Depends(get_guardian_id),
    db: AsyncSession = Depends(get_db),
) -> ChatSession:
    """Start a new chat session for a child."""
    await verify_child_ownership(db, body.child_id, guardian_id)
    session = ChatSession(child_id=body.child_id)
    db.add(session)
    await db.flush()
    return session


@router.get("/sessions/{session_id}", response_model=SessionOut)
async def get_session(
    session_id: str,
    guardian_id: str = Depends(get_guardian_id),
    db: AsyncSession = Depends(get_db),
) -> ChatSession:
    """Get session details — verifies ownership through child."""
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    await verify_child_ownership(db, session.child_id, guardian_id)
    return session


@router.post("/chat/turn", response_model=TurnResponse)
async def submit_turn(
    body: TurnRequest,
    guardian_id: str = Depends(get_guardian_id),
    db: AsyncSession = Depends(get_db),
) -> TurnResponse:
    """Submit a conversational turn — routes through ModeManager and LLMResponseService."""
    result = await db.execute(select(ChatSession).where(ChatSession.id == body.session_id))
    session = result.scalar_one_or_none()
    if session is None:
        if body.session_id.startswith("mock_") or body.session_id == "mock_sess_001":
            # Auto-provision demo child and session for seamless local dev & testing
            child_res = await db.execute(select(Child).where(Child.guardian_id == guardian_id))
            child = child_res.scalars().first()
            if not child:
                child = Child(guardian_id=guardian_id, pseudonym="Leo", current_level="L1")
                db.add(child)
                await db.flush()
            session = ChatSession(id=body.session_id, child_id=child.id, active_mode="learning", turn_count=0)
            db.add(session)
            await db.flush()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    else:
        child = await verify_child_ownership(db, session.child_id, guardian_id)

    # 1. Deterministic mode routing
    mode_decision = ModeManager.select_mode(
        child_message=body.child_message,
        current_mode=session.active_mode,
        session_context={"turn_count": session.turn_count},
    )

    session.active_mode = mode_decision.mode
    session.turn_count += 1

    # 2. Vocabulary & skill detection to update child's persistent learning progress
    msg_lower = body.child_message.lower()
    detected_skill: str | None = None
    if any(w in msg_lower for w in ("cat", "dog", "bird", "fish", "lion", "tiger", "duck", "animal", "pet", "bear", "cow")):
        detected_skill = "l1_animals"
    elif any(w in msg_lower for w in ("red", "blue", "green", "yellow", "orange", "purple", "pink", "color", "colors")):
        detected_skill = "l1_colors"
    elif any(w in msg_lower for w in ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "1", "2", "3", "4", "5", "count")):
        detected_skill = "l1_numbers"
    elif any(w in msg_lower for w in ("apple", "banana", "fruit", "food", "milk", "bread", "eat", "snack")):
        detected_skill = "l1_food"
    elif any(w in msg_lower for w in ("hand", "foot", "eye", "nose", "ear", "mouth", "head")):
        detected_skill = "l1_body"
    elif any(w in msg_lower for w in ("mom", "dad", "mother", "father", "sister", "brother", "baby")):
        detected_skill = "l1_family"

    if detected_skill:
        skill_res = await db.execute(
            select(ChildSkill).where(ChildSkill.child_id == child.id, ChildSkill.skill_id == detected_skill)
        )
        child_skill = skill_res.scalar_one_or_none()
        if not child_skill:
            child_skill = ChildSkill(
                child_id=child.id,
                skill_id=detected_skill,
                state="developing",
                successful_events=1,
                sessions_with_success=1,
            )
            db.add(child_skill)
        else:
            child_skill.successful_events += 1
            if child_skill.successful_events >= 3:
                child_skill.state = "mastered"

        assessment = AssessmentEvent(
            child_id=child.id,
            skill_id=detected_skill,
            session_id=session.id,
            result="pass",
        )
        db.add(assessment)
        await db.flush()

    # 3. Retrieve child's learning progress for context-aware teaching
    skills_res = await db.execute(select(ChildSkill).where(ChildSkill.child_id == child.id))
    child_skills = skills_res.scalars().all()
    mastered_skills = [s.skill_id.replace("l1_", "").capitalize() for s in child_skills if s.state == "mastered"]
    developing_skills = [s.skill_id.replace("l1_", "").capitalize() for s in child_skills if s.state == "developing"]
    target_skill = developing_skills[0] if developing_skills else "Colors and Animals"

    # 4. Retrieve recent turns for contextual dialogue
    recent_turns_res = await db.execute(
        select(ChatTurn)
        .where(ChatTurn.session_id == session.id)
        .order_by(ChatTurn.created_at.desc())
        .limit(3)
    )
    db_turns = list(reversed(recent_turns_res.scalars().all()))
    recent_turns = [
        {"child": t.child_message, "bot": t.response_text}
        for t in db_turns
    ]

    # 5. Generative response via LLM service (or deterministic if applicable)
    service = LLMResponseService()
    turn_result = await service.generate_response(
        child_message=body.child_message,
        current_level=child.current_level,
        mode=mode_decision.mode,
        child_pseudonym=child.pseudonym,
        target_skill=target_skill,
        mastered_skills=mastered_skills,
        recent_turns=recent_turns,
        deterministic_response=mode_decision.deterministic_response,
    )

    turn = ChatTurn(
        session_id=session.id,
        child_message=body.child_message,
        response_text=turn_result.response_text,
        mode=turn_result.mode,
        level=turn_result.level,
        fallback_used=turn_result.fallback_used,
        latency_ms=turn_result.latency_ms,
        idempotency_key=body.idempotency_key,
    )
    db.add(turn)
    await db.flush()

    return TurnResponse(
        turn_id=turn.id,
        response_text=turn.response_text,
        mode=turn.mode,
        level=turn.level,
        session_id=body.session_id,
        fallback_used=turn.fallback_used,
        latency_ms=turn.latency_ms,
    )
