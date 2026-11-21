# from typing import Dict, List


# class NetworkGenerator:
#     """
#     Generates IDS / Firewall style alerts
#     from simulation timeline events.
#     """

#     ALERT_TEMPLATES = {
#         "phishing": (
#             "EMAIL-GW ALERT: Suspicious email "
#             "communication detected."
#         ),

#         "credential_access": (
#             "SIEM ALERT: Multiple failed "
#             "authentication attempts followed "
#             "by successful login."
#         ),

#         "lateral_movement": (
#             "IDS ALERT: Suspicious SMB "
#             "lateral movement activity detected."
#         ),

#         "privilege_escalation": (
#             "EDR ALERT: Administrative privilege "
#             "escalation detected."
#         ),

#         "data_exfiltration": (
#             "FIREWALL ALERT: Large outbound "
#             "data transfer detected."
#         ),

#         "reconnaissance": (
#             "IDS ALERT: Network scanning "
#             "activity detected."
#         ),

#         "generic_attack": (
#             "SECURITY ALERT: Suspicious "
#             "activity observed."
#         )
#     }

#     @classmethod
#     def generate_alerts(
#         cls,
#         timeline: List[Dict],
#         state
#     ) -> List[Dict]:

#         alerts = []

#         for event in timeline:

#             event_type = event["event_type"]

#             message = cls.ALERT_TEMPLATES.get(
#                 event_type,
#                 cls.ALERT_TEMPLATES["generic_attack"]
#             )

#             alerts.append(
#                 {
#                     "timestamp": event["timestamp"],
#                     "event_type": event_type,
#                     "attacker_ip": state.attacker_ip,
#                     "attacker_hostname": state.attacker_hostname,
#                     "target_ip": state.target_ip,
#                     "target_hostname": state.target_hostname,
#                     "alert": message
#                 }
#             )

#         return alerts

from typing import Dict, List


class NetworkGenerator:
    """
    Generates IDS / Firewall style alerts
    from simulation timeline events.
    """

    ALERT_TEMPLATES = {
        "phishing": (
            "EMAIL-GW ALERT: Suspicious email "
            "communication detected."
        ),

        "credential_access": (
            "SIEM ALERT: Multiple failed "
            "authentication attempts followed "
            "by successful login."
        ),

        "lateral_movement": (
            "IDS ALERT: Suspicious SMB "
            "lateral movement activity detected."
        ),

        "privilege_escalation": (
            "EDR ALERT: Administrative privilege "
            "escalation detected."
        ),

        "reconnaissance": (
            "IDS ALERT: Network scanning "
            "activity detected."
        ),

        "malware_execution": (
            "EDR ALERT: Suspicious executable "
            "execution detected on target host."
        ),

        "ransomware_execution": (
            "EDR ALERT: Multiple sensitive files "
            "modified by suspected ransomware."
        ),

        "data_exfiltration": (
            "FIREWALL ALERT: Large outbound "
            "data transfer detected to external host."
        ),

        "persistence": (
            "SECURITY ALERT: Suspicious persistence "
            "mechanism detected on target host."
        ),

        "command_and_control": (
            "FIREWALL ALERT: Outbound HTTPS "
            "connection to suspected command-and-control "
            "server detected."
        ),

        "generic_attack": (
            "SECURITY ALERT: Suspicious "
            "activity observed."
        ),
    }

    @classmethod
    def generate_alerts(
        cls,
        timeline: List[Dict],
        state
    ) -> List[Dict]:

        alerts = []

        for event in timeline:

            event_type = event["event_type"]

            message = cls.ALERT_TEMPLATES.get(
                event_type,
                cls.ALERT_TEMPLATES["generic_attack"]
            )

            alerts.append(
                {
                    "timestamp": event["timestamp"],
                    "event_type": event_type,
                    "attacker_ip": state.attacker_ip,
                    "attacker_hostname": state.attacker_hostname,
                    "target_ip": state.target_ip,
                    "target_hostname": state.target_hostname,
                    "alert": message,
                }
            )

        return alerts