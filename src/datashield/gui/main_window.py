"""Main window for Data-Shield GUI."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QStatusBar, QMenuBar, QMenu, QMessageBox,
    QSystemTrayIcon, QFileDialog
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction
from .widgets import ScanPanel, ResultsTable, ProgressWidget, VaultPanel, MonitorPanel, SettingsPanel
from .theme import ThemeManager
from .workers import VaultWorker

class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, scanner=None, vault=None, monitor=None, exporter=None):
        super().__init__()
        self.scanner = scanner
        self.vault = vault
        self.monitor = monitor
        self.exporter = exporter
        self.last_session_id = None

        self.setWindowTitle("Data-Shield - Credential Security Tool")
        self.setWindowIcon(QIcon.fromTheme("security-high"))
        self.setGeometry(100, 100, 1200, 750)

        self.theme_manager = None
        self.init_ui()
        self.create_menu_bar()
        self.init_tray()

    def init_ui(self):
        """Initialize user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()

        # Scan tab
        self.scan_panel = ScanPanel()
        self.progress_widget = ProgressWidget()
        self.results_table = ResultsTable()
        self.scan_panel.scan_requested.connect(self.start_scan)
        self.scan_panel.stop_requested.connect(self.stop_scan)

        scan_layout = QVBoxLayout()
        scan_layout.addWidget(self.scan_panel)
        scan_layout.addWidget(self.progress_widget)
        scan_layout.addWidget(self.results_table)
        scan_tab = QWidget()
        scan_tab.setLayout(scan_layout)
        self.tabs.addTab(scan_tab, "Scanner")

        # Vault tab
        self.vault_panel = VaultPanel()
        self.vault_panel.unlock_requested.connect(self.unlock_vault)
        self.vault_panel.lock_requested.connect(self.lock_vault)
        self.tabs.addTab(self.vault_panel, "Vault")

        # Monitor tab
        self.monitor_panel = MonitorPanel()
        self.tabs.addTab(self.monitor_panel, "Monitor")

        # Settings tab
        self.settings_panel = SettingsPanel()
        self.tabs.addTab(self.settings_panel, "Settings")

        main_layout.addWidget(self.tabs)
        self.statusBar().showMessage("Ready")
        central_widget.setLayout(main_layout)
        self.create_toolbar()

    def init_tray(self):
        """Initialize system tray icon."""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Fallback icon if theme is missing
        icon = QIcon.fromTheme("security-high")
        if icon.isNull():
            # Create a simple colored icon if theme icon not found
            from PySide6.QtGui import QPixmap, QPainter, QColor
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setBrush(QColor("#00f2ff"))
            painter.drawEllipse(4, 4, 24, 24)
            painter.end()
            icon = QIcon(pixmap)
            
        self.tray_icon.setIcon(icon)
        
        tray_menu = QMenu()
        restore_action = tray_menu.addAction("Restore Window")
        restore_action.triggered.connect(self.showNormal)
        
        minimize_action = tray_menu.addAction("Minimize to Tray")
        minimize_action.triggered.connect(self.hide)
        
        tray_menu.addSeparator()
        exit_action = tray_menu.addAction("Exit Securely")
        exit_action.triggered.connect(self.close)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def stop_scan(self):
        """Handle stop scan request."""
        if self.scanner:
            self.scanner.stop()
            self.statusBar().showMessage("Stopping scan...")
            self.scan_panel.stop_btn.setEnabled(False)

    def start_scan(self, path: str, mode: str):
        """Start a new scan session."""
        from .workers import ScanWorker
        
        # Apply settings from settings panel
        excludes = [s.strip() for s in self.settings_panel.exclude_input.text().split(",") if s.strip()]
        self.scanner.config.exclude_dirs = excludes
        self.scanner.config.thread_count = self.settings_panel.threads_spin.value()
        self.scanner.should_stop = False # Reset stop flag

        self.scan_panel.scan_btn.setEnabled(False)
        self.scan_panel.stop_btn.setEnabled(True)
        self.results_table.clear_results()
        self.progress_widget.update_progress(0, 1)
        self.statusBar().showMessage("Scanning...")
        
        self.last_session_id = None # Reset last session ID
        self.scan_worker = ScanWorker(self.scanner, path, mode)
        self.scan_worker.progress.connect(self.progress_widget.update_progress)
        self.scan_worker.finished.connect(self.on_scan_finished)
        self.scan_worker.error.connect(self.on_scan_error)
        self.scan_worker.start()

    def on_scan_finished(self, session_id: str):
        """Handle scan completion."""
        self.last_session_id = session_id
        self.scan_panel.scan_btn.setEnabled(True)
        self.scan_panel.stop_btn.setEnabled(False)
        from ..core.findings import FindingService
        
        self.statusBar().showMessage(f"Scan finished. Session: {session_id}")
        
        # Load findings from database
        session = self.scanner.session_factory()
        try:
            service = FindingService(session)
            findings = service.get_session_findings(session_id)
            
            for finding in findings:
                self.results_table.add_finding(finding)
        finally:
            session.close()

    def on_scan_error(self, message: str):
        """Handle scan error."""
        self.scan_panel.scan_btn.setEnabled(True)
        self.scan_panel.stop_btn.setEnabled(False)
        self.statusBar().showMessage(f"Scan error: {message}")
        QMessageBox.critical(self, "Scan Error", message)

    def create_toolbar(self):
        """Create main toolbar."""
        from PySide6.QtCore import QSize
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))

        export_json = QAction("Export JSON", self)
        export_json.triggered.connect(lambda: self.export_results("json"))
        toolbar.addAction(export_json)

        export_csv = QAction("Export CSV", self)
        export_csv.triggered.connect(lambda: self.export_results("csv"))
        toolbar.addAction(export_csv)

    def unlock_vault(self, password: str):
        """Handle vault unlock request."""
        self.statusBar().showMessage("Unlocking vault...")
        self.vault_worker = VaultWorker(self.vault, "unlock", password)
        self.vault_worker.finished.connect(self.on_vault_unlocked)
        self.vault_worker.error.connect(self.on_vault_error)
        self.vault_worker.start()

    def lock_vault(self):
        """Handle vault lock request."""
        self.vault.lock()
        self.vault_panel.set_unlocked(False)
        self.statusBar().showMessage("Vault locked")

    def on_vault_unlocked(self):
        """Handle successful vault unlock."""
        self.vault_panel.set_unlocked(True)
        self.statusBar().showMessage("Vault unlocked")

    def on_vault_error(self, message: str):
        """Handle vault operation error."""
        self.statusBar().showMessage(f"Vault error: {message}")
        QMessageBox.warning(self, "Vault Error", message)

    def export_results(self, format_name: str):
        """Export scan results."""
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "Export", "No results to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "", f"{format_name.upper()} Files (*.{format_name})"
        )
        
        if file_path:
            try:
                from ..core.findings import FindingService
                findings = []
                if self.last_session_id:
                    session = self.scanner.session_factory()
                    try:
                        service = FindingService(session)
                        findings = service.get_session_findings(self.last_session_id)
                    finally:
                        session.close()
                
                self.exporter.export(file_path, format_name, findings)
                QMessageBox.information(self, "Export", f"{len(findings)} results exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

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
