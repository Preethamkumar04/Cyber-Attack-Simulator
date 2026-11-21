"""Shared implementation for isolated scenario-generation experiments.

This module deliberately does not import API routes, open a SQLAlchemy session,
or call Docker.  It reproduces the current Ollama request contract in order to
observe information that the production client intentionally does not expose.
"""

from __future__ import annotations

import csv
import json
import secrets
import statistics
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import requests

# Allow both `python experiments/...` from backend and module execution.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.schemas.scenario_schema import ScenarioSchema
from app.services.ai_generator.ollama_client import OllamaClient
from app.services.ai_generator.scenario_builder import ScenarioBuilder
from app.services.docker.mock_attack_engine import MockAttackEngine
from app.services.simulator.simulation_session_manager import SimulationSessionManager


DIFFICULTIES = ("BEGINNER", "INTERMEDIATE", "ADVANCED")
ARTIFACT_NAMES = ("simulation_log", "traffic_log", "network_alerts", "command_history")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_safe(value: Any) -> Any:
    """Return a JSON-serializable representation without losing response fields."""
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False, default=json_safe)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row}) or ["no_rows"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def normalize_chain(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict) or not isinstance(payload.get("attack_chain"), list):
        return None
    return " | ".join(" ".join(str(step).lower().split()) for step in payload["attack_chain"])


def external_evaluate(payload: Any) -> dict[str, Any]:
    """Common evaluator used on raw platform-first-attempt and baseline output.

    It deliberately does not call ScenarioSchema or ScenarioBuilder.  The rules
    reflect the current prompt requirements, including its 3--6 step range.
    """
    errors: list[str] = []
    if not isinstance(payload, dict):
        return {"valid": False, "errors": ["JSON value is not an object"], "attack_chain_length": None}

    modes = {"active", "passive", "hybrid"}
    severity = {"Low", "Medium", "High", "Critical"}
    if not isinstance(payload.get("attack_mode"), str) or payload["attack_mode"].lower() not in modes:
        errors.append("attack_mode must be active, passive, or hybrid")
    chain = payload.get("attack_chain")
    if not isinstance(chain, list) or not 3 <= len(chain) <= 6 or not all(isinstance(x, str) and x.strip() for x in chain):
        errors.append("attack_chain must contain 3-6 non-empty strings")
    for field in ("hidden_objectives", "expected_findings", "expected_commands", "expected_mitigation"):
        value = payload.get(field)
        if not isinstance(value, list) or not value or not all(isinstance(x, str) and x.strip() for x in value):
            errors.append(f"{field} must be a non-empty string list")
    if not isinstance(payload.get("expected_root_cause"), str) or not payload["expected_root_cause"].strip():
        errors.append("expected_root_cause must be non-empty")
    if payload.get("expected_severity") not in severity:
        errors.append("expected_severity must be Low, Medium, High, or Critical")
    return {"valid": not errors, "errors": errors, "attack_chain_length": len(chain) if isinstance(chain, list) else None}


def _request_payload(client: OllamaClient, prompt: str) -> dict[str, Any]:
    """Exactly mirrors the production scenario request payload."""
    return {
        "model": client.model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.7, "top_p": 0.9},
    }


def _single_request(client: OllamaClient, prompt: str) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        response = requests.post(f"{client.base_url}/api/generate", json=_request_payload(client, prompt), timeout=120)
        response.raise_for_status()
        response_data = response.json()
        if not isinstance(response_data, dict):
            raise ValueError("Ollama response body is not a JSON object")
        return {
            "model_response_time_ms": round((time.perf_counter() - started) * 1000, 3),
            "http_ok": True,
            "raw_response": str(response_data.get("response", "")),
            "ollama_metadata": {key: json_safe(value) for key, value in response_data.items() if key != "response"},
            "request_error": None,
        }
    except (requests.RequestException, ValueError) as exc:
        return {
            "model_response_time_ms": round((time.perf_counter() - started) * 1000, 3),
            "http_ok": False,
            "raw_response": None,
            "ollama_metadata": {},
            "request_error": f"{type(exc).__name__}: {exc}",
        }


def capture_platform_run(run_id: str, difficulty: str) -> tuple[dict[str, Any], list[dict[str, Any]], ScenarioSchema | None, dict[str, Any] | None]:
    """Run the existing production prompt/retry contract with observable attempts."""
    started = time.perf_counter()
    client, builder = OllamaClient(), ScenarioBuilder()
    prompt = client._build_scenario_prompt(difficulty)
    attempts: list[dict[str, Any]] = []
    scenario: ScenarioSchema | None = None
    final_payload: dict[str, Any] | None = None
    final_failure: str | None = None
    retry_wait_ms = 0.0

    for attempt_number in range(1, client.MAX_RETRIES + 1):
        item = _single_request(client, prompt)
        item.update({"run_id": run_id, "attempt_number": attempt_number, "requested_difficulty": difficulty})
        parse_started = time.perf_counter()
        parsed: Any = None
        schema_ok = False
        failure_reason = item["request_error"]
        if item["http_ok"]:
            try:
                parsed = client._parse_json_safely(item["raw_response"] or "")
                if parsed is None:
                    raise ValueError("Failed to parse valid JSON from Ollama response")
                if not isinstance(parsed, dict):
                    raise ValueError("Parsed response is not a JSON object")
                parsed["difficulty"] = difficulty  # Production client behavior.
                scenario = ScenarioSchema(**parsed)
                final_payload = parsed
                schema_ok = True
            except (json.JSONDecodeError, ValueError) as exc:
                failure_reason = f"{type(exc).__name__}: {exc}"
        item["parse_and_schema_time_ms"] = round((time.perf_counter() - parse_started) * 1000, 3)
        item["parse_ok"] = parsed is not None
        item["schema_validation_ok"] = schema_ok
        item["failure_reason"] = failure_reason
        item["external_evaluation"] = external_evaluate(parsed)
        attempts.append(item)
        if schema_ok:
            break
        if attempt_number < client.MAX_RETRIES:
            wait_started = time.perf_counter()
            time.sleep(client.RETRY_DELAY * attempt_number)
            retry_wait_ms += (time.perf_counter() - wait_started) * 1000
    else:
        final_failure = attempts[-1]["failure_reason"] if attempts else "No attempts recorded"

    builder_validation_ms = 0.0
    builder_ok = False
    if scenario is not None:
        validation_started = time.perf_counter()
        try:
            scenario = builder.validate(scenario, difficulty)
            builder_ok = True
        except ValueError as exc:
            final_failure = f"{type(exc).__name__}: {exc}"
        builder_validation_ms = (time.perf_counter() - validation_started) * 1000

    first = attempts[0] if attempts else {}
    run = {
        "run_id": run_id,
        "requested_difficulty": difficulty,
        "requested_attack_mode": "model_selected",
        "scenario_uuid": scenario.scenario_id if scenario and builder_ok else None,
        "attack_mode": scenario.attack_mode if scenario and builder_ok else (final_payload or {}).get("attack_mode"),
        "attempt_count": len(attempts),
        "retry_count": max(0, len(attempts) - 1),
        "first_attempt_schema_valid": bool(first.get("schema_validation_ok")),
        "first_attempt_external_valid": bool(first.get("external_evaluation", {}).get("valid")),
        "final_structural_valid": builder_ok,
        "final_generation_failure": not builder_ok,
        "failure_reason": final_failure,
        "model_response_time_ms": round(sum(item["model_response_time_ms"] for item in attempts), 3),
        "parse_and_schema_time_ms": round(sum(item["parse_and_schema_time_ms"] for item in attempts), 3),
        "builder_validation_time_ms": round(builder_validation_ms, 3),
        "retry_wait_time_ms": round(retry_wait_ms, 3),
        "total_generation_time_ms": round((time.perf_counter() - started) * 1000, 3),
        "attack_chain_length": len(scenario.attack_chain) if scenario and builder_ok else None,
        "first_attempt_ollama_metadata": json.dumps(first.get("ollama_metadata", {}), ensure_ascii=False),
        "created_at": utc_now(),
    }
    return run, attempts, (scenario if builder_ok else None), final_payload


@contextmanager
def isolated_artifact_root(root: Path):
    """Temporarily redirect only the in-process simulation writers.

    Production source is untouched.  All modules are restored even when a
    simulation fails, so this cannot redirect a later application request.
    """
    from app.services.artifacts import artifact_manager
    from app.services.simulator import log_writer, network_writer, traffic_writer
    from app.services.terminal_generator import terminal_writer

    modules = (artifact_manager, log_writer, network_writer, traffic_writer, terminal_writer)
    previous = {module: module.BASE_DIR for module in modules}
    try:
        for module in modules:
            module.BASE_DIR = str(root)
        yield
    finally:
        for module, value in previous.items():
            module.BASE_DIR = value


def artifact_metrics(run_id: str, root: Path, session_id: int) -> list[dict[str, Any]]:
    from app.services.artifacts.artifact_manager import ArtifactManager

    with isolated_artifact_root(root):
        paths = ArtifactManager.get_artifact_paths(session_id)
    rows = []
    for artifact_name in ARTIFACT_NAMES:
        path = Path(paths[artifact_name])
        exists = path.is_file()
        line_count = 0
        if exists:
            with path.open("r", encoding="utf-8") as handle:
                line_count = sum(1 for line in handle if line.strip())
        rows.append({
            "run_id": run_id,
            "session_id": session_id,
            "artifact_type": artifact_name,
            "path": str(path),
            "exists": exists,
            "non_empty": line_count > 0,
            "line_count": line_count,
        })
    complete = all(row["exists"] and row["non_empty"] for row in rows)
    for row in rows:
        row["all_four_complete"] = complete
    return rows


def simulate_valid_scenario(run_id: str, scenario: ScenarioSchema, artifact_root: Path, session_id: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Use the existing mock engine; model-provided commands are never executed."""
    started = time.perf_counter()
    try:
        with isolated_artifact_root(artifact_root):
            result = MockAttackEngine().run_simulation(scenario.model_dump(), session_id)
        return ({"attempted": True, "success": True, "time_ms": round((time.perf_counter() - started) * 1000, 3), "result": result}, artifact_metrics(run_id, artifact_root, session_id))
    except Exception as exc:  # Retain failure instead of stopping later runs.
        # Emit four absent/partial artifact rows too; otherwise an engine
        # failure would incorrectly disappear from artifact-rate denominators.
        return ({"attempted": True, "success": False, "time_ms": round((time.perf_counter() - started) * 1000, 3), "error": f"{type(exc).__name__}: {exc}"}, artifact_metrics(run_id, artifact_root, session_id))
    finally:
        SimulationSessionManager.remove_session(session_id)


def unique_session_id(used: set[int]) -> int:
    while True:
        candidate = 1_000_000_000 + secrets.randbelow(900_000_000)
        if candidate not in used:
            used.add(candidate)
            return candidate


def add_duplicate_flags(rows: list[dict[str, Any]], payloads: dict[str, dict[str, Any] | None]) -> None:
    seen: set[str] = set()
    for row in rows:
        key = normalize_chain(payloads.get(row["run_id"])) if row["final_structural_valid"] else None
        row["normalized_attack_chain"] = key
        row["duplicate_chain"] = bool(key and key in seen)
        if key:
            seen.add(key)


def _rate(numerator: int, denominator: int) -> float | None:
    return round(100 * numerator / denominator, 3) if denominator else None


def _descriptive(values: Iterable[float]) -> dict[str, float | None]:
    items = list(values)
    if not items:
        return {"mean": None, "median": None, "stddev": None}
    return {
        "mean": round(statistics.mean(items), 3),
        "median": round(statistics.median(items), 3),
        "stddev": round(statistics.pstdev(items), 3),
    }


def summarize_platform(rows: list[dict[str, Any]], artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    valid = [row for row in rows if row["final_structural_valid"]]
    retry_recovered = [row for row in valid if row["retry_count"] > 0]
    subset_artifacts = [row for row in artifacts if row["run_id"] in {item["run_id"] for item in valid}]
    complete_runs = {row["run_id"] for row in subset_artifacts if row["all_four_complete"]}
    return {
        "requested_runs": total,
        "first_attempt_validity_rate_percent": _rate(sum(row["first_attempt_external_valid"] for row in rows), total),
        "final_structural_validity_rate_percent": _rate(len(valid), total),
        "retry_recovery_rate_percent": _rate(len(retry_recovered), total),
        "final_generation_failure_rate_percent": _rate(sum(row["final_generation_failure"] for row in rows), total),
        "mean_attempts_per_run": round(statistics.mean([row["attempt_count"] for row in rows]), 3) if rows else None,
        "generation_time_ms": _descriptive(row["total_generation_time_ms"] for row in rows),
        "mean_attack_chain_length": round(statistics.mean([row["attack_chain_length"] for row in valid]), 3) if valid else None,
        "duplicate_chain_rate_percent": _rate(sum(row["duplicate_chain"] for row in valid), len(valid)),
        "artifact_file_presence_rate_percent": _rate(sum(row["exists"] for row in subset_artifacts), len(subset_artifacts)),
        "non_empty_artifact_rate_percent": _rate(sum(row["non_empty"] for row in subset_artifacts), len(subset_artifacts)),
        "complete_artifact_rate_percent": _rate(len(complete_runs), len(valid)),
    }


def parse_baseline_response(raw_response: str | None) -> tuple[Any, str | None]:
    """Strict raw JSON only: no production parser/recovery behavior."""
    if raw_response is None:
        return None, "No model response"
    try:
        return json.loads(raw_response), None
    except json.JSONDecodeError as exc:
        return None, f"JSONDecodeError: {exc}"


def capture_baseline_run(run_id: str, difficulty: str) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any]]:
    """One direct LLM call with the same prompt/options and no retries/validation."""
    client = OllamaClient()
    prompt = client._build_scenario_prompt(difficulty)
    request = _single_request(client, prompt)
    payload, parse_error = parse_baseline_response(request["raw_response"])
    evaluation = external_evaluate(payload)
    row = {
        "run_id": run_id,
        "requested_difficulty": difficulty,
        "requested_attack_mode": "model_selected",
        "http_ok": request["http_ok"],
        "raw_json_parse_ok": parse_error is None,
        "external_valid": evaluation["valid"],
        "failure_reason": request["request_error"] or parse_error or "; ".join(evaluation["errors"]),
        "model_response_time_ms": request["model_response_time_ms"],
        "attack_chain_length": evaluation["attack_chain_length"],
        "ollama_metadata": json.dumps(request["ollama_metadata"], ensure_ascii=False),
        "created_at": utc_now(),
    }
    metadata = {"request": request, "external_evaluation": evaluation, "raw_payload": payload}
    return row, (payload if isinstance(payload, dict) else None), metadata

