import os
from typing import Dict, List


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../../../"
    )
)


class NetworkWriter:

    @staticmethod
    def write_alerts(
        alerts: List[Dict],
        session_id: int
    ) -> str:

        network_dir = os.path.join(
            BASE_DIR,
            "logs",
            "generated",
            str(session_id)
        )

        os.makedirs(
            network_dir,
            exist_ok=True
        )

        alert_file = os.path.join(
            network_dir,
            "network_alerts.log"
        )

        with open(
            alert_file,
            "a",
            encoding="utf-8"
        ) as file:

            for alert in alerts:

                line = (
                    f"{alert['timestamp']} | "
                    f"{alert['alert']}\n"
                )

                file.write(line)

        return alert_file