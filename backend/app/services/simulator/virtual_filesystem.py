from typing import Dict, List, Optional


class VirtualFilesystem:
    """
    Simulated filesystem for the cyber attack training environment.

    This does NOT access the real computer filesystem.
    It stores files entirely in memory.
    """

    def __init__(self) -> None:

        self.directories = {
            "/",
            "/etc",
            "/home",
            "/home/j.smith",
            "/data",
            "/var",
            "/var/log",
            "/tmp",
        }

        self.files: Dict[str, Dict] = {
            "/etc/passwd": {
                "type": "file",
                "content": (
                    "root:x:0:0:root:/root:/bin/bash\n"
                    "j.smith:x:1001:1001:John Smith:/home/j.smith:/bin/bash"
                ),
                "sensitive": True,
                "accessed": False,
            },

            "/etc/hosts": {
                "type": "file",
                "content": (
                    "127.0.0.1 localhost\n"
                    "10.10.10.20 WEB-SERVER"
                ),
                "sensitive": False,
                "accessed": False,
            },

            "/home/j.smith/notes.txt": {
                "type": "file",
                "content": (
                    "TODO:\n"
                    "Check employee database credentials.\n"
                    "Username: j.smith"
                ),
                "sensitive": True,
                "accessed": False,
            },

            "/data/employee_records.csv": {
                "type": "file",
                "content": (
                    "employee_id,name,department,salary\n"
                    "1001,John Smith,Engineering,75000\n"
                    "1002,Alice Brown,Finance,82000\n"
                    "1003,David Wilson,HR,68000"
                ),
                "sensitive": True,
                "accessed": False,
            },

            "/data/financial_report.txt": {
                "type": "file",
                "content": (
                    "CONFIDENTIAL FINANCIAL REPORT\n"
                    "Quarterly revenue: $2,450,000\n"
                    "Internal use only."
                ),
                "sensitive": True,
                "accessed": False,
            },

            "/var/log/auth.log": {
                "type": "file",
                "content": (
                    "INFO Login attempt for user j.smith\n"
                    "WARNING Multiple failed login attempts\n"
                    "INFO Successful authentication for j.smith"
                ),
                "sensitive": False,
                "accessed": False,
            },

            "/var/log/access.log": {
                "type": "file",
                "content": (
                    "10.10.10.50 - GET /login\n"
                    "10.10.10.50 - POST /login\n"
                    "10.10.10.50 - GET /admin"
                ),
                "sensitive": False,
                "accessed": False,
            },
        }

    def file_exists(self, path: str) -> bool:
        """
        Check whether a simulated file exists.
        """
        return path in self.files

    def directory_exists(self, path: str) -> bool:
        """
        Check whether a simulated directory exists.
        """
        return path in self.directories

    def list_directory(self, path: str) -> List[str]:
        """
        List files and directories directly inside a directory.
        """

        if path not in self.directories:
            return []

        entries = set()

        for directory in self.directories:
            if directory == path:
                continue

            parent = directory.rsplit("/", 1)[0] or "/"

            if parent == path:
                name = directory.rsplit("/", 1)[-1]
                entries.add(name)

        for file_path in self.files:
            parent = file_path.rsplit("/", 1)[0] or "/"

            if parent == path:
                name = file_path.rsplit("/", 1)[-1]
                entries.add(name)

        return sorted(entries)

    def read_file(self, path: str) -> Optional[str]:
        """
        Return the contents of a simulated file.
        """
        file = self.files.get(path)

        if not file:
            return None

        file["accessed"] = True

        return file["content"]

    def was_accessed(self, path: str) -> bool:
        """
        Check whether a simulated file has been accessed.
        """
        file = self.files.get(path)

        if not file:
            return False

        return file.get("accessed", False)
    
    def list_files(self) -> List[str]:
        """
        Return all files in the virtual filesystem.
        """
        return sorted(self.files.keys())

    def get_file_info(self, path: str) -> Optional[Dict]:
        """
        Return metadata about a simulated file.
        """
        return self.files.get(path)

    def create_file(
        self,
        path: str,
        content: str = "",
        sensitive: bool = False
    ) -> bool:
        """
        Create a new simulated file.
        """

        if path in self.files:
            return False

        parent = path.rsplit("/", 1)[0] or "/"

        if parent not in self.directories:
            return False

        self.files[path] = {
            "type": "file",
            "content": content,
            "sensitive": sensitive,
            "accessed": False,
        }

        return True

    def write_file(
        self,
        path: str,
        content: str
    ) -> bool:
        """
        Replace the contents of a simulated file.
        """

        file = self.files.get(path)

        if not file:
            return False

        file["content"] = content

        return True

    def delete_file(self, path: str) -> bool:
        """
        Delete a simulated file.
        """

        if path not in self.files:
            return False

        del self.files[path]

        return True