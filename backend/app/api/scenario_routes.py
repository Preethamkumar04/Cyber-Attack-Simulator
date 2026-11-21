

from app.schemas.evaluation_schema import AnalystResponse, EvaluationRequest

from fastapi import APIRouter, Depends, HTTPException, status

from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.database.models.user import User

from app.services.ai_generator.scenario_builder import (
    ScenarioBuilder
)
from app.services.investigation.investigation_tracker import (
    investigation_tracker
)
from app.services.docker.engine_factory import get_attack_engine
from app.services.docker.lab_manager import DockerLabError, DockerLabManager, DockerUnavailableError

from app.services.ai_generator.feedback_generator import (
    FeedbackGenerator
)

from app.services.session.session_service import (
    SessionService
)

from app.services.artifacts.artifact_manager import (
    ArtifactManager
)

from app.services.evaluation.scoring_engine import (
    ScoringEngine
)

from app.services.evaluation.evaluation_builder import (
    EvaluationBuilder
)
from app.services.research.execution_telemetry_service import ExecutionTelemetryService
from app.services.research.adaptive_services import AdaptiveDifficultyService, TraineeSkillService
router = APIRouter()

builder = ScenarioBuilder()


class ScenarioRequest(BaseModel):
    difficulty: str

@router.post("/start")
def start_scenario(
    request: ScenarioRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # ---------------------------------------------------------
    # Generate AI scenario
    # ---------------------------------------------------------

    effective_difficulty, difficulty_decision = AdaptiveDifficultyService.resolve(
        db, current_user, request.difficulty
    )
    scenario = builder.generate(effective_difficulty)

    # ---------------------------------------------------------
    # Create training session FIRST
    #
    # This gives us the session_id that will be used for
    # all simulation artifacts.
    # ---------------------------------------------------------

    training_session = SessionService.create_session(
        db=db,
        difficulty=effective_difficulty,
        user=current_user,
        scenario=scenario,
        attack_mode=scenario.attack_mode,
    )

    session_id = training_session.id
    AdaptiveDifficultyService.record(db, training_session, current_user, difficulty_decision)
    db.commit()

    # ---------------------------------------------------------
    # Clear artifacts belonging ONLY to this session
    # ---------------------------------------------------------

    ArtifactManager.clear_artifacts(
        session_id
    )

    # ---------------------------------------------------------
    # Create investigation tracker
    # ---------------------------------------------------------

    investigation_tracker.create_session(
        session_id
    )

    # ---------------------------------------------------------
    # Use only visible scenario data for frontend
    # ---------------------------------------------------------

    visible_scenario = scenario.to_visible_dict()

    # ---------------------------------------------------------
    # Pass full scenario to simulation engine
    # ---------------------------------------------------------

    scenario_dict = scenario.model_dump()

    attack_engine = get_attack_engine()

    try:
        simulation_result = attack_engine.run_simulation(scenario_dict, session_id, training_session.docker_lab_key)
    except DockerUnavailableError as exc:
        training_session.status = "docker_unavailable"
        db.commit()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except DockerLabError as exc:
        training_session.status = "docker_failed"
        db.commit()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Docker lab failed: {exc}") from exc

    engine_type = attack_engine.get_engine_type()
    research = ExecutionTelemetryService.validate_plan(
        db=db,
        session_id=session_id,
        scenario=scenario_dict,
        engine_type=engine_type,
        lab_manager=DockerLabManager() if engine_type == "docker" else None,
        lab_key=training_session.docker_lab_key,
    )

    # ---------------------------------------------------------
    # Verify generated artifacts for this session
    # ---------------------------------------------------------

    artifact_status = (
        ArtifactManager.verify_artifacts(
            session_id
        )
    )

    artifact_paths = (
        ArtifactManager.get_artifact_paths(
            session_id
        )
    )

    # ---------------------------------------------------------
    # Return training session + simulation information
    # ---------------------------------------------------------

    return {
        "session_id": session_id,
        "session_name": training_session.session_name,
        "difficulty": training_session.difficulty,
        "difficulty_adaptation": difficulty_decision,
        "status": training_session.status,
        "simulation": simulation_result,
        "scenario": visible_scenario,
        "research": research,
        "artifacts": {
            "paths": artifact_paths,
            "status": artifact_status
        }
    }


def _get_owned_session(session_id: int, db: Session, current_user: User):
    session = SessionService.get_session_for_user(db, session_id, current_user)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.get("/{session_id}/status")
def get_lab_status(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = _get_owned_session(session_id, db, current_user)
    return DockerLabManager().status(session_id, session.docker_lab_key)


@router.post("/{session_id}/reset")
def reset_lab(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = _get_owned_session(session_id, db, current_user)
    try:
        return DockerLabManager().reset_lab(session_id, session.docker_lab_key)
    except DockerLabError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.delete("/{session_id}/lab")
def remove_lab(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = _get_owned_session(session_id, db, current_user)
    try:
        DockerLabManager().remove_lab(session_id, session.docker_lab_key)
    except DockerLabError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return {"session_id": session_id, "status": "removed"}

@router.post("/submit-response")
def submit_response(
    response: AnalystResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    session = SessionService.get_session_for_user(
        db,
        response.session_id,
        current_user
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    SessionService.save_response(
        db,
        session,
        response
    )

    return {
        "message": "Response submitted successfully.",
        "session_id": response.session_id
    }


@router.post("/evaluate")
def evaluate_session(
    request: EvaluationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    session = SessionService.get_session_for_user(
        db,
        request.session_id,
        current_user
    )

    if session is None:
        return {
            "error": "Scenario not found."
        }

    scenario = SessionService.load_scenario(
        session
    )

    if scenario is None:
        return {
            "error": "Scenario not found."
        }

    response = SessionService.load_response(
        session
    )

    if response is None:
        return {
            "error": "Analyst response not submitted."
        }

    expected = {
        "findings": scenario.expected_findings,
        "commands": scenario.expected_commands,
        "severity": scenario.expected_severity,
        "root_cause": scenario.expected_root_cause,
        "mitigation": scenario.expected_mitigation
    }

    result = EvaluationBuilder.evaluate(
        expected,
        response
    )


    SessionService.save_evaluation(
        db,
        session,
        result
    )

    skill_profile = TraineeSkillService.update(
        db,
        session,
        current_user,
        result,
        investigation_tracker.get_session(session.id),
    )

    return {**result.model_dump(), "skill_profile": skill_profile}
