"""PySide6 application initialization."""

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSize
from .main_window import MainWindow
from .theme import ThemeManager
import sys


class GuiApp:
    """Data-Shield GUI Application."""

    def __init__(self, scanner=None, vault=None, monitor=None, exporter=None):
        """Initialize GUI application.

        Args:
            scanner: Scanner instance
            vault: Vault instance
            monitor: Monitor instance
            exporter: Exporter instance
        """
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow(scanner, vault, monitor, exporter)
        self.theme_manager = ThemeManager(self.app)
        self.main_window.set_theme_manager(self.theme_manager)

    def run(self):
        """Run the application.

        Returns:
            Exit code
        """
        self.main_window.show()
        return self.app.exec()

    def quit(self):
        """Quit the application."""
        self.app.quit()
