from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class WebsiteState:
    """
    Represents the state of the simulated web application.

    This is entirely in-memory and does not interact with
    any real website or server.
    """

    website_status: str = "online"

    login_status: str = "normal"

    authentication_status: str = "normal"

    admin_panel_status: str = "locked"

    database_status: str = "normal"

    file_upload_status: str = "enabled"

    compromised_accounts: List[str] = field(
        default_factory=list
    )

    malicious_files: List[str] = field(
        default_factory=list
    )

    def compromise_account(
        self,
        username: str
    ) -> None:
        """
        Mark a website account as compromised.
        """

        if username not in self.compromised_accounts:
            self.compromised_accounts.append(username)

    def enable_admin_access(self) -> None:
        """
        Simulate successful administrative access.
        """

        self.admin_panel_status = "accessible"

    def compromise_authentication(self) -> None:
        """
        Mark the authentication system as compromised.
        """

        self.authentication_status = "compromised"

    def compromise_database(self) -> None:
        """
        Mark the application's database as compromised.
        """

        self.database_status = "compromised"

    def disable_file_uploads(self) -> None:
        """
        Disable application file uploads.
        """

        self.file_upload_status = "disabled"

    def add_malicious_file(
        self,
        file_path: str
    ) -> None:
        """
        Record a malicious file introduced into
        the simulated website environment.
        """

        if file_path not in self.malicious_files:
            self.malicious_files.append(file_path)

    def take_offline(self) -> None:
        """
        Mark the simulated website as offline.
        """

        self.website_status = "offline"

    def summary(self) -> Dict:
        """
        Return the current website state.
        """

        return {
            "website_status": self.website_status,
            "login_status": self.login_status,
            "authentication_status": self.authentication_status,
            "admin_panel_status": self.admin_panel_status,
            "database_status": self.database_status,
            "file_upload_status": self.file_upload_status,
            "compromised_accounts": list(
                self.compromised_accounts
            ),
            "malicious_files": list(
                self.malicious_files
            ),
            
        }