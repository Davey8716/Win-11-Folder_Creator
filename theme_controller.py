from typing import List
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from styles import THEMES, ACCENT_MAP

class ThemeController:
    def __init__(self, themes: List[str] = THEMES):
        if not themes:
            raise RuntimeError("No qt_material themes available.")

        self.themes = themes
        self.current_index = 0
        self.current_accent = "#2196F3"

    # ---------------------------------------------------------
    # Public
    # ---------------------------------------------------------

    def theme_count(self) -> int:
        return len(self.themes)
    
    def apply_theme(self, index: int) -> str:
        """
        Applies theme and returns accent color.
        """
        self.current_index = index
        theme = self.themes[index]

        app = QApplication.instance()

        apply_stylesheet(app, theme=theme)

        # ------------------------------------------------
        # Disabled button contrast fix (light vs dark)
        # ------------------------------------------------
        if "light" in theme.lower():
            disabled_style = """
            QPushButton:disabled {
                background-color: #d6d6d6;
                color: #8a8a8a;
                border: 1px solid #bdbdbd;
            }
            """
        else:
            disabled_style = """
            QPushButton:disabled {
                background-color: #474747;
                color: #9a9a9a;
                border: 1px solid #5a5a5a;
            }
            """

        app.setStyleSheet(app.styleSheet() + disabled_style)

        accent_key = self._extract_accent_key(theme)
        accent_color = ACCENT_MAP.get(accent_key, "#2196F3")

        self.current_accent = accent_color
        return accent_color

    # ---------------------------------------------------------
    # Internal
    # ---------------------------------------------------------

    def _extract_accent_key(self, theme_name: str) -> str:
        return (
            theme_name
            .replace("light_", "")
            .replace("dark_", "")
            .replace(".xml", "")
        )