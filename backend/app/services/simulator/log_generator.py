from typing import Dict, List


class LogGenerator:
    """
    Generates realistic security logs
    from simulation events.
    """

    LOG_TEMPLATES = {
        "phishing": (
            "MAIL-GW01 Suspicious email received "
            "from attacker@fake-login.com "
            "targeting employee mailbox."
        ),

        "credential_access": (
            "AUTH-SRV01 Multiple failed login attempts "
            "detected for user j.smith."
        ),

        "lateral_movement": (
            "FILE-SRV01 Remote SMB connection "
            "initiated from WS-004."
        ),

        "privilege_escalation": (
            "DC01 Administrative privileges "
            "granted to unexpected account."
        ),

        "malware_execution": (
            "WS-010 Suspicious executable launched "
            "from Downloads directory."
        ),

        "data_exfiltration": (
            "FW01 Large outbound data transfer "
            "detected to external host."
        ),

        "reconnaissance": (
            "IDS01 Port scanning activity detected "
            "against internal network."
        ),

        "generic_attack": (
            "SYSTEM01 Suspicious activity detected."
        ),
    }

    @classmethod
    def generate_logs(
        cls,
        timeline: List[Dict],
        state
    ) -> List[Dict]:

        logs = []

        for event in timeline:

            event_type = event["event_type"]

            message = cls.LOG_TEMPLATES.get(
                event_type,
                cls.LOG_TEMPLATES["generic_attack"]
            )

            logs.append(
                {
                    "timestamp": event["timestamp"],
                    "event_type": event_type,
                    "attacker_ip": state.attacker_ip,
                    "attacker_hostname": state.attacker_hostname,
                    "target_ip": state.target_ip,
                    "target_hostname": state.target_hostname,
                    "log": message,
                }
            )

        return logs