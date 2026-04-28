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
            background-color: #05070a;
            color: #e0e0e0;
        }
        
        QTabWidget::pane {
            border: 2px solid #00f2ff;
            background-color: #0b0e14;
            top: -2px;
            border-radius: 4px;
        }
        
        QTabBar::tab {
            background-color: #121820;
            color: #00f2ff;
            padding: 12px 25px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 5px;
            font-weight: bold;
            border: 1px solid #1c222d;
        }
        
        QTabBar::tab:selected {
            background-color: #00f2ff;
            color: #05070a;
            border: 2px solid #ffffff;
        }
        
        QTableView {
            background-color: #0b0e14;
            alternate-background-color: #121820;
            color: #00f2ff;
            gridline-color: #00f2ff;
            border: 1px solid #00f2ff;
            border-radius: 10px;
            selection-background-color: rgba(0, 242, 255, 0.3);
            selection-color: #ffffff;
        }
        
        QHeaderView::section {
            background-color: #121820;
            color: #00ffaa;
            padding: 10px;
            border: 1px solid #1c222d;
            font-weight: bold;
            font-size: 14px;
        }
        
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00f2ff, stop:1 #0044ff);
            color: #ffffff;
            border: 2px solid #00f2ff;
            padding: 12px 25px;
            border-radius: 10px;
            font-weight: bold;
            font-size: 14px;
            text-transform: uppercase;
        }
        
        QPushButton:hover {
            background-color: #00ffff;
            color: #000000;
            border: 2px solid #ffffff;
        }
        
        QPushButton#secondary {
            background-color: transparent;
            border: 2px solid #ff3e3e;
            color: #ff3e3e;
        }
        
        QPushButton#secondary:hover {
            background-color: #ff3e3e;
            color: #ffffff;
        }
        
        QLineEdit {
            background-color: #121820;
            border: 2px solid #1c222d;
            border-radius: 8px;
            padding: 10px;
            color: #00f2ff;
            font-size: 13px;
        }
        
        QLineEdit:focus {
            border: 2px solid #00f2ff;
            background-color: #05070a;
        }
        
        QProgressBar {
            border: 2px solid #00f2ff;
            border-radius: 10px;
            text-align: center;
            background-color: #05070a;
            color: #ffffff;
            font-weight: bold;
            height: 30px;
        }
        
        QProgressBar::chunk {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f2ff, stop:1 #00ffaa);
            border-radius: 8px;
        }
        
        QStatusBar {
            background-color: #0b0e14;
            color: #00f2ff;
            border-top: 1px solid #00f2ff;
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
