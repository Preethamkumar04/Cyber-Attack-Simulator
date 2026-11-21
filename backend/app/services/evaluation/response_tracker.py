from typing import Dict

from app.schemas.evaluation_schema import AnalystResponse


class ResponseTracker:
    """
    Stores analyst responses for active training sessions.
    """

    def __init__(self):
        self.responses: Dict[int, AnalystResponse] = {}

    def save_response(self, response: AnalystResponse):
        self.responses[response.session_id] = response

    def get_response(self, session_id: int):
        return self.responses.get(session_id)

    def has_response(self, session_id: int):
        return session_id in self.responses

    def delete_response(self, session_id: int):
        self.responses.pop(session_id, None)


response_tracker = ResponseTracker()