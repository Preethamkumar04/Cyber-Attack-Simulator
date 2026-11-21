"""Docker-backed, session-isolated training simulation engine."""

from typing import Dict

from app.services.docker.attack_engine_interface import AttackEngineInterface
from app.services.docker.lab_manager import DockerLabManager
from app.services.simulator.simulation_runner import SimulationRunner


class DockerAttackEngine(AttackEngineInterface):

    def __init__(self) -> None:
        self.lab_manager = DockerLabManager()

    def run_simulation(self, scenario: Dict, session_id: int, lab_key: str | None = None) -> Dict:
        # Preserve the existing investigation state and artifact format, then
        # append observations collected from the isolated real containers.
        baseline = SimulationRunner.run(scenario, session_id)
        lab = self.lab_manager.create_lab(session_id, lab_key)
        docker_result = self.lab_manager.run_safe_sequence(session_id, scenario, lab_key)
        return {**baseline, "engine": self.get_engine_type(), "lab": lab, "docker": docker_result}

    def get_engine_type(self) -> str:
        return "docker"
