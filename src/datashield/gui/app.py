"""PySide6 application initialization."""

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSize
from .main_window import MainWindow
from .theme import ThemeManager
import sys


class GuiApp:
    """Data-Shield GUI Application."""

    def __init__(self, scanner=None, vault=None, monitor=None, exporter=None, session_factory=None):
        """Initialize GUI application."""
        self.app = QApplication(sys.argv)
        
        # Show Splash Screen
        from .widgets import SplashScreen
        from PySide6.QtCore import QTimer
        
        self.splash = SplashScreen()
        self.splash.show()
        self.app.processEvents()
        
        # Initialize Main Window (while splash is showing)
        self.main_window = MainWindow(scanner, vault, monitor, exporter, session_factory)
        
        # Wait a bit so the splash is visible
        QTimer.singleShot(2500, self._finish_initialization)

    def _finish_initialization(self):
        """Close splash and show main window."""
        self.main_window.show()
        self.splash.close()

    def run(self):
        """Run the application.

        Returns:
            Exit code
        """
        return self.app.exec()

    def quit(self):
        """Quit the application."""
        self.app.quit()
