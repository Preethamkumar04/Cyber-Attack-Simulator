"""
FeedbackGenerator — produces narrative AI coaching after evaluation.

Why this exists:
  ScoringEngine returns numeric breakdowns; this service uses Ollama to generate
  human-readable feedback for trainees, preserving the existing FastAPI + Ollama
  architecture without modifying scoring logic.
"""

import json
from typing import Any, Dict

import requests

from app.core.config import settings
from app.schemas.evaluation_schema import AnalystResponse, EvaluationResult


class FeedbackGenerator:

    @staticmethod
    def _build_prompt(
        evaluation: EvaluationResult,
        expected: Dict[str, Any],
        response: AnalystResponse,
    ) -> str:
        return f"""
You are a senior SOC mentor reviewing a cyber attack simulation exercise.

Provide constructive, professional feedback for the trainee.

Evaluation summary:

- Total score: {evaluation.score}/100
- Findings score: {evaluation.findings_score}/35
- Commands score: {evaluation.commands_score}/25
- Severity score: {evaluation.severity_score}/15
- Root cause score: {evaluation.root_cause_score}/15
- Mitigation score: {evaluation.mitigation_score}/10

Matched findings: {evaluation.matched_findings}
Missed findings: {evaluation.missed_findings}

Matched commands: {evaluation.matched_commands}
Missed commands: {evaluation.missed_commands}

Matched mitigation: {evaluation.matched_mitigation}
Missed mitigation: {evaluation.missed_mitigation}

Trainee severity: {response.severity}
Expected severity: {expected.get('severity', '')}
Severity score awarded: {evaluation.severity_score}/15


Trainee root cause: {response.root_cause}
Expected root cause: {expected.get('root_cause', '')}
Root cause score awarded: {evaluation.root_cause_score}/15

STRICT SCORE INTERPRETATION:

Severity:
- Awarded score = {evaluation.severity_score}/15.
- If the awarded score is 0, the trainee's severity MUST be described as incorrect or not matching the expected severity.
- If the awarded score is 15, the trainee's severity MUST be described as correct.
- Never describe the severity as correct when the awarded score is 0.

Root cause:
- Awarded score = {evaluation.root_cause_score}/15.
- If the awarded score is 0, the trainee's root cause MUST be described as incorrect or not matching the expected root cause.
- If the awarded score is 15, the trainee's root cause MUST be described as correct.
- Never describe the root cause as correct when the awarded score is 0.


IMPORTANT GROUNDING RULES:

Use ONLY the evaluation information explicitly provided above.

Do NOT invent or assume:
- attack techniques
- malware
- RATs
- phishing attachments
- vulnerabilities
- unauthorized processes
- network connections
- attacker actions
- indicators of compromise
- attack stages
- tools or commands not listed above

Do NOT introduce any finding that is not explicitly present in:
- matched findings
- missed findings
- matched commands
- missed commands
- matched mitigation
- missed mitigation
- trainee severity
- expected severity
- trainee root cause
- expected root cause

The numerical evaluation scores are authoritative.

Never claim that the trainee correctly answered something when its corresponding score is 0.

- If severity_score is 0, state that the trainee's severity did not match the expected severity.
- If root_cause_score is 0, state that the trainee's root cause did not match the expected root cause.
- Use matched_findings and missed_findings as the authoritative source for findings.
- Use matched_commands and missed_commands as the authoritative source for commands.
- Use matched_mitigation and missed_mitigation as the authoritative source for mitigation.
- Do not infer that an answer was correct merely because it sounds reasonable.
- Do not contradict the numerical scores.
- Do not invent findings, commands, root causes, severity levels, or mitigation actions that are not present in the evaluation data.

Recommended investigation steps MUST be derived directly from the
missed findings and missed commands.

Do NOT create new investigation commands unless they are already listed
in the missed commands.

Do NOT claim that the trainee discovered something unless it appears in
the matched findings.

Do NOT claim that the trainee missed something unless it appears in
the missed findings, missed commands, or missed mitigation.

Do not explain WHY a finding occurred or what attack technique it represents
unless that information is explicitly present in the evaluation data.

For example, do not transform "multiple failed login attempts" into
"brute-force attack" unless "brute-force" appears in the provided evaluation.

Do not claim that a mitigation would have prevented, caused, or reduced
an attack unless that relationship is explicitly provided in the evaluation.

Describe evaluation items using their provided meaning without adding
causal explanations or cybersecurity interpretations.
D
If information is unavailable, explicitly state that it was not identified
in the trainee response or evaluation.

The feedback must accurately reflect the numerical scores.


Write 5 short sections:

1. Overall Performance Assessment
   Explain the overall score and summarize the trainee's performance.

2. What the Analyst Did Well
   Discuss only matched findings, matched commands, matched mitigation,
   and correctly assessed severity/root cause where applicable.

3. Critical Gaps or Missed Indicators
   Discuss only the explicitly listed missed findings, missed commands,
   missed mitigation, and root cause gaps.

4. Recommended Next Investigation Steps
   Recommend actions based ONLY on the missed findings and missed commands.
   Do not introduce new commands or indicators.

5. One Concrete Improvement Tip
   Give one practical improvement directly related to the trainee's
   missed items.

Use clear, encouraging language suitable for an M.Tech cybersecurity
training platform.

Return plain text only, no markdown fences.
""".strip()

    @classmethod
    def generate(
        cls,
        evaluation: EvaluationResult,
        expected: Dict[str, Any],
        response: AnalystResponse,
    ) -> str:
        prompt = cls._build_prompt(evaluation, expected, response)

        try:
            api_response = requests.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120,
            )
            api_response.raise_for_status()
            return api_response.json()["response"].strip()
        except (requests.RequestException, KeyError, json.JSONDecodeError):
            return cls._fallback_feedback(evaluation)

    @staticmethod
    def _fallback_feedback(evaluation: EvaluationResult) -> str:
        if evaluation.score >= 80:
            level = "Strong performance"
        elif evaluation.score >= 60:
            level = "Solid effort with room to improve"
        else:
            level = "Needs further practice"

        feedback_parts = [
            f"{level}. You scored {evaluation.score}/100."
        ]

        if evaluation.matched_findings:
            feedback_parts.append(
                f"You correctly identified {len(evaluation.matched_findings)} "
                f"expected finding(s)."
            )

        if evaluation.missed_findings:
            feedback_parts.append(
                f"You missed {len(evaluation.missed_findings)} expected finding(s)."
            )

        if evaluation.matched_commands:
            feedback_parts.append(
                f"You correctly used {len(evaluation.matched_commands)} "
                f"expected investigation command(s)."
            )

        if evaluation.missed_commands:
            feedback_parts.append(
                f"{len(evaluation.missed_commands)} expected investigation "
                f"command(s) were not identified."
            )

        if evaluation.matched_mitigation:
            feedback_parts.append(
                f"You identified {len(evaluation.matched_mitigation)} "
                f"expected mitigation action(s)."
            )

        if evaluation.missed_mitigation:
            feedback_parts.append(
                f"{len(evaluation.missed_mitigation)} expected mitigation "
                f"action(s) were missed."
            )

        if evaluation.severity_score == 0:
            feedback_parts.append(
                "The submitted severity did not match the expected severity."
            )

        if evaluation.root_cause_score == 0:
            feedback_parts.append(
                "The submitted root cause did not match the expected root cause."
            )

        return "\n\n".join(feedback_parts)