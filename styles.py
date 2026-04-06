import qt_material
from pathlib import Path

def get_available_qt_material_themes(preferred: list[str]) -> list[str]:
    themes_dir = Path(qt_material.__file__).parent / "themes"
    existing = {p.name for p in themes_dir.glob("*.xml")}
    return [t for t in preferred if t in existing]


ACCENT_MAP = {
    "red": "#D64545",        # softened red (less neon)
    "orange": "#E6892E",     # warmer, less bright
    "amber": "#D4A017",      # toned-down amber
    "green": "#2DBE7E",      # softened mint green
    "teal": "#1FB5A3",       # calmer teal
    "blue": "#3F6DF6",       # slightly softened blue
    "purple": "#8E44AD",     # richer but less bright purple
    "pink": "#D65C9E",       # muted rose pink
 
}

PREFERRED_THEMES = [
    
    # Light
    "light_red.xml",
    "light_pink.xml",
    "light_purple.xml",
    "light_blue.xml",
    "light_teal.xml",
    "light_green.xml",

    # Dark
    "dark_red.xml",
    "dark_pink.xml",
    "dark_purple.xml",
    "dark_blue.xml",
    "dark_teal.xml",
    "dark_green.xml",
]

THEMES = get_available_qt_material_themes(PREFERRED_THEMES)