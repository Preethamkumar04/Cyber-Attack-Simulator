"""
AttackEngineInterface — abstract contract for simulation execution backends.

Why this exists:
  Decouples scenario orchestration from the runtime that produces artifacts
  (logs, traffic, terminal history). The UI and API routes depend on this
  interface only. Swap MockAttackEngine for DockerAttackEngine later without
  touching routes or the React frontend.
"""

from abc import ABC, abstractmethod
from typing import Dict


class AttackEngineInterface(ABC):

    @abstractmethod
    def run_simulation(self, scenario: Dict, session_id: int, lab_key: str | None = None) -> Dict:
        """
        Execute an attack simulation for the given scenario dict.
        session_id identifies the training session whose
        SimulationState should be used.
        Returns a summary dict (event counts, status, etc.).
        """
        raise NotImplementedError

    @abstractmethod
    def get_engine_type(self) -> str:
        """Return engine identifier, e.g. 'mock' or 'docker'."""
        raise NotImplementedError
