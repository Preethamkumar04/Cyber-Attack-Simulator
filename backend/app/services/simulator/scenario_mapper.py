from typing import Dict, List


class ScenarioMapper:
    """
    Converts AI-generated attack chain steps
    into standardized simulation event types.
    """

    EVENT_MAPPING = {
        "phishing": "phishing",
        "credential": "credential_access",
        "password": "credential_access",
        "lateral": "lateral_movement",
        "privilege": "privilege_escalation",
        "reconnaissance": "reconnaissance",
        "scan": "reconnaissance",
        "malware": "malware_execution",
        "ransomware": "ransomware_execution",
        "exfiltration": "data_exfiltration",
        "exfiltrate": "data_exfiltration",
        "data theft": "data_exfiltration",
        "persistence": "persistence",
        "c2": "command_and_control",
        "command and control": "command_and_control",
    }

    EVENT_METADATA = {
        "phishing": {
            "target": "user_account",
            "state_changes": ["user_targeted"],
            "evidence_types": [
                "email_log",
                "authentication_log",
                "security_alert",
            ],
        },
        "credential_access": {
            "target": "user_account",
            "state_changes": ["account_compromised"],
            "evidence_types": [
                "authentication_log",
                "security_alert",
                "command_history",
            ],
        },
        "lateral_movement": {
            "target": "internal_host",
            "state_changes": ["host_accessed"],
            "evidence_types": [
                "network_log",
                "traffic",
                "command_history",
            ],
        },
        "privilege_escalation": {
            "target": "target_host",
            "state_changes": ["privileges_escalated"],
            "evidence_types": [
                "security_log",
                "process_log",
                "command_history",
            ],
        },
        "reconnaissance": {
            "target": "network",
            "state_changes": ["services_discovered"],
            "evidence_types": [
                "network_log",
                "traffic",
                "command_history",
            ],
        },
        "malware_execution": {
            "target": "target_host",
            "state_changes": ["malware_executed"],
            "evidence_types": [
                "process_log",
                "security_alert",
                "command_history",
            ],
        },
        "ransomware_execution": {
            "target": "target_host",
            "state_changes": ["files_affected"],
            "evidence_types": [
                "file_log",
                "process_log",
                "security_alert",
            ],
        },
        "data_exfiltration": {
            "target": "sensitive_data",
            "state_changes": ["data_exfiltrated"],
            "evidence_types": [
                "file_log",
                "network_log",
                "traffic",
            ],
        },
        "persistence": {
            "target": "target_host",
            "state_changes": ["persistence_established"],
            "evidence_types": [
                "system_log",
                "process_log",
                "command_history",
            ],
        },
        "command_and_control": {
            "target": "target_host",
            "state_changes": ["c2_established"],
            "evidence_types": [
                "network_log",
                "traffic",
                "security_alert",
            ],
        },
        "generic_attack": {
            "target": "target_host",
            "state_changes": [],
            "evidence_types": [
                "security_log",
            ],
        },
    }

    @classmethod
    def map_attack_chain(
        cls,
        attack_chain: List[str]
    ) -> List[Dict]:
        """
        Convert attack chain text into
        normalized simulation events.
        """

        events = []

        for step_number, step_text in enumerate(
            attack_chain,
            start=1
        ):
            event_type = "generic_attack"

            step_lower = step_text.lower()

            for keyword, mapped_type in cls.EVENT_MAPPING.items():
                if keyword in step_lower:
                    event_type = mapped_type
                    break

            metadata = cls.EVENT_METADATA.get(
                event_type,
                cls.EVENT_METADATA["generic_attack"]
            )

            events.append(
                {
                    "step": step_number,
                    "description": step_text,
                    "event_type": event_type,
                    "target": metadata["target"],
                    "state_changes": metadata["state_changes"].copy(),
                    "evidence_types": metadata["evidence_types"].copy(),
                }
            )

        return events