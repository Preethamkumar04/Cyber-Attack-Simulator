"""
Session history routes — tenant-scoped training session listing and detail.
"""

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.database.models.user import User
from app.schemas.session_schema import SessionDetail, SessionSummary
from app.services.session.session_service import SessionService
from app.database.models.research import AttackExecutionRecord, TelemetryValidationRecord, AdaptationDecision, TraineeSkillProfile

router = APIRouter()


@router.get("/", response_model=List[SessionSummary])
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = SessionService.list_sessions(db, current_user)
    return sessions


@router.get("/skills/me")
def get_my_skill_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(TraineeSkillProfile).filter(TraineeSkillProfile.user_id == current_user.id, TraineeSkillProfile.tenant_id == current_user.tenant_id).first()
    if profile is None:
        return {"sessions_completed": 0, "metrics": {}, "skill_dimensions": {}}
    return {"sessions_completed": profile.sessions_completed, "metrics": json.loads(profile.metrics_json), "skill_dimensions": json.loads(profile.skill_dimensions_json), "updated_at": profile.updated_at.isoformat()}


@router.get("/{session_id}", response_model=SessionDetail)
def get_session_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = SessionService.get_session_for_user(db, session_id, current_user)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return SessionDetail(
        id=session.id,
        session_name=session.session_name,
        difficulty=session.difficulty,
        status=session.status,
        attack_mode=session.attack_mode,
        score=session.score,
        created_at=session.created_at,
        completed_at=session.completed_at,
        scenario=json.loads(session.scenario_json) if session.scenario_json else None,
        response=json.loads(session.response_json) if session.response_json else None,
        evaluation=json.loads(session.evaluation_json) if session.evaluation_json else None,
        behavior=json.loads(session.behavior_json) if session.behavior_json else None,
        difficulty_adaptation=json.loads(session.difficulty_adaptation_json) if session.difficulty_adaptation_json else None,
    )


@router.get("/{session_id}/research")
def get_session_research(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = SessionService.get_session_for_user(db, session_id, current_user)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    executions = db.query(AttackExecutionRecord).filter(AttackExecutionRecord.session_id == session_id).order_by(AttackExecutionRecord.id).all()
    telemetry = db.query(TelemetryValidationRecord).filter(TelemetryValidationRecord.session_id == session_id).order_by(TelemetryValidationRecord.id).all()
    decisions = db.query(AdaptationDecision).filter(AdaptationDecision.session_id == session_id, AdaptationDecision.tenant_id == current_user.tenant_id).order_by(AdaptationDecision.id).all()
    executable = [record for record in executions if record.executable_action]
    return {
        "execution_fidelity_score": round(sum(1 for record in executable if record.success) / len(executable), 2) if executable else 0.0,
        "execution_records": [{"attack_step_id": r.attack_step_id, "technique": r.technique, "intended_action": r.intended_action, "executable_action": r.executable_action, "execution_status": r.execution_status, "success": r.success, "error": r.error, "evidence": json.loads(r.evidence_json), "timestamp": r.created_at.isoformat()} for r in executions],
        "telemetry_records": [{"attack_step_id": r.attack_step_id, "expected_events": json.loads(r.expected_events_json), "observed_events": json.loads(r.observed_events_json), "matched_events": json.loads(r.matched_events_json), "missing_expected_events": json.loads(r.missing_events_json), "unexpected_events": json.loads(r.unexpected_events_json), "telemetry_fidelity_score": r.telemetry_fidelity_score} for r in telemetry],
        "adaptation_decisions": [{"decision_type": r.decision_type, "current_attack_step": r.current_attack_step, "trainee_state": json.loads(r.trainee_state_json), "candidate_actions": json.loads(r.candidate_actions_json), "selected_action": r.selected_action, "reason": r.reason, "timestamp": r.created_at.isoformat()} for r in decisions],
        "behavior": json.loads(session.behavior_json) if session.behavior_json else None,
        "difficulty_adaptation": json.loads(session.difficulty_adaptation_json) if session.difficulty_adaptation_json else None,
    }

