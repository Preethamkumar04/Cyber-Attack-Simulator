def build_scenario_prompt(difficulty: str) -> str:

    return f"""
You are a cybersecurity attack planner for a training simulator.

Generate ONE completely unique cyber attack scenario.

Rules:

1. Select attack mode:
   - active
   - passive
   - hybrid

2. Create attack_chain as SHORT steps only.

Example:

[
"Recon",
"Phishing",
"Credential Harvesting",
"Privilege Escalation",
"Lateral Movement"
]

3. Create hidden objectives.

4. Generate an evaluation answer key.

Difficulty:
{difficulty}

Return ONLY valid JSON in exactly this format:

{{
    "attack_mode":"",
    "difficulty":"",
    "attack_chain":[],
    "hidden_objectives":[],

    "expected_findings":[],
    "expected_commands":[],
    "expected_root_cause":"",
    "expected_severity":"",
    "expected_mitigation":[]
}}

Requirements:

- expected_findings should describe what a SOC analyst is expected to discover during the investigation.
  Return short bullet-style findings only.

- expected_commands should contain ONLY plain Linux investigation commands.
  Do NOT use:
  - backticks (` )
  - markdown
  - explanations
  - command output

  Example:
  [
    "cat /var/log/auth.log",
    "grep 'Failed password' /var/log/auth.log",
    "last",
    "netstat -tulnp"
  ]

- expected_root_cause should be a single short sentence describing the primary cause of the attack.

- expected_severity must be exactly one of:
  Low
  Medium
  High
  Critical

  Assign severity based on attack impact.
  Examples:
  - Recon only → Low
  - Credential theft → High
  - Privilege escalation → High
  - Ransomware → Critical
  - Domain compromise → Critical

- expected_mitigation should contain practical remediation steps as a list of short action items.

Return JSON only.
"""