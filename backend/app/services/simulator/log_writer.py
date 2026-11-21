import os
from typing import Dict, List


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../../../"
    )
)


class LogWriter:
    """
    Writes generated simulation logs
    to a session-specific log file.
    """

    @staticmethod
    def write_logs(
        logs: List[Dict],
        session_id: int
    ) -> str:

        log_dir = os.path.join(
            BASE_DIR,
            "logs",
            "generated",
            str(session_id)
        )

        os.makedirs(
            log_dir,
            exist_ok=True
        )

        simulation_log_file = os.path.join(
            log_dir,
            "simulation.log"
        )

        with open(
            simulation_log_file,
            "a",
            encoding="utf-8"
        ) as log_file:

            for entry in logs:

                log_line = (
                    f"{entry['timestamp']} | "
                    f"{entry['event_type']} | "
                    f"{entry['log']}\n"
                )

                log_file.write(log_line)

        return simulation_log_file