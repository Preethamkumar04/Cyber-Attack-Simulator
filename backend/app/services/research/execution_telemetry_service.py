"""Execution-grounded validation using only the existing bounded Docker lab."""

import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models.research import AttackExecutionRecord, TelemetryValidationRecord
from app.services.artifacts.artifact_manager import ArtifactManager
from app.services.simulator.scenario_mapper import ScenarioMapper


SAFE_ACTIONS = {
    "reconnaissance": ("web_health_check", "GET http://target:8080/health", ["WEB_ACCESS"]),
    "credential_access": ("internal_auth_check", "GET http://service:8080/authenticate?user=training-analyst", ["AUTH_EVENT"]),
    "data_exfiltration": ("report_export_check", "GET http://target:8080/reports/export?dataset=training", ["WEB_ACCESS"]),
}


class ExecutionTelemetryService:
    @staticmethod
    def _artifact_lines(session_id: int):
        lines = []
        for source, path in ArtifactManager.get_artifact_paths(session_id).items():
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    lines.extend({"source": source, "line": line} for line in handle.read().splitlines() if line.strip())
            except FileNotFoundError:
                continue
        return lines

    @classmethod
    def validate_plan(cls, db: Session, session_id: int, scenario: dict, engine_type: str, lab_manager=None, lab_key=None):
        """Persist a result for every intended step; only allowlisted actions run."""
        events = ScenarioMapper.map_attack_chain(scenario.get("attack_chain", []))
        records = []
        for event in events:
            step_id = f"step-{event['step']}"
            technique = event["event_type"]
            safe_action = SAFE_ACTIONS.get(technique)
            intended = event["description"]
            executable = safe_action[1] if safe_action else None
            status, success, error, evidence = "NOT_EXECUTED", False, None, []

            if engine_type != "docker":
                error = "Mock engine produces simulated artifacts; no Docker action was executed."
            elif not safe_action:
                error = "No safe bounded Docker action is defined for this intended technique."
            else:
                try:
                    output = lab_manager.execute_validated_action(session_id, safe_action[0], lab_key)
                    success = True
                    status = "EXECUTED"
                    evidence = [{"action": safe_action[0], "output": output}]
                except Exception as exc:  # Records reality without changing lab safety policy.
                    status = "FAILED"
                    error = str(exc)

            record = AttackExecutionRecord(
                session_id=session_id, attack_step_id=step_id, technique=technique,
                intended_action=intended, executable_action=executable,
                execution_status=status, success=success, error=error,
                evidence_json=json.dumps(evidence),
            )
            db.add(record)
            records.append(record)
        db.flush()
        telemetry = cls._validate_telemetry(db, session_id, records)
        db.commit()
        return cls.summary(records, telemetry)

    @classmethod
    def _validate_telemetry(cls, db: Session, session_id: int, executions):
        all_lines = cls._artifact_lines(session_id)
        results = []
        for execution in executions:
            safe_action = SAFE_ACTIONS.get(execution.technique)
            expected = safe_action[2] if safe_action and execution.success else []
            observed = [item for item in all_lines if any(marker in item["line"] for marker in expected)]
            # Report other Docker service observations separately instead of
            # silently discarding them during the per-step comparison.
            unexpected = [
                item for item in all_lines
                if ("WEB_ACCESS" in item["line"] or "AUTH_EVENT" in item["line"])
                and not any(marker in item["line"] for marker in expected)
            ]
            matched = list(expected) if expected and all(any(marker in item["line"] for item in observed) for marker in expected) else []
            missing = [marker for marker in expected if marker not in matched]
            score = round(len(matched) / len(expected), 2) if expected else 0.0
            # The bounded request returned successfully but did not yield all
            # expected telemetry: retain the execution evidence and mark the
            # outcome honestly as partial rather than successful.
            if execution.success and missing:
                execution.execution_status = "PARTIALLY_EXECUTED"
            validation = TelemetryValidationRecord(
                session_id=session_id, attack_step_id=execution.attack_step_id,
                expected_events_json=json.dumps(expected), observed_events_json=json.dumps(observed),
                matched_events_json=json.dumps(matched), missing_events_json=json.dumps(missing),
                unexpected_events_json=json.dumps(unexpected), telemetry_fidelity_score=score,
            )
            db.add(validation)
            results.append(validation)
        db.flush()
        return results

    @staticmethod
    def summary(executions, telemetry):
        executable = [item for item in executions if item.executable_action]
        successful = [item for item in executable if item.success]
        return {
            "status_definitions": {
                "INTENDED": "Planned action awaiting execution.",
                "EXECUTED": "Allowlisted action completed and expected telemetry was observed.",
                "PARTIALLY_EXECUTED": "Action completed but one or more expected telemetry items were absent.",
                "FAILED": "Allowlisted action was attempted and returned an error.",
                "NOT_EXECUTED": "No safe bounded executable action exists, or the active engine is mock-only.",
            },
            "execution_fidelity_score": round(len(successful) / len(executable), 2) if executable else 0.0,
            "execution_records": [
                {"attack_step_id": item.attack_step_id, "technique": item.technique,
                 "intended_action": item.intended_action, "executable_action": item.executable_action,
                 "execution_status": item.execution_status, "success": item.success,
                 "error": item.error, "evidence": json.loads(item.evidence_json),
                 "timestamp": item.created_at.isoformat() if item.created_at else datetime.utcnow().isoformat()}
                for item in executions
            ],
            "telemetry_records": [
                {"attack_step_id": item.attack_step_id, "expected_events": json.loads(item.expected_events_json),
                 "observed_events": json.loads(item.observed_events_json), "matched_events": json.loads(item.matched_events_json),
                 "missing_expected_events": json.loads(item.missing_events_json),
                 "unexpected_events": json.loads(item.unexpected_events_json),
                 "telemetry_fidelity_score": item.telemetry_fidelity_score}
                for item in telemetry
            ],
        }
