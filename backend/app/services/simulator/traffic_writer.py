import os
from typing import Dict, List


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../../../"
    )
)


class TrafficWriter:

    @staticmethod
    def write_traffic(
        records: List[Dict],
        session_id: int
    ) -> str:

        traffic_dir = os.path.join(
            BASE_DIR,
            "logs",
            "traffic",
            str(session_id)
        )

        os.makedirs(
            traffic_dir,
            exist_ok=True
        )

        traffic_file = os.path.join(
            traffic_dir,
            "traffic.log"
        )

        with open(
            traffic_file,
            "a",
            encoding="utf-8"
        ) as file:

            for record in records:

                line = (
                    f"{record['timestamp']} | "
                    f"SRC={record['src_ip']} | "
                    f"DST={record['dst_ip']} | "
                    f"PROTO={record['protocol']} | "
                    f"PORT={record['port']} | "
                    f"BYTES={record['bytes']}\n"
                )

                file.write(line)

        return traffic_file