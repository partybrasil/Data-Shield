"""Theme management for PySide6 GUI."""

from pathlib import Path
from typing import Optional


class ThemeManager:
    """Manage dark/light theme switching."""

    def __init__(self, app):
        """Initialize theme manager.

        Args:
            app: QApplication instance
        """
        self.app = app
        self.current_theme = "dark"
        self.styles = {}
        self._load_styles()

    def _load_styles(self):
        """Load QSS stylesheets."""
        # Dark theme
        self.styles["dark"] = """
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QTableView {
            background-color: #252526;
            color: #ffffff;
            gridline-color: #3e3e42;
        }
        QPushButton {
            background-color: #0e639c;
            color: white;
            border: none;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #1177bb;
        }
        """

        # Light theme
        self.styles["light"] = """
        QMainWindow {
            background-color: #ffffff;
            color: #000000;
        }
        QTableView {
            background-color: #ffffff;
            color: #000000;
            gridline-color: #e0e0e0;
        }
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #1084d7;
        }
        """

    def set_theme(self, theme: str):
        """Set application theme.

        Args:
            theme: 'dark' or 'light'
        """
        if theme in self.styles:
            self.current_theme = theme
            self.app.setStyleSheet(self.styles[theme])

    def toggle_theme(self):
        """Toggle between dark and light theme."""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.set_theme(new_theme)

    def get_current_theme(self) -> str:
        """Get current theme name."""
        return self.current_theme
