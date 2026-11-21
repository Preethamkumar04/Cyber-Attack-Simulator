"""
Investigation routes.

Provides the trainee's investigation history for a
specific simulation session.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.database.models.user import User
from app.services.investigation.investigation_tracker import (
    investigation_tracker
)

router = APIRouter()


@router.get("/{session_id}")
def get_investigation(
    session_id: int,
    current_user: User = Depends(get_current_user),
):
    record = investigation_tracker.get_session(
        session_id
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation session not found",
        )

    return record.summary()