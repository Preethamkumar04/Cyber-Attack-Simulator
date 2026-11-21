from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.models.base import Base


class TrainingSession(Base):

    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_name = Column(String)
    difficulty = Column(String)
    status = Column(String)
    attack_mode = Column(String, nullable=True)
    docker_lab_key = Column(String, nullable=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)

    scenario_json = Column(Text, nullable=True)
    response_json = Column(Text, nullable=True)
    evaluation_json = Column(Text, nullable=True)
    behavior_json = Column(Text, nullable=True)
    difficulty_adaptation_json = Column(Text, nullable=True)
    score = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")
    tenant = relationship("Tenant", back_populates="sessions")
