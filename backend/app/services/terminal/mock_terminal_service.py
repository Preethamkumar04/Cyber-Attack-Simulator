"""
MockTerminalService — simulates a SOC analyst shell for training exercises.

Why this exists:
  Provides interactive command responses derived from generated artifact logs
  until a real Docker shell or remote terminal backend is connected. Keeps
  terminal behaviour behind a service boundary the API route can swap later.
"""

import os
import re
from typing import Dict, Tuple

from app.services.artifacts.artifact_manager import ArtifactManager


class MockTerminalService:

    PROMPT = "analyst@soc-workstation:~$"

    @classmethod
    def _read_artifact(cls, key: str) -> str:
        paths = ArtifactManager.get_artifact_paths()
        mapping = {
            "simulation": "simulation_log",
            "network": "network_alerts",
            "traffic": "traffic_log",
            "commands": "command_history",
        }
        path_key = mapping.get(key, key)
        file_path = paths.get(path_key, "")

        if not file_path or not os.path.exists(file_path):
            return ""

        with open(file_path, "r", encoding="utf-8") as handle:
            return handle.read()

    @classmethod
    def _grep(cls, pattern: str, content: str) -> str:
        if not content:
            return f"grep: no log data available for pattern '{pattern}'"

        lines = [
            line for line in content.splitlines()
            if re.search(pattern, line, re.IGNORECASE)
        ]

        if not lines:
            return f"(no matches for '{pattern}')"

        return "\n".join(lines)

    @classmethod
    def execute(cls, command: str) -> Tuple[str, int]:
        command = command.strip()

        if not command:
            return "", 0

        lower = command.lower()

        if lower in {"help", "?"}:
            return cls._help_text(), 0

        if lower in {"clear", "cls"}:
            return "__CLEAR__", 0

        if lower == "whoami":
            return "analyst", 0

        if lower == "hostname":
            return "soc-workstation", 0

        if lower == "pwd":
            return "/home/analyst/investigation", 0

        if lower.startswith("ls"):
            return (
                "artifacts/\nlogs/\nevidence/\nnotes.txt\nrunbook.md",
                0,
            )

        if lower.startswith("cat "):
            target = command[4:].strip()

            if "simulation" in target or "auth.log" in target:
                content = cls._read_artifact("simulation")
                return content or "cat: file not found", 1 if not content else 0

            if "network" in target or "alert" in target:
                content = cls._read_artifact("network")
                return content or "cat: file not found", 1 if not content else 0

            if "traffic" in target:
                content = cls._read_artifact("traffic")
                return content or "cat: file not found", 1 if not content else 0

            if "command" in target or "history" in target:
                content = cls._read_artifact("commands")
                return content or "cat: file not found", 1 if not content else 0

            return f"cat: {target}: No such file or directory", 1

        if lower.startswith("grep "):
            parts = command.split(maxsplit=2)
            if len(parts) < 2:
                return "grep: missing pattern", 1

            pattern = parts[1].strip("'\"")
            source = parts[2] if len(parts) > 2 else "simulation.log"

            if "network" in source:
                content = cls._read_artifact("network")
            elif "traffic" in source:
                content = cls._read_artifact("traffic")
            elif "command" in source or "history" in source:
                content = cls._read_artifact("commands")
            else:
                content = cls._read_artifact("simulation")

            return cls._grep(pattern, content), 0

        if lower.startswith("tail"):
            content = cls._read_artifact("simulation")
            if not content:
                return "tail: simulation.log: No such file", 1
            lines = content.splitlines()
            return "\n".join(lines[-10:]), 0

        if lower.startswith("head"):
            content = cls._read_artifact("simulation")
            if not content:
                return "head: simulation.log: No such file", 1
            lines = content.splitlines()
            return "\n".join(lines[:10]), 0

        if lower.startswith("wc "):
            content = cls._read_artifact("simulation")
            if not content:
                return "wc: file not found", 1
            count = len([line for line in content.splitlines() if line.strip()])
            return f"{count}  {count}  {count * 80} simulation.log", 0

        return (
            f"bash: {command.split()[0]}: command not found\n"
            f"Type 'help' for supported investigation commands.",
            127,
        )

    @classmethod
    def _help_text(cls) -> str:
        return (
            "SOC Investigation Shell (mock mode)\n"
            "-----------------------------------\n"
            "  ls                  List investigation directory\n"
            "  cat simulation.log  View system/security simulation logs\n"
            "  cat network_alerts  View IDS/network alert log\n"
            "  cat traffic.log     View network traffic log\n"
            "  cat command_history View attacker command history\n"
            "  grep <pat> <file>   Search logs for a pattern\n"
            "  tail / head         View log head/tail\n"
            "  whoami / hostname   Session identity\n"
            "  clear               Clear terminal screen"
        )
