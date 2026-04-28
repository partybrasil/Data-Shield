"""Main window for Data-Shield GUI with Fluent Design."""

import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMessageBox,
    QSystemTrayIcon, QFileDialog, QLabel
)
from PySide6.QtCore import Qt, QSize, Signal, QTimer, QSettings
from PySide6.QtGui import QIcon, QAction, QColor, QPixmap, QPainter
import psutil
try:
    import GPUtil
except ImportError:
    GPUtil = None

from qfluentwidgets import (
    NavigationItemPosition, FluentWindow, SubtitleLabel, 
    setTheme, Theme, FluentIcon as FIF,
    InfoBar, InfoBarIcon, InfoBarPosition,
    PrimaryPushButton, PushButton, TransparentToolButton
)

from .widgets import ScanPanel, ResultsTable, ProgressWidget, VaultPanel, MonitorPanel, SettingsPanel
from .theme import ThemeManager
from .workers import VaultWorker

class MainWindow(FluentWindow):
    """Main application window using Fluent Design."""

    def __init__(self, scanner=None, vault=None, monitor=None, exporter=None):
        # Persistence MUST be initialized before super().__init__() 
        # because the base class triggers resizeEvent during initialization.
        self.settings = QSettings("DataShield", "SecureScanner")
        
        super().__init__()
        self.scanner = scanner
        self.vault = vault
        self.monitor = monitor
        self.exporter = exporter
        self.last_session_id = None
        self.theme_manager = None

        # Basic setup
        self.setWindowTitle("Data-Shield")
        self.setWindowIcon(QIcon.fromTheme("security-high"))
        
        # Persistence
        self.load_settings()

        # Initialize sub-panels
        self.init_panels()
        
        # Load persisted scan settings into UI
        self.load_scan_settings()
        
        # Setup Navigation
        self.init_navigation()
        
        # System Tray
        self.init_tray()
        
        # Stats Timer
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_title_stats)
        self.stats_timer.start(2000) # Update every 2 seconds
        
        # Apply Dark Theme
        setTheme(Theme.DARK)

    def load_settings(self):
        """Restore window geometry."""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(1100, 800)
            
    def save_settings(self):
        """Save window geometry."""
        self.settings.setValue("geometry", self.saveGeometry())

    def update_title_stats(self):
        """Update window title with system info and dimensions."""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        gpu_str = ""
        if GPUtil:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_str = f" | GPU: {int(gpus[0].load*100)}%"
            except:
                pass
        
        size = self.size()
        stats = f"CPU: {cpu}% | RAM: {ram}%{gpu_str} | Res: {size.width()}x{size.height()}"
        self.setWindowTitle(f"Data-Shield - Premium Security [{stats}]")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_title_stats()
        self.save_settings()

    def moveEvent(self, event):
        super().moveEvent(event)
        self.save_settings()

    def init_panels(self):
        """Initialize all functional panels."""
        # Scanner Panel
        self.scanner_interface = QWidget()
        scan_layout = QVBoxLayout(self.scanner_interface)
        scan_layout.setContentsMargins(30, 30, 30, 30)
        
        self.scan_header = SubtitleLabel("System Security Scan", self.scanner_interface)
        self.scan_panel = ScanPanel()
        self.progress_widget = ProgressWidget()
        self.results_table = ResultsTable()
        
        self.scan_panel.scan_requested.connect(self.start_scan)
        self.scan_panel.stop_requested.connect(self.stop_scan)
        
        scan_layout.addWidget(self.scan_header)
        scan_layout.addWidget(self.scan_panel)
        scan_layout.addWidget(self.progress_widget)
        scan_layout.addWidget(self.results_table)
        self.scanner_interface.setObjectName("scanner_interface")

        # Vault Panel
        self.vault_interface = VaultPanel()
        self.vault_interface.setObjectName("vault_interface")
        self.vault_interface.unlock_requested.connect(self.unlock_vault)
        self.vault_interface.lock_requested.connect(self.lock_vault)

        # Monitor Panel
        self.monitor_interface = MonitorPanel()
        self.monitor_interface.setObjectName("monitor_interface")

        # Settings Panel
        self.settings_interface = SettingsPanel()
        self.settings_interface.setObjectName("settings_interface")
        self.settings_interface.settings_saved.connect(self.save_scan_settings)

    def load_scan_settings(self):
        """Load scan settings from persistence into UI."""
        exclusions = self.settings.value("scan/exclusions", "node_modules, venv, .git, .venv")
        threads = self.settings.value("scan/threads", 4, type=int)
        
        self.settings_interface.exclude_input.setText(exclusions)
        self.settings_interface.threads_spin.setValue(threads)

    def save_scan_settings(self, exclusions_list, threads):
        """Save scan settings from UI to persistence."""
        # Re-get the raw string from input for persistence
        exclusions_str = self.settings_interface.exclude_input.text()
        self.settings.setValue("scan/exclusions", exclusions_str)
        self.settings.setValue("scan/threads", threads)
        InfoBar.success(title="Settings Saved", content="Scan preferences updated and persisted.", parent=self)

    def init_navigation(self):
        """Setup the sidebar navigation."""
        self.addSubInterface(self.scanner_interface, FIF.SEARCH, "Scanner")
        self.addSubInterface(self.vault_interface, FIF.FINGERPRINT, "Vault")
        self.addSubInterface(self.monitor_interface, FIF.PEOPLE, "Monitor")
        
        # Add settings to bottom
        self.addSubInterface(self.settings_interface, FIF.SETTING, "Settings", NavigationItemPosition.BOTTOM)

    def init_tray(self):
        """Initialize system tray icon."""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Fallback icon logic
        icon = QIcon.fromTheme("security-high")
        if icon.isNull():
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setBrush(QColor("#00f2ff"))
            painter.drawEllipse(4, 4, 24, 24)
            painter.end()
            icon = QIcon(pixmap)
            
        self.tray_icon.setIcon(icon)
        
        from PySide6.QtWidgets import QMenu
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

    def start_scan(self, path: str, mode: str):
        """Start a new scan session."""
        from .workers import ScanWorker
        
        excludes = [s.strip() for s in self.settings_interface.exclude_input.text().split(",") if s.strip()]
        self.scanner.config.exclude_dirs = excludes
        self.scanner.config.thread_count = self.settings_interface.threads_spin.value()
        self.scanner.should_stop = False

        self.scan_panel.scan_btn.setEnabled(False)
        self.scan_panel.stop_btn.setEnabled(True)
        self.results_table.clear_results()
        self.progress_widget.update_progress(0, 1)
        
        InfoBar.info(
            title="Scan Started",
            content=f"Scanning directory: {path}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
        
        self.scan_worker = ScanWorker(self.scanner, path, mode)
        self.scan_worker.progress.connect(self.progress_widget.update_progress)
        self.scan_worker.finished.connect(self.on_scan_finished)
        self.scan_worker.error.connect(self.on_scan_error)
        self.scan_worker.start()

    def stop_scan(self):
        if self.scanner:
            self.scanner.stop()
            self.scan_panel.stop_btn.setEnabled(False)
            InfoBar.warning(title="Stopping Scan", content="Scan termination requested...", parent=self)

    def on_scan_finished(self, session_id: str):
        self.last_session_id = session_id
        self.scan_panel.scan_btn.setEnabled(True)
        self.scan_panel.stop_btn.setEnabled(False)
        
        from ..core.findings import FindingService
        session = self.scanner.session_factory()
        try:
            service = FindingService(session)
            findings = service.get_session_findings(session_id)
            for finding in findings:
                self.results_table.add_finding(finding)
        finally:
            session.close()

        InfoBar.success(
            title="Scan Complete",
            content=f"Detected {len(findings)} potential threats.",
            parent=self
        )

    def on_scan_error(self, message: str):
        self.scan_panel.scan_btn.setEnabled(True)
        self.scan_panel.stop_btn.setEnabled(False)
        InfoBar.error(title="Scan Error", content=message, parent=self)

    def unlock_vault(self, password: str):
        self.vault_worker = VaultWorker(self.vault, "unlock", password)
        self.vault_worker.finished.connect(self.on_vault_unlocked)
        self.vault_worker.error.connect(self.on_vault_error)
        self.vault_worker.start()

    def on_vault_unlocked(self):
        self.vault_interface.set_unlocked(True)
        InfoBar.success(title="Vault Unlocked", content="Secure storage is now accessible.", parent=self)

    def on_vault_error(self, message: str):
        InfoBar.error(title="Vault Error", content=message, parent=self)

    def lock_vault(self):
        self.vault.lock()
        self.vault_interface.set_unlocked(False)
        InfoBar.info(title="Vault Locked", content="Secure storage is now encrypted.", parent=self)

    def set_theme_manager(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager

    def closeEvent(self, event):
        """Ensure vault is locked on close."""
        if self.vault:
            self.vault.lock()
        self.tray_icon.hide()
        super().closeEvent(event)
