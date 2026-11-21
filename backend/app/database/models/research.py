"""Small, append-only research records for training-session analysis."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.database.models.base import Base


class AttackExecutionRecord(Base):
    __tablename__ = "attack_execution_records"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=False, index=True)
    attack_step_id = Column(String, nullable=False)
    technique = Column(String, nullable=False)
    intended_action = Column(Text, nullable=False)
    executable_action = Column(Text, nullable=True)
    execution_status = Column(String, nullable=False)
    success = Column(Boolean, default=False, nullable=False)
    error = Column(Text, nullable=True)
    evidence_json = Column(Text, default="[]", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TelemetryValidationRecord(Base):
    __tablename__ = "telemetry_validation_records"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=False, index=True)
    attack_step_id = Column(String, nullable=False)
    expected_events_json = Column(Text, default="[]", nullable=False)
    observed_events_json = Column(Text, default="[]", nullable=False)
    matched_events_json = Column(Text, default="[]", nullable=False)
    missing_events_json = Column(Text, default="[]", nullable=False)
    unexpected_events_json = Column(Text, default="[]", nullable=False)
    telemetry_fidelity_score = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AdaptationDecision(Base):
    __tablename__ = "adaptation_decisions"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    decision_type = Column(String, nullable=False)  # attack_path or difficulty
    current_attack_step = Column(String, nullable=True)
    trainee_state_json = Column(Text, default="{}", nullable=False)
    candidate_actions_json = Column(Text, default="[]", nullable=False)
    selected_action = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TraineeSkillProfile(Base):
    __tablename__ = "trainee_skill_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    metrics_json = Column(Text, default="{}", nullable=False)
    skill_dimensions_json = Column(Text, default="{}", nullable=False)
    sessions_completed = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
