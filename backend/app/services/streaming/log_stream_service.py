
# """
# LogStreamService — real-time log tailing for WebSocket clients.

# Tails session-specific artifact files and streams new lines
# to connected WebSocket subscribers.
# """

# import asyncio
# import os
# from typing import Dict, List, Set

# from fastapi import WebSocket

# from app.services.artifacts.artifact_manager import ArtifactManager


# LOG_KEY_MAP = {
#     "simulation": "simulation_log",
#     "network": "network_alerts",
#     "traffic": "traffic_log",
#     "commands": "command_history",
# }


# class LogStreamManager:

#     def __init__(self):
#         self.connections: Dict[str, Set[WebSocket]] = {}

#     def _resolve_path(
#         self,
#         session_id: int,
#         log_type: str
#     ) -> str:

#         paths = ArtifactManager.get_artifact_paths(
#             session_id
#         )

#         path_key = LOG_KEY_MAP.get(log_type)

#         if not path_key:
#             raise ValueError(
#                 f"Invalid log type: {log_type}"
#             )

#         return paths[path_key]

#     async def connect(
#         self,
#         session_id: int,
#         log_type: str,
#         websocket: WebSocket
#     ):

#         await websocket.accept()

#         connection_key = (
#             f"{session_id}:{log_type}"
#         )

#         self.connections.setdefault(
#             connection_key,
#             set()
#         ).add(websocket)

#         path = self._resolve_path(
#             session_id,
#             log_type
#         )

#         initial_lines = self._read_lines(
#             path
#         )

#         await websocket.send_json(
#             {
#                 "type": "snapshot",
#                 "session_id": session_id,
#                 "log_type": log_type,
#                 "lines": initial_lines,
#                 "line_count": len(initial_lines),
#             }
#         )

#     def disconnect(
#         self,
#         session_id: int,
#         log_type: str,
#         websocket: WebSocket
#     ):

#         connection_key = (
#             f"{session_id}:{log_type}"
#         )

#         if connection_key in self.connections:

#             self.connections[
#                 connection_key
#             ].discard(websocket)

#     @staticmethod
#     def _read_lines(
#         path: str
#     ) -> List[str]:

#         if not os.path.exists(path):
#             return []

#         with open(
#             path,
#             "r",
#             encoding="utf-8"
#         ) as handle:

#             return [
#                 line
#                 for line in handle.read().splitlines()
#                 if line.strip()
#             ]

#     async def stream_loop(
#         self,
#         session_id: int,
#         log_type: str,
#         websocket: WebSocket
#     ):

#         path = self._resolve_path(
#             session_id,
#             log_type
#         )

#         last_size = (
#             os.path.getsize(path)
#             if os.path.exists(path)
#             else 0
#         )

#         try:

#             while True:

#                 await asyncio.sleep(1)

#                 if not os.path.exists(path):
#                     continue

#                 current_size = os.path.getsize(
#                     path
#                 )

#                 if current_size > last_size:

#                     with open(
#                         path,
#                         "r",
#                         encoding="utf-8"
#                     ) as handle:

#                         handle.seek(last_size)
#                         chunk = handle.read()

#                     new_lines = [
#                         line
#                         for line in chunk.splitlines()
#                         if line.strip()
#                     ]

#                     if new_lines:

#                         await websocket.send_json(
#                             {
#                                 "type": "append",
#                                 "session_id": session_id,
#                                 "log_type": log_type,
#                                 "lines": new_lines,
#                             }
#                         )

#                     last_size = current_size

#                 elif current_size < last_size:

#                     lines = self._read_lines(
#                         path
#                     )

#                     await websocket.send_json(
#                         {
#                             "type": "snapshot",
#                             "session_id": session_id,
#                             "log_type": log_type,
#                             "lines": lines,
#                             "line_count": len(lines),
#                         }
#                     )

#                     last_size = current_size

#         except asyncio.CancelledError:
#             raise


# log_stream_manager = LogStreamManager()

"""
LogStreamService — real-time log tailing for WebSocket clients.

Tails session-specific artifact files and broadcasts
new lines to connected WebSocket subscribers.
"""

import asyncio
import os
from typing import Dict, List, Set

from fastapi import WebSocket

from app.services.artifacts.artifact_manager import ArtifactManager


LOG_KEY_MAP = {
    "simulation": "simulation_log",
    "network": "network_alerts",
    "traffic": "traffic_log",
    "commands": "command_history",
}


class LogStreamManager:

    def __init__(self):

        self.connections: Dict[str, Set[WebSocket]] = {}

    @staticmethod
    def _connection_key(session_id: int, log_type: str) -> str:
        return f"{session_id}:{log_type}"

    def _resolve_path(
        self,
        session_id: int,
        log_type: str,
    ) -> str:

        paths = ArtifactManager.get_artifact_paths(
            session_id
        )

        path_key = LOG_KEY_MAP.get(log_type)

        if not path_key:
            raise ValueError(
                f"Invalid log type: {log_type}"
            )

        return paths[path_key]

    async def connect(
        self,
        session_id: int,
        log_type: str,
        websocket: WebSocket,
    ) -> int:

        await websocket.accept()

        self.connections.setdefault(
            self._connection_key(session_id, log_type), set()
        ).add(websocket)

        path = self._resolve_path(
            session_id,
            log_type,
        )

        initial_lines, offset = self._read_snapshot(path)

        await websocket.send_json(
            {
                "type": "snapshot",
                "session_id": session_id,
                "log_type": log_type,
                "lines": initial_lines,
                "line_count": len(initial_lines),
            }
        )
        return offset

    def disconnect(
        self,
        session_id: int,
        log_type: str,
        websocket: WebSocket,
    ):

        connection_key = self._connection_key(session_id, log_type)
        connections = self.connections.get(connection_key)
        if connections is not None:
            connections.discard(websocket)
            if not connections:
                self.connections.pop(connection_key, None)

    @staticmethod
    def _read_lines(
        path: str,
    ) -> List[str]:

        if not os.path.exists(path):
            return []

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as handle:

            return [
                line
                for line in handle.read().splitlines()
                if line.strip()
            ]

    @staticmethod
    def _read_snapshot(path: str) -> tuple[List[str], int]:
        """Return the exact snapshot and its byte offset for tailing."""
        if not os.path.exists(path):
            return [], 0

        with open(path, "rb") as handle:
            content = handle.read()

        return (
            [
                line
                for line in content.decode("utf-8", errors="replace").splitlines()
                if line.strip()
            ],
            len(content),
        )

    async def stream_loop(
        self,
        session_id: int,
        log_type: str,
        websocket: WebSocket,
        initial_offset: int,
    ):

        path = self._resolve_path(
            session_id,
            log_type,
        )

        last_size = initial_offset

        try:

            while True:

                await asyncio.sleep(1)

                if not os.path.exists(path):
                    continue

                current_size = os.path.getsize(path)

                if current_size > last_size:

                    with open(path, "rb") as handle:

                        handle.seek(last_size)

                        chunk = handle.read().decode("utf-8", errors="replace")

                    new_lines = [
                        line
                        for line in chunk.splitlines()
                        if line.strip()
                    ]

                    if new_lines:

                        await websocket.send_json(
                            {
                                "type": "append",
                                "session_id": session_id,
                                "log_type": log_type,
                                "lines": new_lines,
                            }
                        )

                    last_size = current_size

                elif current_size < last_size:

                    lines = self._read_lines(path)

                    await websocket.send_json(
                        {
                            "type": "snapshot",
                            "session_id": session_id,
                            "log_type": log_type,
                            "lines": lines,
                            "line_count": len(lines),
                        }
                    )

                    last_size = current_size

        except asyncio.CancelledError:
            raise


log_stream_manager = LogStreamManager()
