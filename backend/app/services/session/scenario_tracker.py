from typing import Dict

from app.schemas.scenario_schema import ScenarioSchema


class ScenarioTracker:
    """
    Stores generated scenarios for active training sessions.
    """

    def __init__(self):
        self.scenarios: Dict[int, ScenarioSchema] = {}

    def save_scenario(
        self,
        session_id: int,
        scenario: ScenarioSchema
    ):
        self.scenarios[session_id] = scenario

    def get_scenario(
        self,
        session_id: int
    ):
        return self.scenarios.get(session_id)

    def has_scenario(
        self,
        session_id: int
    ):
        return session_id in self.scenarios

    def delete_scenario(
        self,
        session_id: int
    ):
        self.scenarios.pop(session_id, None)


scenario_tracker = ScenarioTracker()