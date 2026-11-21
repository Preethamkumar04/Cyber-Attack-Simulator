"""
Artifact routes — expose generated simulation artifacts to the frontend.

Why this exists:
  The React logs panel needs read-only access to mock-generated log files
  without direct filesystem access. These endpoints serve artifact content
  produced by MockAttackEngine (or future DockerAttackEngine).
"""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.database.models.user import User
from app.services.session.session_service import SessionService
from app.services.artifacts.artifact_manager import ArtifactManager
from app.services.investigation.investigation_tracker import investigation_tracker

router = APIRouter()

LogType = Literal["simulation", "network", "traffic", "commands"]

LOG_KEY_MAP = {
    "simulation": "simulation_log",
    "network": "network_alerts",
    "traffic": "traffic_log",
    "commands": "command_history",
}


@router.get("/logs/{session_id}/{log_type}")
def get_log_content(
    session_id: int,
    log_type: LogType,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if SessionService.get_session_for_user(db, session_id, current_user) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    investigation_tracker.get_or_create_session(session_id).record_artifact_inspected(log_type)

    paths = ArtifactManager.get_artifact_paths(session_id)
    path_key = LOG_KEY_MAP.get(log_type)

    if not path_key:
        raise HTTPException(status_code=400, detail="Invalid log type")

    file_path = paths[path_key]

    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            content = handle.read()
    except FileNotFoundError:
        content = ""

    lines = [line for line in content.splitlines() if line.strip()]

    return {
        "log_type": log_type,
        "path": file_path,
        "line_count": len(lines),
        "content": content,
        "lines": lines,
    }


@router.get("/status/{session_id}")
def get_artifact_status(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if SessionService.get_session_for_user(db, session_id, current_user) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return {
        "paths": ArtifactManager.get_artifact_paths(session_id),
        "status": ArtifactManager.verify_artifacts(session_id),
    }
