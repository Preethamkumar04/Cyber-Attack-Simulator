

"""
Terminal routes — interactive investigation shell API.

Routes trainee commands through the simulated cyber environment.

Commands are handled by CommandParser and operate only against
SimulationState / VirtualFilesystem. They are NEVER executed on
the real host machine.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.services.terminal_generator.command_parser import CommandParser
from app.services.simulator.simulation_session_manager import (
    SimulationSessionManager
)
from app.services.investigation.investigation_tracker import (
    investigation_tracker
)
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.database.models.user import User
from sqlalchemy.orm import Session
from app.services.session.session_service import SessionService
from app.services.docker.lab_manager import DockerLabError, DockerLabManager
from app.services.terminal_generator.terminal_writer import TerminalWriter
from app.services.research.adaptive_services import AdaptiveAttackerService
router = APIRouter()


# ---------------------------------------------------------
# Temporary in-memory simulation storage
# ---------------------------------------------------------
#
# Each session_id gets its own SimulationState.
#
# This allows multiple terminal commands to operate against
# the SAME simulated environment.
#
# Later we can connect this to the proper session manager.
# ---------------------------------------------------------

# _simulation_states: Dict[int, SimulationState] = {}


class TerminalExecuteRequest(BaseModel):
    command: str = Field(
        ...,
        min_length=0,
        max_length=500
    )

    session_id: Optional[int] = None


class TerminalExecuteResponse(BaseModel):
    output: str
    exit_code: int
    prompt: str = "j.smith@WEB-SERVER:~$"


@router.post(
    "/execute",
    response_model=TerminalExecuteResponse
)
def execute_command(
    request: TerminalExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    session_id = request.session_id

    if session_id is None:
        return TerminalExecuteResponse(
            output="Session ID is required.",
            exit_code=1,
        )

    training_session = SessionService.get_session_for_user(db, session_id, current_user)
    if training_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if training_session.status != "active":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Terminal commands are only available for active sessions")

    if settings.ATTACK_ENGINE.lower() == "docker":
        manager = DockerLabManager()
        lab_status = manager.status(session_id, training_session.docker_lab_key)
        if lab_status["state"] != "running":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The session Docker lab is not running")
        try:
            output, exit_code = manager.execute_trainee_command(session_id, request.command, training_session.docker_lab_key)
        except DockerLabError as exc:
            output, exit_code = str(exc), 1
        TerminalWriter.write_history([{"timestamp": __import__("datetime").datetime.now().isoformat(), "command": request.command}], session_id)
        investigation_tracker.get_or_create_session(session_id).record_command(
            command=request.command,
            output=output,
            exit_code=exit_code,
        )
        AdaptiveAttackerService.consider(
            db, training_session, current_user,
            investigation_tracker.get_or_create_session(session_id), "docker", manager,
        )
        return TerminalExecuteResponse(output=output, exit_code=exit_code, prompt="analyst@docker-lab:~$")

    state = SimulationSessionManager.get_session(
        session_id
    )

    if state is None:
        return TerminalExecuteResponse(
            output="Simulation session not found.",
            exit_code=1,
        )

    result = CommandParser.execute(
        request.command,
        state
    )
    tracker = investigation_tracker.get_or_create_session(
        session_id
    )

    tracker.record_command(
        command=request.command,
        output=result.get("output", ""),
        exit_code=0 if result["success"] else 1,
    )

    for file_path in state.discovered_files:
        tracker.record_discovered_file(file_path)

    for file_path in state.accessed_files:
        tracker.record_accessed_file(file_path)

    for directory_path in state.discovered_directories:
        tracker.record_discovered_directory(directory_path)

    AdaptiveAttackerService.consider(
        db, training_session, current_user, tracker, settings.ATTACK_ENGINE.lower()
    )

    if result["success"]:

        return TerminalExecuteResponse(
            output=result.get("output", ""),
            exit_code=0,
        )

    return TerminalExecuteResponse(
        output=result.get(
            "error",
            "Command failed"
        ),
        exit_code=1,
    )

@router.get("/prompt")
def get_prompt(current_user: User = Depends(get_current_user)):

    return {
        "prompt": "j.smith@WEB-SERVER:~$"
    }

@router.get("/investigation/{session_id}")
def get_investigation(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if SessionService.get_session_for_user(db, session_id, current_user) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    tracker = investigation_tracker.get_session(
        session_id
    )

    if tracker is None:
        return {
            "error": "Investigation session not found"
        }

    return tracker.summary()

@router.get("/state/{session_id}")
def get_simulation_state(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if SessionService.get_session_for_user(db, session_id, current_user) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    state = SimulationSessionManager.get_session(
        session_id
    )

    if state is None:
        return {
            "error": "Simulation session not found"
        }

    return state.summary()
