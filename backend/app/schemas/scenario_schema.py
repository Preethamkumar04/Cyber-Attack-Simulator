from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from uuid import uuid4


class ScenarioSchema(BaseModel):
    scenario_id: str = Field(default_factory=lambda: str(uuid4()))
    attack_mode: str
    difficulty: str
    attack_chain: List[str]
    hidden_objectives: List[str]

    expected_findings: List[str] = Field(default_factory=list)
    expected_commands: List[str] = Field(default_factory=list)
    expected_root_cause: str = ""
    expected_severity: str = ""
    expected_mitigation: List[str] = Field(default_factory=list)

    simulation_ready: bool = False

    @field_validator("attack_chain")
    @classmethod
    def validate_attack_chain(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Attack chain cannot be empty")
        if len(v) > 8:
            raise ValueError("Attack chain too long")
        return v

    @field_validator("hidden_objectives")
    @classmethod
    def validate_hidden_objectives(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Hidden objectives cannot be empty")
        return v

    @field_validator("expected_severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        valid = ["Low", "Medium", "High", "Critical"]
        if v not in valid:
            raise ValueError(f"Severity must be one of: {valid}")
        return v

    @field_validator("expected_root_cause")
    @classmethod
    def validate_root_cause(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Root cause cannot be empty")
        return v.strip()

    def to_visible_dict(self) -> dict:
        """Return only trainee-visible parts."""
        return {
            "scenario_id": self.scenario_id,
            "difficulty": self.difficulty,
            "attack_mode": self.attack_mode,
            "attack_chain": self.attack_chain,
            "available_artifacts": [
                "system_logs",
                "network_alerts",
                "traffic",
                "command_history"
            ],
        }

    def to_hidden_dict(self) -> dict:
        """Return hidden parts for evaluation only."""
        return {
            "hidden_objectives": self.hidden_objectives,
            "expected_findings": self.expected_findings,
            "expected_commands": self.expected_commands,
            "expected_root_cause": self.expected_root_cause,
            "expected_severity": self.expected_severity,
            "expected_mitigation": self.expected_mitigation,
        }