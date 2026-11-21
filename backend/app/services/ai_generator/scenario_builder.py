import logging

from app.services.ai_generator.ollama_client import OllamaClient
from app.schemas.scenario_schema import ScenarioSchema

logger = logging.getLogger(__name__)


class ScenarioBuilder:

    def __init__(self):
        self.ollama = OllamaClient()

    def validate(
        self,
        scenario: ScenarioSchema,
        requested_difficulty: str
    ) -> ScenarioSchema:

        valid_modes = ["active", "passive", "hybrid"]

        if scenario.attack_mode.lower() not in valid_modes:
            raise ValueError(f"Invalid attack mode: {scenario.attack_mode}")

        if len(scenario.attack_chain) == 0:
            raise ValueError("Attack chain cannot be empty")

        if len(scenario.attack_chain) > 8:
            raise ValueError("Attack chain too long (max 8 steps)")

        if len(scenario.hidden_objectives) == 0:
            raise ValueError("Hidden objectives missing")

        if scenario.difficulty.lower() != requested_difficulty.lower():
            logger.warning(f"Difficulty mismatch: got {scenario.difficulty}, expected {requested_difficulty}")
            scenario.difficulty = requested_difficulty

        valid_severities = ["Low", "Medium", "High", "Critical"]
        if scenario.expected_severity not in valid_severities:
            logger.warning(f"Invalid severity: {scenario.expected_severity}, defaulting to Medium")
            scenario.expected_severity = "Medium"

        if not scenario.expected_root_cause:
            raise ValueError("Expected root cause is required")

        if len(scenario.expected_findings) == 0:
            raise ValueError("Expected findings cannot be empty")

        if len(scenario.expected_commands) == 0:
            raise ValueError("Expected commands cannot be empty")

        scenario.simulation_ready = True
        return scenario

    def generate(self, difficulty: str) -> ScenarioSchema:
        generated_scenario = self.ollama.generate_scenario(difficulty)
        validated_scenario = self.validate(generated_scenario, difficulty)
        logger.info(f"Scenario generated and validated for difficulty={difficulty}")
        return validated_scenario

    def get_visible_scenario(self, scenario: ScenarioSchema) -> dict:
        """Return only the visible parts of the scenario for the frontend."""
        return {
            "scenario_id": scenario.scenario_id,
            "difficulty": scenario.difficulty,
            "attack_chain": scenario.attack_chain,
            "attack_mode": scenario.attack_mode,
            "available_artifacts": [
                "system_logs",
                "network_alerts",
                "traffic",
                "command_history"
            ],
        }

    def get_hidden_objectives(self, scenario: ScenarioSchema) -> dict:
        """Return hidden objectives for evaluation (not exposed to frontend before submission)."""
        return {
            "hidden_objectives": scenario.hidden_objectives,
            "expected_findings": scenario.expected_findings,
            "expected_commands": scenario.expected_commands,
            "expected_root_cause": scenario.expected_root_cause,
            "expected_severity": scenario.expected_severity,
            "expected_mitigation": scenario.expected_mitigation,
        }