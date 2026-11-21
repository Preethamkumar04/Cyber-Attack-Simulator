# import os
# from typing import Dict, List


# BASE_DIR = os.path.abspath(
#     os.path.join(
#         os.path.dirname(__file__),
#         "../../../../"
#     )
# )

# LOG_DIR = os.path.join(
#     BASE_DIR,
#     "logs",
#     "generated"
# )

# os.makedirs(
#     LOG_DIR,
#     exist_ok=True
# )

# COMMAND_HISTORY_FILE = os.path.join(
#     LOG_DIR,
#     "command_history.log"
# )


# class TerminalWriter:

#     @staticmethod
#     def write_history(
#         history: List[Dict]
#     ) -> str:

#         with open(
#             COMMAND_HISTORY_FILE,
#             "a",
#             encoding="utf-8"
#         ) as file:

#             for entry in history:

#                 line = (
#                     f"{entry['timestamp']} | "
#                     f"{entry['command']}\n"
#                 )

#                 file.write(line)

#         return COMMAND_HISTORY_FILE

import os
from typing import Dict, List


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../../../"
    )
)


class TerminalWriter:

    @staticmethod
    def write_history(
        history: List[Dict],
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

        command_history_file = os.path.join(
            log_dir,
            "command_history.log"
        )

        with open(
            command_history_file,
            "a",
            encoding="utf-8"
        ) as file:

            for entry in history:

                line = (
                    f"{entry['timestamp']} | "
                    f"{entry['command']}\n"
                )

                file.write(line)

        return command_history_file