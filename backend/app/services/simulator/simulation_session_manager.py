from typing import Dict, Optional

from app.services.simulator.simulation_state import SimulationState
from app.services.investigation.investigation_tracker import (
    investigation_tracker
)

class SimulationSessionManager:
    """
    Manages SimulationState instances for active training sessions.

    Each training session receives its own isolated simulated environment.

    This state exists only in memory and never interacts with the
    real host filesystem or operating system.
    """

    _states: Dict[int, SimulationState] = {}

    @classmethod
    def create_session(
        cls,
        session_id: int
    ) -> SimulationState:
        """
        Create a fresh simulation state for a training session.
        """

        state = SimulationState()

        cls._states[session_id] = state

        return state

    @classmethod
    def get_session(
        cls,
        session_id: int
    ) -> Optional[SimulationState]:
        """
        Retrieve the simulation state for a training session.
        """

        return cls._states.get(session_id)

    @classmethod
    def get_or_create_session(
        cls,
        session_id: int
    ) -> SimulationState:
        """
        Retrieve an existing state or create one if it does not exist.
        """

        state = cls.get_session(session_id)

        if state is not None:
            return state

        return cls.create_session(session_id)

    @classmethod
    def remove_session(
        cls,
        session_id: int
    ) -> None:
        """
        Remove a simulation state from memory.
        """

        cls._states.pop(session_id, None)

        investigation_tracker.remove_session(
            session_id
        )

    @classmethod
    def clear_all(cls) -> None:
        """
        Clear all active simulation states.
        """

        cls._states.clear()