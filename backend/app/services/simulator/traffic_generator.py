# import random
# from typing import Dict, List


# class TrafficGenerator:
#     """
#     Generates simulated network traffic
#     from timeline events.
#     """

#     TRAFFIC_TEMPLATES = {
#         "phishing": {
#             "src_ip": "10.10.1.25",
#             "dst_ip": "185.201.10.5",
#             "protocol": "HTTPS",
#             "port": 443,
#         },

#         "credential_access": {
#             "src_ip": "10.10.1.45",
#             "dst_ip": "10.10.1.10",
#             "protocol": "LDAP",
#             "port": 389,
#         },

#         "lateral_movement": {
#             "src_ip": "10.10.1.45",
#             "dst_ip": "10.10.1.20",
#             "protocol": "SMB",
#             "port": 445,
#         },

#         "privilege_escalation": {
#             "src_ip": "10.10.1.20",
#             "dst_ip": "10.10.1.10",
#             "protocol": "RPC",
#             "port": 135,
#         },

#         "data_exfiltration": {
#             "src_ip": "10.10.1.20",
#             "dst_ip": "203.0.113.100",
#             "protocol": "HTTPS",
#             "port": 443,
#         },

#         "reconnaissance": {
#             "src_ip": "10.10.1.45",
#             "dst_ip": "10.10.1.0/24",
#             "protocol": "TCP",
#             "port": 0,
#         },
#     }

#     @classmethod
#     def generate_traffic(
#         cls,
#         timeline: List[Dict],
#         state
#     ) -> List[Dict]:

#         traffic_records = []

#         for event in timeline:

#             template = cls.TRAFFIC_TEMPLATES.get(
#                 event["event_type"]
#             )

#             if not template:
#                 continue

#             traffic_records.append(
#                 {
#                     "timestamp": event["timestamp"],
#                     "event_type": event["event_type"],
#                     "src_ip": state.attacker_ip,
#                     "dst_ip": state.target_ip,
#                     "src_hostname": state.attacker_hostname,
#                     "dst_hostname": state.target_hostname,
#                     "protocol": template["protocol"],
#                     "port": template["port"],
#                     "bytes": random.randint(
#                         500,
#                         5000
#                     ),
#                 }
#             )

#         return traffic_records

from typing import Dict, List


class TrafficGenerator:
    """
    Generates simulated network traffic
    from timeline events.
    """

    TRAFFIC_TEMPLATES = {
        "phishing": {
            "src_ip": "10.10.1.25",
            "dst_ip": "185.201.10.5",
            "protocol": "HTTPS",
            "port": 443,
        },

        "credential_access": {
            "src_ip": "10.10.1.45",
            "dst_ip": "10.10.1.10",
            "protocol": "LDAP",
            "port": 389,
        },

        "lateral_movement": {
            "src_ip": "10.10.1.45",
            "dst_ip": "10.10.1.20",
            "protocol": "SMB",
            "port": 445,
        },

        "privilege_escalation": {
            "src_ip": "10.10.1.20",
            "dst_ip": "10.10.1.10",
            "protocol": "RPC",
            "port": 135,
        },

        "data_exfiltration": {
            "src_ip": "10.10.1.20",
            "dst_ip": "203.0.113.100",
            "protocol": "HTTPS",
            "port": 443,
        },

        "reconnaissance": {
            "src_ip": "10.10.1.45",
            "dst_ip": "10.10.1.0/24",
            "protocol": "TCP",
            "port": 0,
        },

        "malware_execution": {
            "src_ip": "10.10.1.45",
            "dst_ip": "10.10.1.20",
            "protocol": "HTTPS",
            "port": 443,
        },

        "ransomware_execution": {
            "src_ip": "10.10.1.45",
            "dst_ip": "10.10.1.20",
            "protocol": "SMB",
            "port": 445,
        },

        "persistence": {
            "src_ip": "10.10.1.45",
            "dst_ip": "10.10.1.20",
            "protocol": "TCP",
            "port": 445,
        },

        "command_and_control": {
            "src_ip": "10.10.1.45",
            "dst_ip": "203.0.113.50",
            "protocol": "HTTPS",
            "port": 443,
        },
    }

    @classmethod
    def generate_traffic(
        cls,
        timeline: List[Dict],
        state
    ) -> List[Dict]:

        traffic_records = []

        for event in timeline:

            event_type = event["event_type"]

            template = cls.TRAFFIC_TEMPLATES.get(
                event_type
            )

            if not template:
                continue

            traffic_records.append(
                {
                    "timestamp": event["timestamp"],
                    "event_type": event_type,

                    # Use the traffic template
                    # instead of ignoring its IP addresses.
                    "src_ip": template["src_ip"],
                    "dst_ip": template["dst_ip"],

                    "src_hostname": state.attacker_hostname,
                    "dst_hostname": state.target_hostname,

                    "protocol": template["protocol"],
                    "port": template["port"],

                    "bytes": 1000,
                }
            )

        return traffic_records