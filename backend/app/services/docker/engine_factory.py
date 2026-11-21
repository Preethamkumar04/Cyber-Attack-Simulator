"""
EngineFactory — selects the active AttackEngine implementation.

Why this exists:
  Centralizes engine selection via configuration so deployment can switch
  from mock to Docker by changing ATTACK_ENGINE in .env only.
"""

import os

from app.services.docker.attack_engine_interface import AttackEngineInterface
from app.services.docker.docker_attack_engine import DockerAttackEngine
from app.services.docker.mock_attack_engine import MockAttackEngine


def get_attack_engine() -> AttackEngineInterface:
    engine_type = os.getenv("ATTACK_ENGINE", "mock").lower()

    if engine_type == "docker":
        return DockerAttackEngine()

    return MockAttackEngine()
