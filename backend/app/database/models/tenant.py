from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database.models.base import Base


class Tenant(Base):
    """
    Multi-tenant organization boundary.
    Sessions and users are scoped to a tenant for data isolation.
    """

    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="tenant")
    sessions = relationship("TrainingSession", back_populates="tenant")
