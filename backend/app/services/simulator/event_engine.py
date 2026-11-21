from datetime import datetime, timedelta
from typing import Dict, List

from app.services.simulator.scenario_mapper import (
    ScenarioMapper,
)
from app.services.simulator.simulation_state import (
    SimulationState,
)

class EventEngine:
    """
    Builds a simulation timeline
    from a generated scenario.
    """

    @staticmethod
    def generate_timeline(
        scenario: Dict,
        state: SimulationState
    ) -> List[Dict]:
        """
        Scenario
            ↓
        Attack Chain
            ↓
        Mapped Events
            ↓
        Timeline
        """

        attack_chain = scenario.get(
            "attack_chain",
            []
        )

        mapped_events = (
            ScenarioMapper.map_attack_chain(
                attack_chain
            )
        )

        start_time = datetime.utcnow()

        timeline = []

        for index, event in enumerate(mapped_events):

            event_timestamp = (
                start_time +
                timedelta(minutes=index * 5)
            )

            timeline_event = {
                **event,
                "timestamp": event_timestamp.isoformat(),
            }

            state.apply_event(
                timeline_event
            )

            timeline.append(
                timeline_event
            )
        return timeline