# from typing import Dict

# from app.services.simulator.event_engine import EventEngine

# from app.services.simulator.simulation_state import (
#     SimulationState
# )

# from app.services.simulator.log_generator import (
#     LogGenerator
# )
# from app.services.simulator.log_writer import (
#     LogWriter
# )

# from app.services.simulator.traffic_generator import (
#     TrafficGenerator
# )
# from app.services.simulator.traffic_writer import (
#     TrafficWriter
# )

# from app.services.simulator.network_generator import (
#     NetworkGenerator
# )
# from app.services.simulator.network_writer import (
#     NetworkWriter
# )

# from app.services.terminal_generator.terminal_generator import (
#     TerminalGenerator
# )
# from app.services.terminal_generator.terminal_writer import (
#     TerminalWriter
# )


# class SimulationRunner:
#     """
#     Orchestrates the complete simulation pipeline.
#     """

#     @staticmethod
#     def run(
#         scenario: Dict
#     ) -> Dict:

#         state = SimulationState()

#         timeline = EventEngine.generate_timeline(
#             scenario,
#             state
#         )

#         logs = LogGenerator.generate_logs(
#             timeline,
#             state
#         )

#         traffic = TrafficGenerator.generate_traffic(
#             timeline,
#             state
#         )

#         alerts = NetworkGenerator.generate_alerts(
#             timeline,
#             state
#         )

#         history = TerminalGenerator.generate_history(
#             timeline,
#             state
#         )

#         LogWriter.write_logs(logs)

#         TrafficWriter.write_traffic(
#             traffic
#         )

#         NetworkWriter.write_alerts(
#             alerts
#         )

#         TerminalWriter.write_history(
#             history
#         )

#         return {
#             "timeline_events": len(timeline),
#             "logs_generated": len(logs),
#             "traffic_records": len(traffic),
#             "alerts_generated": len(alerts),
#             "commands_generated": len(history),
#             "state": state,
#         }

from typing import Dict
import inspect

from app.services.simulator.event_engine import EventEngine
from app.services.simulator.simulation_state import SimulationState
from app.services.simulator.simulation_session_manager import (
    SimulationSessionManager
)

from app.services.simulator.log_generator import LogGenerator
from app.services.simulator.log_writer import LogWriter

from app.services.simulator.traffic_generator import TrafficGenerator
from app.services.simulator.traffic_writer import TrafficWriter

from app.services.simulator.network_generator import NetworkGenerator
from app.services.simulator.network_writer import NetworkWriter

from app.services.terminal_generator.terminal_generator import (
    TerminalGenerator
)
from app.services.terminal_generator.terminal_writer import (
    TerminalWriter
)


class SimulationRunner:
    """
    Orchestrates the complete simulation pipeline.
    """

    @staticmethod
    def run(
        scenario: Dict,
        session_id: int
    ) -> Dict:

        # ---------------------------------------------------------
        # Create and register the simulation state
        # ---------------------------------------------------------

        state = SimulationSessionManager.create_session(
            session_id
        )

        # ---------------------------------------------------------
        # Generate attack timeline and apply events
        # ---------------------------------------------------------

        timeline = EventEngine.generate_timeline(
            scenario,
            state
        )

        # ---------------------------------------------------------
        # Generate investigation artifacts
        # ---------------------------------------------------------

        logs = LogGenerator.generate_logs(
            timeline,
            state
        )

        traffic = TrafficGenerator.generate_traffic(
            timeline,
            state
        )

        alerts = NetworkGenerator.generate_alerts(
            timeline,
            state
        )

        history = TerminalGenerator.generate_history(
            timeline,
            state
        )

        # ---------------------------------------------------------
        # Write artifacts
        # ---------------------------------------------------------

        LogWriter.write_logs(
            logs,
            session_id
        )

        TrafficWriter.write_traffic(
            traffic,
            session_id
        )

        NetworkWriter.write_alerts(
            alerts,
            session_id
        )

        TerminalWriter.write_history(
            history,
            session_id
        )

        # ---------------------------------------------------------
        # Return simulation summary
        # ---------------------------------------------------------

        return {
            "timeline_events": len(timeline),
            "logs_generated": len(logs),
            "traffic_records": len(traffic),
            "alerts_generated": len(alerts),
            "commands_generated": len(history),
            # "state": state,
        }