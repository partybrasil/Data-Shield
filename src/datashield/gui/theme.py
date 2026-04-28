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
        """Load QSS stylesheets with Neon Dark aesthetic."""
        # Dark Neon theme
        self.styles["dark"] = """
        QMainWindow, QDialog {
            background-color: #0b0e14;
            color: #e0e0e0;
        }
        
        QTabWidget::pane {
            border: 1px solid #1c222d;
            background-color: #0b0e14;
            top: -1px;
        }
        
        QTabBar::tab {
            background-color: #1c222d;
            color: #a0a0a0;
            padding: 10px 20px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #00f2ff;
            color: #0b0e14;
            font-weight: bold;
        }
        
        QTableView {
            background-color: #121820;
            alternate-background-color: #1c222d;
            color: #e0e0e0;
            gridline-color: #2a3442;
            border: none;
            border-radius: 8px;
            selection-background-color: rgba(0, 242, 255, 0.2);
            selection-color: #00f2ff;
        }
        
        QHeaderView::section {
            background-color: #1c222d;
            color: #00f2ff;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
        
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00f2ff, stop:1 #0099ff);
            color: #0b0e14;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 13px;
        }
        
        QPushButton:hover {
            background-color: #00ffff;
            border: 1px solid #ffffff;
        }
        
        QPushButton#secondary {
            background-color: transparent;
            border: 1px solid #00f2ff;
            color: #00f2ff;
        }
        
        QLineEdit {
            background-color: #1c222d;
            border: 1px solid #2a3442;
            border-radius: 4px;
            padding: 8px;
            color: #ffffff;
        }
        
        QLineEdit:focus {
            border: 1px solid #00f2ff;
        }
        
        QProgressBar {
            border: 1px solid #2a3442;
            border-radius: 5px;
            text-align: center;
            background-color: #1c222d;
            color: white;
        }
        
        QProgressBar::chunk {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f2ff, stop:1 #00ffaa);
            border-radius: 4px;
        }
        
        QStatusBar {
            background-color: #1c222d;
            color: #00f2ff;
        }
        """

        # Light theme (modernized variant)
        self.styles["light"] = """
        QMainWindow {
            background-color: #f5f7fa;
            color: #1a202c;
        }
        QTableView {
            background-color: #ffffff;
            color: #1a202c;
            gridline-color: #edf2f7;
            border: 1px solid #e2e8f0;
        }
        QPushButton {
            background-color: #3182ce;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
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
