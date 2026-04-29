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
import shutil
import sys
from types import ModuleType

# Mock distutils for GPUtil (Python 3.12+ compatibility)
if 'distutils' not in sys.modules:
    try:
        import distutils
    except ImportError:
        distutils = ModuleType('distutils')
        spawn = ModuleType('distutils.spawn')
        spawn.find_executable = shutil.which
        distutils.spawn = spawn
        sys.modules['distutils'] = distutils
        sys.modules['distutils.spawn'] = spawn

try:
    import GPUtil
except Exception:
    GPUtil = None

from qfluentwidgets import (
    NavigationItemPosition, FluentWindow, SubtitleLabel, 
    setTheme, Theme, FluentIcon as FIF,
    InfoBar, InfoBarIcon, InfoBarPosition,
    PrimaryPushButton, PushButton, TransparentToolButton,
    StrongBodyLabel, BodyLabel, ComboBox
)

from .widgets import ScanPanel, ResultsTable, ProgressWidget, VaultPanel, MonitorPanel, SettingsPanel
from .theme import ThemeManager
from .workers import VaultWorker

class MainWindow(FluentWindow):
    """Main application window using Fluent Design."""

    def __init__(self, scanner=None, vault=None, monitor=None, exporter=None, session_factory=None):
        # Persistence MUST be initialized before super().__init__() 
        # because the base class triggers resizeEvent during initialization.
        self.settings = QSettings("DataShield", "SecureScanner")
        
        super().__init__()
        self.scanner = scanner
        self.vault = vault
        self.monitor = monitor
        self.exporter = exporter
        self.session_factory = session_factory
        self.last_session_id = None
        self.theme_manager = None
        self._initialized = False
        
        # Timer for debounced persistence
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self._actual_save_settings)

        # Basic setup
        self.setWindowTitle("Data-Shield")
        self.setWindowIcon(QIcon.fromTheme("security-high"))
        
        # Persistence - Delay restoration to ensure OS window manager is ready
        QTimer.singleShot(100, self.load_settings)

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
        
        self._initialized = True

    def load_settings(self):
        """Restore window geometry."""
        geometry = self.settings.value("geometry")
        
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(1100, 800)
            
    def save_settings(self):
        """Debounce save operation."""
        if getattr(self, "_initialized", False) and self.isVisible():
            self.save_timer.start(500) # Save 500ms after last change

    def _actual_save_settings(self):
        """Perform the actual save to disk."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.sync()

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
        self.results_table = ResultsTable() # Initialize FIRST
        
        # Results Section with Discrete Filter
        results_header_layout = QHBoxLayout()
        results_header_layout.setContentsMargins(0, 10, 0, 0)
        
        self.results_label = StrongBodyLabel("Scan Findings")
        
        self.type_filter_combo = ComboBox()
        self.type_filter_combo.setPlaceholderText("Filter by type...")
        self.type_filter_combo.addItem("All Types")
        self.type_filter_combo.setFixedWidth(200)
        self.type_filter_combo.currentTextChanged.connect(self.results_table.set_filter)
        
        results_header_layout.addWidget(self.results_label)
        results_header_layout.addStretch()
        results_header_layout.addWidget(BodyLabel("Filter:"))
        results_header_layout.addWidget(self.type_filter_combo)
        
        self.scanner_interface.setObjectName("scanner_interface")
        
        self.scan_panel.scan_requested.connect(self.start_scan)
        self.scan_panel.stop_requested.connect(self.stop_scan)
        
        scan_layout.addWidget(self.scan_header)
        scan_layout.addWidget(self.scan_panel)
        scan_layout.addWidget(self.progress_widget)
        scan_layout.addLayout(results_header_layout)
        scan_layout.addWidget(self.results_table)
        
        self.results_table.save_to_vault_requested.connect(self.save_copy_to_vault)
        self.results_table.open_explorer_requested.connect(self.open_in_explorer)
        self.results_table.view_details_requested.connect(self.view_details)
        
        self.found_types = set()

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
        
        # Reset filter
        self.found_types = set()
        self.type_filter_combo.clear()
        self.type_filter_combo.addItem("All Types")
        self.type_filter_combo.setCurrentText("All Types")
        
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
        self.scan_worker.finding_discovered.connect(self.on_finding_discovered)
        self.scan_worker.finished.connect(self.on_scan_finished)
        self.scan_worker.error.connect(self.on_scan_error)
        self.scan_worker.start()

    def on_finding_discovered(self, finding):
        """Handle real-time finding and update dynamic filter."""
        # Update table
        self.results_table.add_finding(finding)
        
        # Update dynamic filter list
        is_dict = isinstance(finding, dict)
        f_type = finding["pattern_name"] if is_dict else finding.pattern_name
        
        if f_type not in self.found_types:
            self.found_types.add(f_type)
            self.type_filter_combo.addItem(f_type)

    def stop_scan(self):
        if self.scanner:
            self.scanner.stop()
            self.scan_panel.stop_btn.setEnabled(False)
            InfoBar.warning(title="Stopping Scan", content="Scan termination requested...", parent=self)

    def on_scan_finished(self, session_id: str):
        self.last_session_id = session_id
        self.scan_panel.scan_btn.setEnabled(True)
        self.scan_panel.stop_btn.setEnabled(False)
        
        InfoBar.success(
            title="Scan Complete",
            content=f"Scan finished successfully.",
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

    def save_copy_to_vault(self, finding):
        """Save a copy of the selected finding to the vault."""
        if self.vault.is_locked:
            InfoBar.warning(
                title="Vault Locked",
                content="Please unlock the vault first to save items.",
                parent=self
            )
            return

        try:
            from ..storage.database import VaultEntry, get_session
            from ..storage.repository import VaultRepository
            import uuid

            # Encrypt finding details
            is_dict = isinstance(finding, dict)
            match_text = finding.get("match_text", "N/A") if is_dict else getattr(finding, "match_text", "N/A")
            if not match_text:
                match_text = "N/A"
            
            ct, iv, tag = self.vault.encrypt(match_text)
            
            # Save to DB
            session = self.get_db_session()
            repo = VaultRepository(session)
            
            entry = VaultEntry(
                id=str(uuid.uuid4()),
                finding_id=finding.get("id") if is_dict else getattr(finding, "id", str(uuid.uuid4())),
                encrypted_value=ct,
                iv=iv,
                tag=tag
            )
            repo.create(entry)
            
            # Refresh vault view if it's open
            self.refresh_vault_dashboard()
            
            InfoBar.success(
                title="Saved to Vault",
                content=f"Copy of finding saved securely.",
                parent=self
            )
        except Exception as e:
            InfoBar.error(title="Vault Error", content=f"Failed to save to vault: {str(e)}", parent=self)

    def open_in_explorer(self, file_path: str):
        """Open file location in Explorer and select the file."""
        import subprocess
        path = os.path.abspath(file_path)
        if os.path.exists(path):
            subprocess.run(['explorer', '/select,', path])
        else:
            InfoBar.error(title="Error", content="File not found.", parent=self)

    def view_details(self, finding):
        """Show full details of a finding."""
        from .widgets import DetailsDialog
        dialog = DetailsDialog(finding, self)
        dialog.exec()

    def get_db_session(self):
        """Get a database session using the provided session factory."""
        from ..storage.database import init_db, get_session
        if not self.session_factory:
            db_path = self.settings.value("db_path", str(Path.home() / ".datashield" / "datashield.db"))
            self.session_factory = init_db(f"sqlite:///{db_path}")
        return get_session(self.session_factory)

    def refresh_vault_dashboard(self):
        """Refresh the vault dashboard with current entries."""
        if not self.vault.is_locked:
            from ..storage.repository import VaultRepository
            session = self.get_db_session()
            repo = VaultRepository(session)
            entries = repo.get_all()
            self.vault_interface.set_unlocked(True, entries)

    def on_vault_unlocked(self):
        self.refresh_vault_dashboard()
        InfoBar.success(title="Vault Unlocked", content="Secure storage is now accessible.", parent=self)

    def set_theme_manager(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager

    def closeEvent(self, event):
        """Ensure vault is locked and threads are stopped on close."""
        if hasattr(self, "scan_worker") and self.scan_worker.isRunning():
            self.scanner.stop()
            self.scan_worker.wait(2000) # Wait up to 2 seconds
            
        if self.vault:
            self.vault.lock()
        self.tray_icon.hide()
        super().closeEvent(event)
