# """
# WebSocket routes — real-time log streaming
# for a specific simulation session.
# """

# import asyncio

# from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# from app.services.streaming.log_stream_service import (
#     LOG_KEY_MAP,
#     log_stream_manager,
# )


# router = APIRouter()


# @router.websocket(
#     "/logs/{session_id}/{log_type}"
# )
# async def stream_logs(
#     websocket: WebSocket,
#     session_id: int,
#     log_type: str
# ):

#     if log_type not in LOG_KEY_MAP:

#         await websocket.close(
#             code=1008
#         )

#         return

#     await log_stream_manager.connect(
#         session_id,
#         log_type,
#         websocket
#     )

#     stream_task = asyncio.create_task(
#         log_stream_manager.stream_loop(
#             session_id,
#             log_type,
#             websocket
#         )
#     )

#     try:

#         while True:

#             await websocket.receive_text()

#     except WebSocketDisconnect:

#         pass

#     finally:

#         stream_task.cancel()

#         log_stream_manager.disconnect(
#             session_id,
#             log_type,
#             websocket
#         )

"""
WebSocket routes — real-time log streaming to connected clients.
"""

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import decode_access_token
from app.database.connection import SessionLocal
from app.database.models.training_session import TrainingSession
from app.database.models.user import User

from app.services.streaming.log_stream_service import (
    LOG_KEY_MAP,
    log_stream_manager,
)
from app.services.investigation.investigation_tracker import investigation_tracker

router = APIRouter()


@router.websocket("/logs/{session_id}/{log_type}")
async def stream_logs(
    websocket: WebSocket,
    session_id: int,
    log_type: str,
):

    if log_type not in LOG_KEY_MAP:
        await websocket.close(code=1008)
        return

    token = websocket.query_params.get("token")
    payload = decode_access_token(token) if token else None
    user_id = payload.get("sub") if payload else None
    if user_id is None:
        await websocket.close(code=1008)
        return

    try:
        authenticated_user_id = int(user_id)
    except (TypeError, ValueError):
        await websocket.close(code=1008)
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == authenticated_user_id).first()
        training_session = None
        if user is not None and user.is_active:
            training_session = (
                db.query(TrainingSession)
                .filter(
                    TrainingSession.id == session_id,
                    TrainingSession.tenant_id == user.tenant_id,
                )
                .first()
            )
    finally:
        db.close()

    if user is None or not user.is_active or training_session is None:
        await websocket.close(code=1008)
        return

    investigation_tracker.get_or_create_session(session_id).record_artifact_inspected(log_type)

    initial_offset = await log_stream_manager.connect(
        session_id,
        log_type,
        websocket,
    )

    stream_task = asyncio.create_task(
        log_stream_manager.stream_loop(
            session_id,
            log_type,
            websocket,
            initial_offset,
        )
    )

    try:

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        pass

    finally:

        stream_task.cancel()
        try:
            await stream_task
        except asyncio.CancelledError:
            pass

        log_stream_manager.disconnect(
            session_id,
            log_type,
            websocket,
        )
