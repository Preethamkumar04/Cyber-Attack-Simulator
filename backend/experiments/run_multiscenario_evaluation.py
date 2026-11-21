"""Run the approved 15-run platform and direct-LLM baseline experiment.

This script is intentionally not run by tests or application startup.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from uuid import uuid4

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from experiments.experiment_core import (
    DIFFICULTIES,
    add_duplicate_flags,
    capture_baseline_run,
    capture_platform_run,
    simulate_valid_scenario,
    summarize_platform,
    unique_session_id,
    utc_now,
    write_csv,
    write_json,
)


def make_output_dir(parent: Path) -> Path:
    label = f"experiment_{utc_now().replace(':', '').replace('+00:00', 'Z').replace('-', '')}_{uuid4().hex[:8]}"
    output = parent / label
    output.mkdir(parents=True, exist_ok=False)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Run isolated scenario-generation evaluation (no API, DB, or Docker).")
    parser.add_argument("--runs-per-difficulty", type=int, default=5, help="Default 5; approved experiment total is 15.")
    parser.add_argument("--output-parent", type=Path, default=BACKEND_DIR / "experiments" / "results")
    args = parser.parse_args()
    if args.runs_per_difficulty < 1:
        parser.error("--runs-per-difficulty must be at least 1")

    output = make_output_dir(args.output_parent.resolve())
    write_json(output / "experiment_manifest.json", {
        "created_at": utc_now(),
        "runs_per_difficulty": args.runs_per_difficulty,
        "difficulties": list(DIFFICULTIES),
        "total_platform_runs": args.runs_per_difficulty * len(DIFFICULTIES),
        "execution": "sequential",
        "engine": "MockAttackEngine only",
        "database_access": False,
        "docker_access": False,
        "notes": "No /scenario/start API calls are made. Experiment artifacts are redirected in-process to this output directory.",
    })

    platform_rows: list[dict] = []
    attempt_rows: list[dict] = []
    artifact_rows: list[dict] = []
    payloads: dict[str, dict | None] = {}
    used_session_ids: set[int] = set()

    run_number = 0
    for difficulty in DIFFICULTIES:
        for _ in range(args.runs_per_difficulty):
            run_number += 1
            run_id = f"platform_{run_number:03d}"
            run_dir = output / "platform_runs" / run_id
            run_dir.mkdir(parents=True, exist_ok=False)
            row, attempts, scenario, raw_payload = capture_platform_run(run_id, difficulty)
            payloads[run_id] = raw_payload
            # The parsed raw object is retained even when final builder
            # validation fails, so every run has inspectable scenario JSON.
            write_json(run_dir / "raw_scenario.json", raw_payload)
            for attempt in attempts:
                attempt["raw_response_path"] = str(run_dir / f"attempt_{attempt['attempt_number']:02d}_raw.txt")
                (run_dir / f"attempt_{attempt['attempt_number']:02d}_raw.txt").write_text(attempt["raw_response"] or "", encoding="utf-8")
            attempt_rows.extend(attempts)
            simulation = {"attempted": False, "reason": "Final structural validation failed"}
            if scenario is not None:
                write_json(run_dir / "scenario.json", scenario.model_dump())
                session_id = unique_session_id(used_session_ids)
                row["experiment_session_id"] = session_id
                simulation, measures = simulate_valid_scenario(run_id, scenario, run_dir / "artifact_root", session_id)
                artifact_rows.extend(measures)
            row["simulation_attempted"] = simulation["attempted"]
            row["simulation_success"] = simulation.get("success")
            row["simulation_time_ms"] = simulation.get("time_ms")
            row["simulation_error"] = simulation.get("error")
            write_json(run_dir / "metadata.json", {"run": row, "attempts": attempts, "raw_payload": raw_payload, "simulation": simulation})
            platform_rows.append(row)

    add_duplicate_flags(platform_rows, payloads)
    complete_by_run = {row["run_id"]: row["all_four_complete"] for row in artifact_rows if row["all_four_complete"]}
    for row in platform_rows:
        row["all_four_artifacts_complete"] = bool(complete_by_run.get(row["run_id"], False))

    baseline_rows: list[dict] = []
    baseline_payloads: dict[str, dict | None] = {}
    baseline_number = 0
    for difficulty in DIFFICULTIES:
        for _ in range(args.runs_per_difficulty):
            baseline_number += 1
            run_id = f"baseline_{baseline_number:03d}"
            run_dir = output / "baseline_runs" / run_id
            run_dir.mkdir(parents=True, exist_ok=False)
            row, payload, metadata = capture_baseline_run(run_id, difficulty)
            baseline_payloads[run_id] = payload
            (run_dir / "raw_response.txt").write_text(metadata["request"]["raw_response"] or "", encoding="utf-8")
            if payload is not None:
                write_json(run_dir / "raw_scenario.json", payload)
            write_json(run_dir / "metadata.json", metadata)
            baseline_rows.append(row)

    # Baseline duplicates are calculated from raw JSON; only externally valid rows count.
    seen: set[str] = set()
    for row in baseline_rows:
        from experiments.experiment_core import normalize_chain
        key = normalize_chain(baseline_payloads.get(row["run_id"])) if row["external_valid"] else None
        row["normalized_attack_chain"] = key
        row["duplicate_chain"] = bool(key and key in seen)
        if key:
            seen.add(key)

    write_csv(output / "scenario_runs.csv", platform_rows)
    write_csv(output / "generation_attempts.csv", attempt_rows)
    write_csv(output / "artifact_metrics.csv", artifact_rows)
    write_csv(output / "baseline_runs.csv", baseline_rows)

    overall = summarize_platform(platform_rows, artifact_rows)
    by_difficulty = {
        difficulty: summarize_platform(
            [row for row in platform_rows if row["requested_difficulty"] == difficulty],
            [row for row in artifact_rows if any(run["run_id"] == row["run_id"] and run["requested_difficulty"] == difficulty for run in platform_rows)],
        )
        for difficulty in DIFFICULTIES
    }
    baseline_rate = (100 * sum(row["external_valid"] for row in baseline_rows) / len(baseline_rows)) if baseline_rows else None
    summary = {
        "created_at": utc_now(),
        "platform": {"overall": overall, "by_difficulty": by_difficulty},
        "baseline": {
            "runs": len(baseline_rows),
            "external_validity_rate_percent": round(baseline_rate, 3) if baseline_rate is not None else None,
            "platform_first_attempt_validity_rate_percent": overall["first_attempt_validity_rate_percent"],
            "comparison": "Both values use the same external evaluator on raw first-response JSON; the baseline receives no platform parsing recovery, retries, schema construction, or ScenarioBuilder validation.",
        },
        "limitations": [
            "Structural validity and artifact completeness do not establish attack realism, technical feasibility, or training effectiveness.",
            "The platform records a UUID but does not guarantee semantic scenario uniqueness; duplicate detection is exact normalized attack-chain matching only.",
            "Ollama metadata is exported only when the server returns it.",
        ],
    }
    write_json(output / "experiment_summary.json", summary)
    print(f"Experiment infrastructure completed. Results written to: {output}")


if __name__ == "__main__":
    main()
