# """
# MockAttackEngine — development-time simulation backend.

# Why this exists:
#   Wraps the existing SimulationRunner pipeline (event engine, log/traffic/
#   network generators, terminal history) behind AttackEngineInterface.
#   Used on machines without Docker until real container orchestration is wired.
# """

# from typing import Dict

# from app.services.docker.attack_engine_interface import AttackEngineInterface
# from app.services.simulator.simulation_runner import SimulationRunner


# class MockAttackEngine(AttackEngineInterface):

#     def run_simulation(self, scenario: Dict) -> Dict:
#         result = SimulationRunner.run(scenario)
#         return {
#             **result,
#             "engine": self.get_engine_type(),
#             "status": "completed",
#         }

#     def get_engine_type(self) -> str:
#         return "mock"
"""
MockAttackEngine — development-time simulation backend.

Why this exists:
Wraps the existing SimulationRunner pipeline behind AttackEngineInterface.
Used on machines without Docker until real container orchestration is wired.
"""

from typing import Dict

from app.services.docker.attack_engine_interface import AttackEngineInterface
from app.services.simulator.simulation_runner import SimulationRunner


class MockAttackEngine(AttackEngineInterface):

    def run_simulation(
        self,
        scenario: Dict,
        session_id: int,
        lab_key: str | None = None,
    ) -> Dict:

        result = SimulationRunner.run(
            scenario,
            session_id
        )

        return {
            **result,
            "engine": self.get_engine_type(),
            "status": "completed",
        }

    def get_engine_type(self) -> str:
        return "mock"
