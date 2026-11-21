import json
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models.training_session import TrainingSession
from app.database.models.user import User
from app.schemas.evaluation_schema import AnalystResponse, EvaluationResult
from app.schemas.scenario_schema import ScenarioSchema


class SessionService:

    @staticmethod
    def create_session(
        db: Session,
        difficulty: str,
        user: User,
        scenario: ScenarioSchema,
        attack_mode: Optional[str] = None,
    ) -> TrainingSession:
        session = TrainingSession(
            session_name=f"{difficulty.capitalize()} Attack Simulation",
            difficulty=difficulty,
            status="active",
            attack_mode=attack_mode or scenario.attack_mode,
            docker_lab_key=uuid.uuid4().hex[:12],
            user_id=user.id,
            tenant_id=user.tenant_id,
            scenario_json=json.dumps(scenario.model_dump()),
        )

        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session_for_user(
        db: Session,
        session_id: int,
        user: User,
    ) -> Optional[TrainingSession]:
        return (
            db.query(TrainingSession)
            .filter(
                TrainingSession.id == session_id,
                TrainingSession.tenant_id == user.tenant_id,
            )
            .first()
        )

    @staticmethod
    def list_sessions(
        db: Session,
        user: User,
        limit: int = 50,
    ) -> List[TrainingSession]:
        return (
            db.query(TrainingSession)
            .filter(TrainingSession.tenant_id == user.tenant_id)
            .order_by(TrainingSession.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def save_response(
        db: Session,
        session: TrainingSession,
        response: AnalystResponse,
    ) -> TrainingSession:
        session.response_json = json.dumps(response.model_dump())
        session.status = "submitted"
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def save_evaluation(
        db: Session,
        session: TrainingSession,
        evaluation: EvaluationResult,
    ) -> TrainingSession:
        session.evaluation_json = json.dumps(evaluation.model_dump())
        session.score = evaluation.score
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def load_scenario(session: TrainingSession) -> Optional[ScenarioSchema]:
        if not session.scenario_json:
            return None
        return ScenarioSchema(**json.loads(session.scenario_json))

    @staticmethod
    def load_response(session: TrainingSession) -> Optional[AnalystResponse]:
        if not session.response_json:
            return None
        return AnalystResponse(**json.loads(session.response_json))

    @staticmethod
    def load_evaluation(session: TrainingSession) -> Optional[EvaluationResult]:
        if not session.evaluation_json:
            return None
        return EvaluationResult(**json.loads(session.evaluation_json))

    @staticmethod
    def get_analytics(db: Session, user: User) -> dict:
        base_query = db.query(TrainingSession).filter(
            TrainingSession.tenant_id == user.tenant_id
        )

        total_sessions = base_query.count()
        completed = base_query.filter(TrainingSession.status == "completed")

        completed_sessions = completed.count()
        average_score = (
            completed.with_entities(func.avg(TrainingSession.score)).scalar() or 0.0
        )
        best_score = (
            completed.with_entities(func.max(TrainingSession.score)).scalar() or 0.0
        )

        difficulty_rows = (
            db.query(
                TrainingSession.difficulty,
                func.count(TrainingSession.id),
                func.avg(TrainingSession.score),
            )
            .filter(
                TrainingSession.tenant_id == user.tenant_id,
                TrainingSession.status == "completed",
            )
            .group_by(TrainingSession.difficulty)
            .all()
        )

        scores_by_difficulty = [
            {
                "difficulty": row[0],
                "count": row[1],
                "average_score": round(row[2] or 0, 2),
            }
            for row in difficulty_rows
        ]

        difficulty_distribution = [
            {
                "difficulty": row[0],
                "count": row[1],
            }
            for row in (
                db.query(
                    TrainingSession.difficulty,
                    func.count(TrainingSession.id),
                )
                .filter(TrainingSession.tenant_id == user.tenant_id)
                .group_by(TrainingSession.difficulty)
                .all()
            )
        ]

        attack_mode_distribution = [
            {
                "attack_mode": row[0] or "unknown",
                "count": row[1],
            }
            for row in (
                db.query(
                    TrainingSession.attack_mode,
                    func.count(TrainingSession.id),
                )
                .filter(TrainingSession.tenant_id == user.tenant_id)
                .group_by(TrainingSession.attack_mode)
                .all()
            )
        ]

        recent_completed = (
            completed.order_by(TrainingSession.completed_at.desc())
            .limit(20)
            .all()
        )

        scores_over_time = [
            {
                "session_id": item.id,
                "label": item.completed_at.strftime("%Y-%m-%d")
                if item.completed_at
                else "",
                "score": item.score or 0,
                "difficulty": item.difficulty,
            }
            for item in reversed(recent_completed)
        ]

        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "average_score": round(average_score, 2),
            "best_score": round(best_score, 2),
            "scores_by_difficulty": scores_by_difficulty,
            "scores_over_time": scores_over_time,
            "difficulty_distribution": difficulty_distribution,
            "attack_mode_distribution": attack_mode_distribution,
        }
