from typing import Dict, Optional

from app.services.simulator.simulation_state import SimulationState


class SimulationRegistry:
    """
    Stores active SimulationState objects by training session ID.

    This is runtime-only state.
    It is intentionally not stored in the database.
    """

    _states: Dict[int, SimulationState] = {}

    @classmethod
    def store(
        cls,
        session_id: int,
        state: SimulationState
    ) -> None:
        cls._states[session_id] = state

    @classmethod
    def get(
        cls,
        session_id: int
    ) -> Optional[SimulationState]:
        return cls._states.get(session_id)

    @classmethod
    def remove(
        cls,
        session_id: int
    ) -> None:
        cls._states.pop(session_id, None)

    @classmethod
    def clear(cls) -> None:
        cls._states.clear()