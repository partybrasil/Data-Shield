"""Main window for Data-Shield GUI."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QStatusBar, QMenuBar, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction

from .widgets import ScanPanel, ResultsTable, ProgressWidget, VaultPanel
from .theme import ThemeManager
from .workers import VaultWorker


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, scanner=None, vault=None, monitor=None, exporter=None):
        """Initialize main window.

        Args:
            scanner: Scanner instance
            vault: Vault instance
            monitor: Monitor instance
            exporter: Exporter instance
        """
        super().__init__()
        self.scanner = scanner
        self.vault = vault
        self.monitor = monitor
        self.exporter = exporter

        self.setWindowTitle("Data-Shield - Credential Security Tool")
        self.setGeometry(100, 100, 1200, 700)

        self.theme_manager = None
        self.init_ui()
        self.create_menu_bar()

    def init_ui(self):
        """Initialize user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()

        # Create tabs
        tabs = QTabWidget()

        # Scan tab
        self.scan_panel = ScanPanel()
        self.progress_widget = ProgressWidget()
        self.results_table = ResultsTable()

        # Connect scan signals
        self.scan_panel.scan_requested.connect(self.start_scan)

        scan_layout = QVBoxLayout()
        scan_layout.addWidget(self.scan_panel)
        scan_layout.addWidget(self.progress_widget)
        scan_layout.addWidget(self.results_table)

        scan_tab = QWidget()
        scan_tab.setLayout(scan_layout)
        tabs.addTab(scan_tab, "Scanner")

        # Vault tab
        self.vault_panel = VaultPanel()
        vault_tab = QWidget()
        vault_layout = QVBoxLayout()
        vault_layout.addWidget(self.vault_panel)
        vault_tab.setLayout(vault_layout)
        tabs.addTab(vault_tab, "Vault")

        # Add tabs to main layout
        main_layout.addWidget(tabs)

        # Status bar
        self.statusBar().showMessage("Ready")

        central_widget.setLayout(main_layout)

    def start_scan(self, path: str, mode: str):
        """Start a new scan session.
        
        Args:
            path: Directory to scan
            mode: Scan mode
        """
        from .workers import ScanWorker
        
        self.results_table.clear_results()
        self.progress_widget.update_progress(0, 1)
        self.statusBar().showMessage("Scanning...")
        
        self.scan_worker = ScanWorker(self.scanner, path, mode)
        self.scan_worker.progress.connect(self.progress_widget.update_progress)
        self.scan_worker.finished.connect(self.on_scan_finished)
        self.scan_worker.error.connect(self.on_scan_error)
        self.scan_worker.start()

    def on_scan_finished(self, session_id: str):
        """Handle scan completion."""
        from ..core.findings import FindingService
        
        self.statusBar().showMessage(f"Scan finished. Session: {session_id}")
        
        # Load findings from database
        service = FindingService(self.scanner.session)
        findings = service.get_session_findings(session_id)
        
        for finding in findings:
            self.results_table.add_finding(finding)

    def on_scan_error(self, message: str):
        """Handle scan error."""
        self.statusBar().showMessage(f"Scan error: {message}")
        QMessageBox.critical(self, "Scan Error", message)

    def create_menu_bar(self):
        """Create application menu bar."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        # View menu
        view_menu = menu_bar.addMenu("View")
        theme_action = view_menu.addAction("Toggle Theme")
        theme_action.triggered.connect(self.toggle_theme)

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)

    def toggle_theme(self):
        """Toggle application theme."""
        if self.theme_manager:
            self.theme_manager.toggle_theme()

    def show_about(self):
        """Show about dialog."""
        QMessageBox.information(
            self,
            "About Data-Shield",
            "Data-Shield v0.2.0\n\n"
            "Sensitive credential scanner and encryption vault for Windows.\n\n"
            "© 2026 Data-Shield Team"
        )

    def set_theme_manager(self, theme_manager: ThemeManager):
        """Set theme manager instance.

        Args:
            theme_manager: ThemeManager instance
        """
        self.theme_manager = theme_manager
