from dataclasses import dataclass, field
from typing import Dict, List

from app.services.simulator.virtual_filesystem import (
    VirtualFilesystem,
)
from app.services.simulator.website_state import WebsiteState
@dataclass
class SimulationState:
    """
    Stores the current state of one cyber attack simulation.
    """

    filesystem: VirtualFilesystem = field(
        default_factory=VirtualFilesystem
    )
    current_directory: str = "/home/j.smith"
    
    website: WebsiteState = field(
        default_factory=WebsiteState
    )
    # Identity of the attacker
    attacker_ip: str = "10.10.10.50"
    attacker_hostname: str = "ATTACKER-01"

    # Identity of the target environment
    target_ip: str = "10.10.10.20"
    target_hostname: str = "WEB-SERVER"

    # Things discovered or changed during the attack
    compromised_accounts: List[str] = field(default_factory=list)
    compromised_hosts: List[str] = field(default_factory=list)
    discovered_services: List[str] = field(default_factory=list)
    accessed_files: List[str] = field(default_factory=list)
    discovered_files: List[str] = field(
        default_factory=list
    )
    discovered_directories: List[str] = field(
        default_factory=list
    )
    affected_files: List[str] = field(default_factory=list)
    executed_commands: List[str] = field(default_factory=list)
    network_connections: List[Dict] = field(default_factory=list)

    # Attack stages that have occurred
    attack_events: List[Dict] = field(default_factory=list)

    # Current privilege level
    privilege_level: str = "user"

    # Whether important attack conditions have occurred
    malware_executed: bool = False
    files_affected: bool = False
    data_exfiltrated: bool = False
    persistence_established: bool = False
    c2_established: bool = False

    def record_event(self, event: Dict) -> None:
        """
        Store an attack event in the simulation history.
        """
        self.attack_events.append(event)

    def compromise_account(self, account: str) -> None:
        """
        Mark an account as compromised.
        """
        if account not in self.compromised_accounts:
            self.compromised_accounts.append(account)

    def compromise_host(self, host: str) -> None:
        """
        Mark a host as compromised.
        """
        if host not in self.compromised_hosts:
            self.compromised_hosts.append(host)

    def discover_service(self, service: str) -> None:
        """
        Record a discovered service.
        """
        if service not in self.discovered_services:
            self.discovered_services.append(service)

    def discover_directory(self, directory_path: str) -> None:
        """
        Record a directory discovered during investigation.
        """
        if not self.filesystem.directory_exists(directory_path):
            return

        if directory_path not in self.discovered_directories:
            self.discovered_directories.append(directory_path)

    def access_file(self, file_path: str) -> None:
        """
        Record access to a simulated file.
        """
        if not self.filesystem.file_exists(file_path):
            return
        
        if file_path not in self.accessed_files:
            self.accessed_files.append(file_path)

    def discover_file(self, file_path: str) -> None:
        """
        Record a file discovered during investigation.
        """
        if not self.filesystem.file_exists(file_path):
            return

        if file_path not in self.discovered_files:
            self.discovered_files.append(file_path)

    def affect_file(self, file_path: str) -> None:
        """
        Record a file that was modified or affected by an attack.
        """
        if file_path not in self.affected_files:
            self.affected_files.append(file_path)

    def record_command(self, command: str) -> None:
        """
        Record a command executed during the simulation.
        """
        self.executed_commands.append(command)

    def record_network_connection(
        self,
        connection: Dict
    ) -> None:
        """
        Record a simulated network connection.
        """
        self.network_connections.append(connection)

    def escalate_privileges(
        self,
        level: str = "admin"
    ) -> None:
        """
        Update the current privilege level.
        """
        self.privilege_level = level

    def apply_event(self, event: Dict) -> None:
        """
        Apply the effects of an attack event
        to the current simulation state.
        """

        event_type = event.get(
            "event_type",
            ""
        )

        if event_type == "reconnaissance":
            self.discover_service(
                "network_services"
            )

        elif event_type == "credential_access":
            self.compromise_account(
                "j.smith"
            )
            self.website.compromise_account("j.smith")
            self.website.compromise_authentication()

        elif event_type == "privilege_escalation":
            self.escalate_privileges(
                "admin"
            )
            self.website.enable_admin_access()

        elif event_type == "lateral_movement":
            self.compromise_host(
                "INTERNAL-SERVER"
            )

        elif event_type == "malware_execution":
            self.malware_executed = True

            self.filesystem.create_file(
                "/tmp/payload.exe",
                "SIMULATED_MALWARE_PAYLOAD",
                sensitive=True
            )

            self.website.add_malicious_file(
                "/tmp/payload.exe"
            )

        elif event_type == "ransomware_execution":
            self.files_affected = True

            self.filesystem.write_file(
                "/data/employee_records.csv",
                "ENCRYPTED_BY_RANSOMWARE"
            )

            self.filesystem.write_file(
                "/data/financial_report.txt",
                "ENCRYPTED_BY_RANSOMWARE"
            )

            self.affect_file(
                "/data/employee_records.csv"
            )

            self.affect_file(
                "/data/financial_report.txt"
            )

        elif event_type == "data_exfiltration":
            self.access_file(
                "/data/employee_records.csv"
            )
            self.data_exfiltrated = True

            self.website.compromise_database()

        elif event_type == "persistence":
            self.persistence_established = True

            self.filesystem.create_file(
                "/etc/persistence.conf",
                "SIMULATED_PERSISTENCE_ENTRY",
                sensitive=True
            )

        elif event_type == "command_and_control":
            self.c2_established = True

            self.record_network_connection(
                {
                    "src_ip": self.attacker_ip,
                    "dst_ip": "203.0.113.50",
                    "protocol": "HTTPS",
                    "port": 443,
                    "connection_type": "simulated_c2",
                }
            )

        event_record = event.copy()

        event_record["state_snapshot"] = {
            "privilege_level": self.privilege_level,
            "malware_executed": self.malware_executed,
            "files_affected": self.files_affected,
            "data_exfiltrated": self.data_exfiltrated,
            "persistence_established": self.persistence_established,
            "c2_established": self.c2_established,
        }

        self.record_event(event_record)

    def summary(self) -> Dict:
        """
        Return a compact summary of the current simulation state.
        """
        return {
            "attacker_ip": self.attacker_ip,
            "attacker_hostname": self.attacker_hostname,
            "target_ip": self.target_ip,
            "target_hostname": self.target_hostname,

            "compromised_accounts": self.compromised_accounts.copy(),
            "compromised_hosts": self.compromised_hosts.copy(),
            "discovered_services": self.discovered_services.copy(),
            
            "discovered_directories": self.discovered_directories.copy(),
            "accessed_files": self.accessed_files.copy(),
            "discovered_files": self.discovered_files.copy(),
            "affected_files": self.affected_files.copy(),

            "executed_commands": self.executed_commands.copy(),
            "network_connections": self.network_connections.copy(),

            "privilege_level": self.privilege_level,
            "malware_executed": self.malware_executed,
            "files_affected": self.files_affected,
            "data_exfiltrated": self.data_exfiltrated,
            "persistence_established": self.persistence_established,
            "c2_established": self.c2_established,
            "website": self.website.summary(),
        }