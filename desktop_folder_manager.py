from pathlib import Path
from datetime import datetime
from typing import Literal, Tuple,Optional, Tuple

TimestampMode = Literal["ISO", "UK", "US", None]

class DesktopFolderManager:
    def __init__(self):
        self.desktop_path = Path.home() / "Desktop"

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def create_folder(
        self,
        base_name: str,
        timestamp_mode: Optional[TimestampMode] = None,
    ) -> Tuple[str, str]:
        """
        Returns (status_code, message)

        status_code:
            "success"
            "exists"
            "invalid"
            "error"
        """

        name = self.apply_timestamp(base_name, timestamp_mode)

        if not name:
            return "invalid", "No folder name was entered."

        new_path = self.desktop_path / name

        try:
            new_path.mkdir(exist_ok=False)
            return "success", f'The folder "{name}" was created on Desktop.'

        except FileExistsError:
            return "exists", "Folder already exists on desktop."

        except Exception:
            return "error", "Error creating folder"

    # ---------------------------------------------------------
    # Shared helpers
    # ---------------------------------------------------------

    def apply_timestamp(
        self,
        base_name: str,
        timestamp_mode: Optional[TimestampMode],
    ) -> str:

        name = base_name.strip()

        if not name:
            return ""

        if timestamp_mode:
            stamp = self.build_timestamp(timestamp_mode)
            if stamp:
                name = f"{name}_{stamp}"

        return name

    def build_timestamp(self, mode: TimestampMode) -> str:
        now = datetime.now()

        if mode == "ISO":
            return now.strftime("%Y-%m-%d")

        if mode == "UK":
            return now.strftime("%d-%m-%Y")

        if mode == "US":
            return now.strftime("%m-%d-%Y")

        return ""