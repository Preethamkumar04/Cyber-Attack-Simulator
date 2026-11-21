from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class InvestigationRecord:
    """
    Stores everything a trainee has investigated
    during one simulation session.
    """

    session_id: int

    commands: List[Dict] = field(default_factory=list)

    discovered_files: List[str] = field(default_factory=list)

    accessed_files: List[str] = field(default_factory=list)

    discovered_directories: List[str] = field(default_factory=list)

    findings: List[Dict] = field(default_factory=list)

    artifacts_inspected: List[str] = field(default_factory=list)

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    def record_command(
        self,
        command: str,
        output: str = "",
        exit_code: int = 0,
    ) -> None:

        self.commands.append(
            {
                "command": command,
                "output": output,
                "exit_code": exit_code,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def record_discovered_file(
        self,
        file_path: str,
    ) -> None:

        if file_path not in self.discovered_files:
            self.discovered_files.append(file_path)

    def record_accessed_file(
        self,
        file_path: str,
    ) -> None:

        if file_path not in self.accessed_files:
            self.accessed_files.append(file_path)

    def record_discovered_directory(
        self,
        directory_path: str,
    ) -> None:

        if directory_path not in self.discovered_directories:
            self.discovered_directories.append(
                directory_path
            )

    def record_finding(
        self,
        finding: str,
        source: Optional[str] = None,
    ) -> None:

        self.findings.append(
            {
                "finding": finding,
                "source": source,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def record_artifact_inspected(self, artifact_type: str) -> None:
        if artifact_type not in self.artifacts_inspected:
            self.artifacts_inspected.append(artifact_type)

    def summary(self) -> Dict:

        return {
            "session_id": self.session_id,
            "commands": list(self.commands),
            "discovered_files": list(
                self.discovered_files
            ),
            "accessed_files": list(
                self.accessed_files
            ),
            "discovered_directories": list(
                self.discovered_directories
            ),
            "findings": list(self.findings),
            "artifacts_inspected": list(self.artifacts_inspected),
        }


class InvestigationTracker:
    """
    Manages investigation records for active
    training sessions.
    """

    def __init__(self):
        self.records: Dict[
            int,
            InvestigationRecord
        ] = {}

    def create_session(
        self,
        session_id: int,
    ) -> InvestigationRecord:

        record = InvestigationRecord(
            session_id=session_id
        )

        self.records[session_id] = record

        return record

    def get_session(
        self,
        session_id: int,
    ) -> Optional[InvestigationRecord]:

        return self.records.get(session_id)

    def get_or_create_session(
        self,
        session_id: int,
    ) -> InvestigationRecord:

        record = self.get_session(session_id)

        if record is not None:
            return record

        return self.create_session(session_id)

    def remove_session(
        self,
        session_id: int,
    ) -> None:

        self.records.pop(
            session_id,
            None
        )

    def clear_all(self) -> None:

        self.records.clear()


investigation_tracker = InvestigationTracker()
