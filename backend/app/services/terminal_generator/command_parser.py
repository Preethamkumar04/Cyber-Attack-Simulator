from typing import Dict, Optional

from app.services.simulator.simulation_state import SimulationState


class CommandParser:
    """
    Parses investigation commands entered by the trainee.

    Commands operate only against the simulated environment.
    They never execute commands on the real host machine.
    """

    @staticmethod
    def execute(
        command: str,
        state: SimulationState
    ) -> Dict:

        command = command.strip()

        if not command:
            return {
                "command": command,
                "success": False,
                "output": "",
                "error": "Empty command"
            }

        state.record_command(command)

        parts = command.split(maxsplit=1)
        base_command = parts[0].lower()
        argument: Optional[str] = (
            parts[1].strip()
            if len(parts) > 1
            else None
        )

        # -------------------------
        # whoami
        # -------------------------

        if base_command == "whoami":

            return {
                "command": command,
                "success": True,
                "output": "j.smith"
            }

        # -------------------------
        # hostname
        # -------------------------

        if base_command == "hostname":

            return {
                "command": command,
                "success": True,
                "output": state.target_hostname
            }

        # -------------------------
        # pwd
        # -------------------------

        if base_command == "pwd":

            return {
                "command": command,
                "success": True,
                "output": state.current_directory,
                "error": None
            }

        # -------------------------
        # cd
        # -------------------------

        if base_command == "cd":

            # cd with no argument → home directory
            if not argument:
                state.current_directory = "/home/j.smith"

                return {
                    "command": command,
                    "success": True,
                    "output": "",
                    "error": None
                }

            target_path = argument

            # Check if target is a real simulated directory
            if not state.filesystem.directory_exists(target_path):

                if state.filesystem.file_exists(target_path):
                    return {
                        "command": command,
                        "success": False,
                        "output": "",
                        "error": (
                            f"cd: {target_path}: "
                            "Not a directory"
                        )
                    }

                return {
                    "command": command,
                    "success": False,
                    "output": "",
                    "error": (
                        f"cd: {target_path}: "
                        "No such file or directory"
                    )
                }

            state.current_directory = target_path

            return {
                "command": command,
                "success": True,
                "output": "",
                "error": None
            }

        # -------------------------
        # ls
        # -------------------------

        if base_command == "ls":

            path = argument or "/home/j.smith"

            if not state.filesystem.directory_exists(path):
                if state.filesystem.file_exists(path):
                    return {
                        "command": command,
                        "success": False,
                        "output": "",
                        "error": (
                            f"ls: {path}: "
                            "Not a directory"
                        )
                    }

                return {
                    "command": command,
                    "success": False,
                    "output": "",
                    "error": (
                        f"ls: {path}: "
                        "No such file or directory"
                    )
                }

            entries = state.filesystem.list_directory(path)

            for entry in entries:
                if path == "/":
                    entry_path = f"/{entry}"
                else:
                    entry_path = f"{path.rstrip('/')}/{entry}"

                if state.filesystem.file_exists(entry_path):
                    state.discover_file(entry_path)

                elif state.filesystem.directory_exists(entry_path):
                    state.discover_directory(entry_path)

            return {
                "command": command,
                "success": True,
                "output": "\n".join(entries),
                "error": None
            }
        # -------------------------
        # cat
        # -------------------------

        if base_command == "cat":

            if not argument:
                return {
                    "command": command,
                    "success": False,
                    "output": "",
                    "error": "cat: missing file operand"
                }

            if state.filesystem.directory_exists(argument):
                return {
                    "command": command,
                    "success": False,
                    "output": "",
                    "error": (
                        f"cat: {argument}: "
                        "Is a directory"
                    )
                }

            if not state.filesystem.file_exists(argument):
                return {
                    "command": command,
                    "success": False,
                    "output": "",
                    "error": (
                        f"cat: {argument}: "
                        "No such file or directory"
                    )
                }

            state.access_file(argument)

            content = state.filesystem.read_file(argument)

            return {
                "command": command,
                "success": True,
                "output": content
            }

        # -------------------------
        # find
        # -------------------------

        if base_command == "find":

            if not argument:
                path = "/"
                name_filter = None

            else:
                find_parts = argument.split()

                path = find_parts[0]
                name_filter = None

                if (
                    len(find_parts) == 3
                    and find_parts[1] == "-name"
                ):
                    name_filter = find_parts[2]

                elif len(find_parts) > 1:
                    return {
                        "command": command,
                        "success": False,
                        "output": "",
                        "error": "find: unsupported arguments"
                    }

            if not state.filesystem.directory_exists(path):
                if state.filesystem.file_exists(path):
                    return {
                        "command": command,
                        "success": False,
                        "output": "",
                        "error": (
                            f"find: {path}: "
                            "Not a directory"
                        )
                    }

                return {
                    "command": command,
                    "success": False,
                    "output": "",
                    "error": (
                        f"find: {path}: "
                        "No such file or directory"
                    )
                }

            files = []

            for file_path in state.filesystem.list_files():

                if not file_path.startswith(path):
                    continue

                if name_filter:
                    filename = file_path.rsplit("/", 1)[-1]

                    if filename != name_filter:
                        continue

                files.append(file_path)
                state.discover_file(file_path)

            return {
                "command": command,
                "success": True,
                "output": "\n".join(files),
                "error": None
            }

        # -------------------------
        # extra
        # -------------------------

        # -------------------------
        # ip
        # -------------------------

        if base_command == "ip":

            output = (
                f"Attacker IP: {state.attacker_ip}\n"
                f"Target IP: {state.target_ip}\n"
                f"Hostname: {state.target_hostname}"
            )

            return {
                "command": command,
                "success": True,
                "output": output,
                "error": None
            }

        # -------------------------
        # ifconfig
        # -------------------------

        if base_command == "ifconfig":

            output = (
                "eth0\n"
                f"    inet {state.target_ip}\n"
                "    netmask 255.255.255.0\n"
                "    status UP"
            )

            return {
                "command": command,
                "success": True,
                "output": output,
                "error": None
            }

        # -------------------------
        # ps
        # -------------------------

        if base_command == "ps":

            output = (
                "PID     PROCESS\n"
                "1       system\n"
                "101     nginx\n"
                "202     sshd\n"
                "303     python"
            )

            if state.malware_executed:
                output += "\n404     simulated_payload"

            return {
                "command": command,
                "success": True,
                "output": output,
                "error": None
            }

        # -------------------------
        # netstat
        # -------------------------

        if base_command == "netstat":

            if not state.network_connections:
                return {
                    "command": command,
                    "success": True,
                    "output": "No active network connections",
                    "error": None
                }

            lines = [
                "SRC             DST             PROTOCOL    PORT"
            ]

            for connection in state.network_connections:

                lines.append(
                    f"{connection['src_ip']:<15} "
                    f"{connection['dst_ip']:<15} "
                    f"{connection['protocol']:<11} "
                    f"{connection['port']}"
                )

            return {
                "command": command,
                "success": True,
                "output": "\n".join(lines),
                "error": None
            }

        # -------------------------
        # history
        # -------------------------

        if base_command == "history":

            commands = state.executed_commands

            if not commands:
                return {
                    "command": command,
                    "success": True,
                    "output": ""
                }

            output = "\n".join(
                f"{index + 1}  {cmd}"
                for index, cmd in enumerate(commands)
            )

            return {
                "command": command,
                "success": True,
                "output": output
            }

        # -------------------------
        # Unsupported command
        # -------------------------

        return {
            "command": command,
            "success": False,
            "output": "",
            "error": (
                f"command not found: {base_command}"
            )
        }