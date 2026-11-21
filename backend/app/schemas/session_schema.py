from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SessionSummary(BaseModel):
    id: int
    session_name: str
    difficulty: str
    status: str
    attack_mode: Optional[str] = None
    score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SessionDetail(SessionSummary):
    scenario: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None
    evaluation: Optional[Dict[str, Any]] = None
    behavior: Optional[Dict[str, Any]] = None
    difficulty_adaptation: Optional[Dict[str, Any]] = None


class AnalyticsOverview(BaseModel):
    total_sessions: int
    completed_sessions: int
    average_score: float
    best_score: float
    scores_by_difficulty: List[Dict[str, Any]]
    scores_over_time: List[Dict[str, Any]]
    difficulty_distribution: List[Dict[str, Any]]
    attack_mode_distribution: List[Dict[str, Any]]
