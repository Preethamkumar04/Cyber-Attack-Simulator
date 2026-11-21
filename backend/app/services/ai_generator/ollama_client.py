import json
import logging
import re
import time
from typing import Optional

import requests

from app.core.config import settings
from app.schemas.scenario_schema import ScenarioSchema

logger = logging.getLogger(__name__)


class OllamaClient:
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0

    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL

    def generate_scenario(self, difficulty: str) -> ScenarioSchema:
        prompt = self._build_scenario_prompt(difficulty)

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                        },
                    },
                    timeout=120,
                )
                response.raise_for_status()

                data = response.json()
                generated_text = data.get("response", "").strip()

                scenario_data = self._parse_json_safely(generated_text)

                if scenario_data is None:
                    raise ValueError("Failed to parse valid JSON from Ollama response")

                scenario_data["difficulty"] = difficulty
                scenario = ScenarioSchema(**scenario_data)
                logger.info(f"Generated scenario for difficulty={difficulty} on attempt {attempt}")
                return scenario

            except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Attempt {attempt}/{self.MAX_RETRIES} failed: {e}")
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY * attempt)
                else:
                    logger.error(f"All {self.MAX_RETRIES} attempts failed for difficulty={difficulty}")
                    raise RuntimeError(f"Failed to generate valid scenario after {self.MAX_RETRIES} attempts: {e}")

    def _parse_json_safely(self, text: str) -> Optional[dict]:
        text = text.strip()

        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    @staticmethod
    def _build_scenario_prompt(difficulty: str) -> str:
        return f"""
You are a cybersecurity attack planner for a training simulator.

Generate ONE completely unique cyber attack scenario for difficulty: {difficulty}.

Rules:
1. Select attack_mode: "active", "passive", or "hybrid"
2. Create attack_chain as SHORT steps only (3-6 steps).
   Example: ["Recon", "Phishing", "Credential Harvesting", "Privilege Escalation", "Lateral Movement"]
3. Create hidden_objectives (internal, not shown to trainee).
4. Generate evaluation answer key.

Return ONLY valid JSON in exactly this format:
{{
    "attack_mode": "",
    "difficulty": "{difficulty}",
    "attack_chain": [],
    "hidden_objectives": [],
    "expected_findings": [],
    "expected_commands": [],
    "expected_root_cause": "",
    "expected_severity": "",
    "expected_mitigation": []
}}

Requirements:
- attack_chain: 3-6 short labels describing the attack progression
- hidden_objectives: Specific attacker goals (e.g., "Steal admin credentials", "Exfiltrate customer database")
- expected_findings: What a SOC analyst should discover (short bullets)
- expected_commands: Plain Linux investigation commands ONLY (no backticks, markdown, explanations)
  Example: ["cat /var/log/auth.log", "grep 'Failed password' /var/log/auth.log", "last", "netstat -tulnp"]
- expected_root_cause: Single short sentence
- expected_severity: Exactly one of: Low, Medium, High, Critical
- expected_mitigation: Practical remediation steps as short action items

Difficulty guidelines:
- BEGINNER: Simple chain (3-4 steps), basic attacks (phishing, brute force), Low/Medium severity
- INTERMEDIATE: Multi-step chain (4-5 steps), lateral movement, privilege escalation, Medium/High severity
- ADVANCED: Complex chain (5-6 steps), APT-style, persistence, data exfiltration, High/Critical severity

Return JSON only.
""".strip()