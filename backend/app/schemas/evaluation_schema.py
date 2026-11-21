from typing import List
from pydantic import BaseModel, Field


class AnalystResponse(BaseModel):
    session_id: int
    findings: List[str]
    commands: List[str]
    severity: str
    root_cause: str
    mitigation: List[str]


class EvaluationResult(BaseModel):
    session_id: int

    score: float

    findings_score: float
    commands_score: float
    severity_score: float
    root_cause_score: float
    mitigation_score: float

    matched_findings: List[str] = Field(default_factory=list)
    missed_findings: List[str] = Field(default_factory=list)

    matched_commands: List[str] = Field(default_factory=list)
    missed_commands: List[str] = Field(default_factory=list)

    matched_mitigation: List[str] = Field(default_factory=list)
    missed_mitigation: List[str] = Field(default_factory=list)

    feedback: str = ""


class EvaluationRequest(BaseModel):
    session_id: int