from pathlib import Path
from datetime import datetime
from typing import Literal, Tuple

TimestampMode = Literal["ISO", "UK", "US", None]

class DesktopFolderService:
    def __init__(self):
        self.desktop_path = Path.home() / "Desktop"

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def create_folder(
        self,
        base_name: str,
        timestamp_mode: TimestampMode = None,
    ) -> Tuple[str, str]:
        """
        Returns (status_code, message)

        status_code:
            "success"
            "exists"
            "invalid"
            "error"
        """

        name = base_name.strip()

        if not name:
            return "invalid", "No folder name was entered."

        if timestamp_mode:
            stamp = self._build_timestamp(timestamp_mode)
            if stamp:
                name = f"{name}_{stamp}"

        new_path = self.desktop_path / name

        try:
            new_path.mkdir(exist_ok=False)
            return "success", f'The folder "{name}" was created on Desktop.'

        except FileExistsError:
            return "exists", "Folder already exists."

        except Exception:
            return "error", "Error creating folder"

    # ---------------------------------------------------------
    # Internal
    # ---------------------------------------------------------

    def _build_timestamp(self, mode: TimestampMode) -> str:
        now = datetime.now()

        if mode == "ISO":
            return now.strftime("%Y-%m-%d")

        if mode == "UK":
            return now.strftime("%d-%m-%Y")

        if mode == "US":
            return now.strftime("%m-%d-%Y")

        return ""