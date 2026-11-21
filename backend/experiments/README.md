# Multi-scenario experiment infrastructure

Run from `backend` after configuring the same `.env` used by the application:

```powershell
python experiments/run_multiscenario_evaluation.py
```

The default performs the approved 15 platform runs and 15 direct-LLM baseline
runs sequentially. It never calls `/scenario/start`, opens no database session,
uses `MockAttackEngine` only, and redirects simulated artifacts to a fresh
`experiments/results/experiment_*` directory.

The output directory contains `scenario_runs.csv`, `generation_attempts.csv`,
`artifact_metrics.csv`, `baseline_runs.csv`, `experiment_summary.json`, plus
raw model responses and per-run JSON metadata. It is intentionally not invoked
by normal application startup or tests.
