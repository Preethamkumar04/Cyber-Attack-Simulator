"""Session-scoped, isolated Docker training lab orchestration.

This module deliberately uses the Docker CLI instead of a Docker SDK so the
application remains importable when Docker Desktop is absent.  Every command
uses an argument list (never a shell) and all containers are placed on an
internal, per-session network.
"""

from __future__ import annotations

import subprocess
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Tuple
from urllib.parse import urlparse

from app.core.config import settings
from app.services.artifacts.artifact_manager import ArtifactManager


class DockerLabError(RuntimeError):
    """A Docker lab could not be created or controlled."""


class DockerUnavailableError(DockerLabError):
    """Docker is disabled or Docker Desktop is not reachable."""


class DockerLabManager:
    """Creates and controls bounded, disposable labs for one training session."""

    def __init__(self) -> None:
        self.prefix = settings.DOCKER_NETWORK_PREFIX
        self.timeout = settings.DOCKER_LAB_TIMEOUT
        self.image = settings.DOCKER_LAB_IMAGE
        self.context = Path(settings.DOCKER_LAB_CONTEXT) if settings.DOCKER_LAB_CONTEXT else Path(__file__).resolve().parents[4] / "docker" / "lab"

    def names(self, session_id: int, lab_key: str | None = None) -> Dict[str, str]:
        # The immutable key avoids reusing a stale lab if a database was ever
        # restored and its numeric session IDs overlap an older deployment.
        suffix = f"-{lab_key}" if lab_key else ""
        base = f"{self.prefix}-{session_id}{suffix}"
        return {
            "network": base,
            "attacker": f"{base}-attacker",
            "target": f"{base}-target",
            "internal": f"{base}-service",
        }

    def _run(self, args: Iterable[str], *, timeout: int | None = None) -> str:
        if not settings.DOCKER_ENABLED:
            raise DockerUnavailableError("Docker labs are disabled (set DOCKER_ENABLED=true).")
        try:
            result = subprocess.run(
                ["docker", *args], capture_output=True, text=True,
                timeout=timeout or self.timeout, check=False,
            )
        except FileNotFoundError as exc:
            raise DockerUnavailableError("Docker CLI was not found. Start Docker Desktop and install Docker.") from exc
        except subprocess.TimeoutExpired as exc:
            raise DockerLabError("Docker operation timed out.") from exc
        if result.returncode:
            message = (result.stderr or result.stdout).strip()
            raise DockerLabError(message or "Docker operation failed.")
        return result.stdout.strip()

    def ensure_available(self) -> None:
        self._run(["info"], timeout=10)

    def _ensure_image(self) -> None:
        if not self.context.exists():
            raise DockerLabError(f"Docker lab build context is missing: {self.context}")
        self._run(["build", "--tag", self.image, str(self.context)], timeout=180)

    def create_lab(self, session_id: int, lab_key: str | None = None) -> Dict[str, str]:
        self.ensure_available()
        self._ensure_image()
        names = self.names(session_id, lab_key)
        label = f"cybersim.session_id={session_id}"
        key_label = f"cybersim.lab_key={lab_key or 'legacy'}"
        try:
            try:
                self._run(["network", "inspect", names["network"]])
            except DockerLabError:
                self._run(["network", "create", "--internal", "--label", label, "--label", key_label, names["network"]])

            for role in ("target", "internal", "attacker"):
                name = names[role]
                try:
                    self._run(["container", "inspect", name])
                    continue
                except DockerLabError:
                    pass
                args = [
                    "run", "--detach", "--name", name, "--network", names["network"],
                    "--network-alias", role if role != "internal" else "service",
                    "--label", label, "--label", key_label, "--read-only", "--tmpfs", "/tmp", "--cap-drop", "ALL",
                    "--security-opt", "no-new-privileges", "--pids-limit", "64", "--memory", "128m",
                    "--cpus", "0.50", "--env", f"LAB_ROLE={role}", self.image,
                ]
                if role == "attacker":
                    args.extend(["sleep", "infinity"])
                self._run(args)
            return self.status(session_id, lab_key)
        except DockerLabError:
            # A failed start must not leave partially-created session resources.
            self.remove_lab(session_id, lab_key)
            raise

    def _exec_request(self, session_id: int, host: str, path: str, lab_key: str | None = None) -> str:
        attacker = self.names(session_id, lab_key)["attacker"]
        program = (
                "import http.client; "
                "c=http.client.HTTPConnection(%r, 8080, timeout=5); "
                "c.request('GET', %r); "
                "r=c.getresponse(); "
                "print('%%s %%s' %% (r.status, r.read().decode()))"
        ) % (host, path)
        return self._run(["exec", attacker, "python", "-c", program], timeout=10)

    def _exec_container(self, session_id: int, command: list[str], lab_key: str | None = None) -> Tuple[str, int]:
        """Run a validated argv in the session's attacker container only."""
        if not settings.DOCKER_ENABLED:
            raise DockerUnavailableError("Docker labs are disabled (set DOCKER_ENABLED=true).")
        try:
            result = subprocess.run(
                ["docker", "exec", self.names(session_id, lab_key)["attacker"], *command],
                capture_output=True,
                text=True,
                timeout=min(self.timeout, 15),
                check=False,
            )
        except FileNotFoundError as exc:
            raise DockerUnavailableError("Docker CLI was not found. Start Docker Desktop and install Docker.") from exc
        except subprocess.TimeoutExpired:
            return ("Command timed out inside the Docker lab.", 124)
        output = "".join(part for part in (result.stdout, result.stderr) if part).strip()
        return (output or "(no output)", result.returncode)

    @staticmethod
    def _safe_url(value: str) -> bool:
        parsed = urlparse(value)
        return (
            parsed.scheme == "http"
            and parsed.hostname in {"target", "service"}
            and parsed.port in {None, 8080}
            and not parsed.username
            and not parsed.password
        )

    @staticmethod
    def _safe_path(value: str) -> bool:
        return value in {"/", "/lab", "/tmp", "/etc/hosts", "/etc/os-release", "/lab/service.py"}

    def _parse_terminal_command(self, command: str) -> Tuple[list[str] | None, str | None]:
        """Return a safe argv; user input is never sent through a shell."""
        try:
            parts = shlex.split(command, posix=True)
        except ValueError:
            return None, "Invalid command syntax."
        if not parts:
            return None, "Enter a command."
        if any(any(char in part for char in ";|&`$><") for part in parts):
            return None, "Shell operators are not permitted in the Docker lab."

        name, args = parts[0], parts[1:]
        if name in {"whoami", "pwd", "ps"} and not args:
            return [name], None
        if name == "ls" and (not args or all(arg in {"-a", "-l", "-la", "-al"} or self._safe_path(arg) for arg in args)):
            return [name, *args], None
        if name == "cat" and len(args) == 1 and self._safe_path(args[0]):
            return [name, args[0]], None
        if name == "grep" and len(args) in {2, 3} and self._safe_path(args[-1]):
            flags = args[:-2] if len(args) == 3 else []
            if not flags or flags == ["-i"]:
                return [name, *args], None
        if name == "ip" and args in (["addr"], ["route"]):
            return [name, *args], None
        if name in {"ss", "netstat"} and args in ([], ["-tuln"]):
            return [name, *args], None
        if name == "curl" and len(args) == 1 and self._safe_url(args[0]):
            return [name, "--fail", "--silent", "--show-error", args[0]], None
        if name == "wget" and len(args) == 1 and self._safe_url(args[0]):
            return [name, "-qO-", args[0]], None
        return None, "Unsupported or unsafe Docker-lab command. Type 'help' for allowed commands."

    def run_safe_sequence(self, session_id: int, scenario: Dict, lab_key: str | None = None) -> Dict:
        """Run deterministic HTTP requests against project-owned fake services only."""
        self._exec_request(session_id, "target", "/health", lab_key)
        self._exec_request(session_id, "target", "/reports/export?dataset=training", lab_key)
        self._exec_request(session_id, "service", "/authenticate?user=training-analyst", lab_key)
        command_path = ArtifactManager.get_artifact_paths(session_id)["command_history"]
        Path(command_path).parent.mkdir(parents=True, exist_ok=True)
        with open(command_path, "a", encoding="utf-8") as out:
            now = datetime.now(timezone.utc).isoformat()
            for action in ("GET target/health", "GET target/reports/export", "GET service/authenticate"):
                out.write(f"{now} | docker-attacker bounded-action {action}\n")
        collected = self.collect_logs(session_id, lab_key)
        return {"status": "completed", "actions": 3, "collected": collected, "scenario_mode": scenario.get("attack_mode")}

    def execute_validated_action(self, session_id: int, action_id: str, lab_key: str | None = None) -> str:
        """Execute one research-plan action from a fixed allowlist only.

        This deliberately accepts action identifiers, never an LLM/user command.
        """
        actions = {
            "web_health_check": ("target", "/health"),
            "report_export_check": ("target", "/reports/export?dataset=training"),
            "internal_auth_check": ("service", "/authenticate?user=training-analyst"),
        }
        action = actions.get(action_id)
        if action is None:
            raise DockerLabError("Unsupported validated action.")
        output = self._exec_request(session_id, action[0], action[1], lab_key)
        self.collect_logs(session_id, lab_key)
        return output

    def collect_logs(self, session_id: int, lab_key: str | None = None) -> Dict[str, int]:
        names = self.names(session_id, lab_key)
        raw: Dict[str, str] = {}
        for role in ("target", "internal", "attacker"):
            try:
                raw[role] = self._run(["logs", "--timestamps", names[role]])
            except DockerLabError:
                raw[role] = ""

        paths = ArtifactManager.get_artifact_paths(session_id)
        for path in paths.values():
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).isoformat()
        target_lines = [line for line in raw["target"].splitlines() if line]
        internal_lines = [line for line in raw["internal"].splitlines() if line]
        attacker_lines = [line for line in raw["attacker"].splitlines() if line]
        with open(paths["simulation_log"], "a", encoding="utf-8") as out:
            for line in target_lines + internal_lines:
                out.write(f"{timestamp} | docker | {line}\n")
        with open(paths["network_alerts"], "a", encoding="utf-8") as out:
            for line in target_lines + internal_lines:
                if "WEB_ACCESS" in line or "AUTH_EVENT" in line:
                    out.write(f"{timestamp} | Docker lab observation: {line}\n")
        with open(paths["traffic_log"], "a", encoding="utf-8") as out:
            for line in target_lines + internal_lines:
                out.write(f"{timestamp} | SRC=attacker | DST=lab-service | PROTO=HTTP | PORT=8080 | BYTES={len(line)}\n")
        with open(paths["command_history"], "a", encoding="utf-8") as out:
            for line in attacker_lines:
                out.write(f"{timestamp} | docker-attacker | {line}\n")
        return {"target": len(target_lines), "internal": len(internal_lines), "attacker": len(attacker_lines)}

    def execute_trainee_command(self, session_id: int, command: str, lab_key: str | None = None) -> Tuple[str, int]:
        normalized = command.strip().lower()
        if normalized == "help":
            return ("Docker lab commands: status, whoami, pwd, ls, ps, cat, grep, ip addr, ip route, ss, netstat, curl <http://target:8080/...>, wget <http://service:8080/...>, web-check, internal-check, collect", 0)
        if normalized == "status":
            status = self.status(session_id, lab_key)
            return (f"lab={status['state']} containers={status['containers']}", 0)
        if normalized == "web-check":
            output = self._exec_request(session_id, "target", "/health", lab_key)
            self.collect_logs(session_id, lab_key)
            return (output, 0)
        if normalized == "internal-check":
            output = self._exec_request(session_id, "service", "/authenticate?user=training-analyst", lab_key)
            self.collect_logs(session_id, lab_key)
            return (output, 0)
        if normalized == "collect":
            return (str(self.collect_logs(session_id, lab_key)), 0)
        argv, error = self._parse_terminal_command(command)
        if error:
            return (error, 2)
        output, exit_code = self._exec_container(session_id, argv, lab_key)
        if argv[0] in {"curl", "wget"}:
            self.collect_logs(session_id, lab_key)
        return output, exit_code

    def status(self, session_id: int, lab_key: str | None = None) -> Dict:
        names = self.names(session_id, lab_key)
        try:
            network = self._run(["network", "inspect", names["network"], "--format", "{{.Name}}"])
            containers = {}
            for role in ("attacker", "target", "internal"):
                try:
                    containers[role] = self._run(["container", "inspect", names[role], "--format", "{{.State.Status}}"])
                except DockerLabError:
                    containers[role] = "missing"
            state = "running" if network and all(value == "running" for value in containers.values()) else "degraded"
            return {"session_id": session_id, "state": state, "network": names["network"], "containers": containers}
        except DockerLabError:
            return {"session_id": session_id, "state": "missing", "network": names["network"], "containers": {}}

    def remove_lab(self, session_id: int, lab_key: str | None = None) -> None:
        names = self.names(session_id, lab_key)
        for role in ("attacker", "target", "internal"):
            try:
                self._run(["rm", "--force", names[role]])
            except DockerLabError:
                pass
        try:
            self._run(["network", "rm", names["network"]])
        except DockerLabError:
            pass

    def reset_lab(self, session_id: int, lab_key: str | None = None) -> Dict[str, str]:
        self.remove_lab(session_id, lab_key)
        return self.create_lab(session_id, lab_key)
