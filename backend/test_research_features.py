"""Focused, offline tests for the additive research mechanisms."""

from datetime import datetime
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models.base import Base
from app.database.models.tenant import Tenant
from app.database.models.user import User
from app.database.models.training_session import TrainingSession
from app.database.models.research import AttackExecutionRecord, AdaptationDecision, TraineeSkillProfile
from app.schemas.evaluation_schema import EvaluationResult
from app.services.investigation.investigation_tracker import InvestigationTracker
from app.services.research.execution_telemetry_service import ExecutionTelemetryService
from app.services.research.adaptive_services import AdaptiveAttackerService, AdaptiveDifficultyService, TraineeSkillService


def make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


class SafeLab:
    def execute_validated_action(self, session_id, action_id, lab_key):
        assert action_id in {"web_health_check", "internal_auth_check", "report_export_check"}
        return f"safe:{action_id}"


def test_execution_validation_records_real_and_unsupported_steps():
    db = make_db()
    with patch.object(ExecutionTelemetryService, "_artifact_lines", return_value=[{"source": "simulation_log", "line": "WEB_ACCESS service=target"}]):
        result = ExecutionTelemetryService.validate_plan(
            db, 100, {"attack_chain": ["Network reconnaissance", "Privilege escalation"]}, "docker", SafeLab(), "safe-key"
        )
    assert result["execution_fidelity_score"] == 1.0
    assert result["execution_records"][0]["execution_status"] == "EXECUTED"
    assert result["execution_records"][1]["execution_status"] == "NOT_EXECUTED"
    assert "No safe bounded" in result["execution_records"][1]["error"]
    assert result["telemetry_records"][0]["telemetry_fidelity_score"] == 1.0


def test_adaptive_difficulty_and_observable_skill_profile():
    db = make_db()
    tenant = Tenant(name="Research tenant", slug="research")
    user = User(email="research@example.test", username="researcher", hashed_password="hash", tenant=tenant)
    session = TrainingSession(session_name="test", difficulty="BEGINNER", status="active", user=user, tenant=tenant, created_at=datetime.utcnow())
    db.add_all([tenant, user, session])
    db.commit()
    tracker = InvestigationTracker().create_session(session.id)
    tracker.record_command("grep suspicious /var/log/auth.log", "match", 0)
    tracker.record_artifact_inspected("simulation")
    evaluation = EvaluationResult(session_id=session.id, score=85, findings_score=30, commands_score=20, severity_score=15, root_cause_score=15, mitigation_score=5, matched_findings=["finding"], matched_commands=["grep suspicious /var/log/auth.log"], missed_findings=[], missed_commands=[], matched_mitigation=[], missed_mitigation=[])
    first = TraineeSkillService.update(db, session, user, evaluation, tracker)
    second = TraineeSkillService.update(db, session, user, evaluation, tracker)
    profile = db.query(TraineeSkillProfile).one()
    assert first["sessions_completed"] == 1
    assert second["sessions_completed"] == 1
    assert profile.sessions_completed == 1
    selected, decision = AdaptiveDifficultyService.resolve(db, user, "adaptive")
    assert selected == "BEGINNER" and decision["mode"] == "adaptive"


def test_adaptive_attacker_only_records_predefined_choice():
    db = make_db()
    tenant = Tenant(name="Other tenant", slug="other")
    user = User(email="other@example.test", username="other", hashed_password="hash", tenant=tenant)
    session = TrainingSession(session_name="test", difficulty="BEGINNER", status="active", user=user, tenant=tenant)
    db.add_all([tenant, user, session])
    db.commit()
    tracker = InvestigationTracker().create_session(session.id)
    tracker.record_command("cat /var/log/auth.log", "", 0)
    decision = AdaptiveAttackerService.consider(db, session, user, tracker, "mock")
    stored = db.query(AdaptationDecision).one()
    assert decision["selected_action"] == "continue_planned_path"
    assert stored.candidate_actions_json == '["continue_planned_path", "alternate_safe_internal_check"]'


if __name__ == "__main__":
    test_execution_validation_records_real_and_unsupported_steps()
    test_adaptive_difficulty_and_observable_skill_profile()
    test_adaptive_attacker_only_records_predefined_choice()
    print("research feature tests passed")
