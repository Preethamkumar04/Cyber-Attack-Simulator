
# import os


# BASE_DIR = os.path.abspath(
#     os.path.join(
#         os.path.dirname(__file__),
#         "../../../../"
#     )
# )


# class ArtifactManager:

#     @classmethod
#     def clear_artifacts(cls, session_id: int):

#         session_generated_dir = os.path.join(
#             BASE_DIR,
#             "logs",
#             "generated",
#             str(session_id)
#         )

#         session_traffic_dir = os.path.join(
#             BASE_DIR,
#             "logs",
#             "traffic",
#             str(session_id)
#         )

#         artifact_files = [
#             os.path.join(
#                 session_generated_dir,
#                 "simulation.log"
#             ),
#             os.path.join(
#                 session_generated_dir,
#                 "network_alerts.log"
#             ),
#             os.path.join(
#                 session_generated_dir,
#                 "command_history.log"
#             ),
#             os.path.join(
#                 session_traffic_dir,
#                 "traffic.log"
#             )
#         ]

#         for file_path in artifact_files:

#             if os.path.exists(file_path):

#                 open(
#                     file_path,
#                     "w",
#                     encoding="utf-8"
#                 ).close()

#     @classmethod
#     def get_artifact_paths(cls, session_id: int):

#         generated_dir = os.path.join(
#             BASE_DIR,
#             "logs",
#             "generated",
#             str(session_id)
#         )

#         traffic_dir = os.path.join(
#             BASE_DIR,
#             "logs",
#             "traffic",
#             str(session_id)
#         )

#         return {
#             "simulation_log": os.path.join(
#                 generated_dir,
#                 "simulation.log"
#             ),
#             "network_alerts": os.path.join(
#                 generated_dir,
#                 "network_alerts.log"
#             ),
#             "command_history": os.path.join(
#                 generated_dir,
#                 "command_history.log"
#             ),
#             "traffic_log": os.path.join(
#                 traffic_dir,
#                 "traffic.log"
#             )
#         }

#     @classmethod
#     def verify_artifacts(cls, session_id: int):

#         paths = cls.get_artifact_paths(session_id)

#         return {
#             os.path.basename(path): os.path.exists(path)
#             for path in paths.values()
#         }

import os


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../../../"
    )
)


class ArtifactManager:

    @classmethod
    def get_artifact_paths(
        cls,
        session_id: int,
    ):

        return {
            "simulation_log": os.path.join(
                BASE_DIR,
                "logs",
                "generated",
                str(session_id),
                "simulation.log",
            ),

            "network_alerts": os.path.join(
                BASE_DIR,
                "logs",
                "generated",
                str(session_id),
                "network_alerts.log",
            ),

            "command_history": os.path.join(
                BASE_DIR,
                "logs",
                "generated",
                str(session_id),
                "command_history.log",
            ),

            "traffic_log": os.path.join(
                BASE_DIR,
                "logs",
                "traffic",
                str(session_id),
                "traffic.log",
            ),
        }

    @classmethod
    def clear_artifacts(
        cls,
        session_id: int,
    ):

        paths = cls.get_artifact_paths(
            session_id
        )

        for file_path in paths.values():

            if os.path.exists(file_path):

                open(
                    file_path,
                    "w",
                    encoding="utf-8",
                ).close()

    @classmethod
    def verify_artifacts(
        cls,
        session_id: int,
    ):

        paths = cls.get_artifact_paths(
            session_id
        )

        return {
            os.path.basename(path): os.path.exists(path)
            for path in paths.values()
        }