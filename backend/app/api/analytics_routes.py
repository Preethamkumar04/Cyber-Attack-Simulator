"""
Analytics routes — aggregated metrics for tenant dashboard charts.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.database.models.user import User
from app.schemas.session_schema import AnalyticsOverview
from app.services.session.session_service import SessionService

router = APIRouter()


@router.get("/overview", response_model=AnalyticsOverview)
def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SessionService.get_analytics(db, current_user)
