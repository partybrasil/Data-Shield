"""GUI Widgets for Data-Shield using Fluent Design."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QTableWidgetItem
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from qfluentwidgets import (
    PushButton, PrimaryPushButton, LineEdit, ProgressBar, 
    TableWidget, ComboBox, SpinBox, CheckBox, BodyLabel, 
    SubtitleLabel, StrongBodyLabel, IconWidget, FluentIcon as FIF,
    PasswordLineEdit, PrimaryToolButton, TransparentToolButton
)

class ScanPanel(QWidget):
    """Panel for configuring and starting scans."""

    scan_requested = Signal(str, str)  # path, mode
    stop_requested = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Path selection
        path_layout = QHBoxLayout()
        self.path_input = LineEdit()
        self.path_input.setPlaceholderText("Select target directory...")
        self.path_input.setClearButtonEnabled(True)
        
        browse_btn = PushButton("Browse")
        browse_btn.clicked.connect(self.browse_directory)
        
        path_layout.addWidget(BodyLabel("Target Path:"))
        path_layout.addWidget(self.path_input, 1)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        # Mode selection
        mode_layout = QHBoxLayout()
        self.mode_combo = ComboBox()
        self.mode_combo.addItems(["ultra_fast", "fast", "safe", "deep", "interactive"])
        self.mode_combo.setCurrentText("safe")
        self.mode_combo.setToolTip("ultra_fast: Filenames only\nfast: Regex + YARA\nsafe: All layers (1MB limit)\ndeep: All layers (Full file)")
        
        mode_layout.addWidget(BodyLabel("Scan Mode:"))
        mode_layout.addWidget(self.mode_combo, 1)
        layout.addLayout(mode_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.scan_btn = PrimaryPushButton(FIF.PLAY, "Start Full Scan")
        self.scan_btn.clicked.connect(self.on_scan_clicked)
        btn_layout.addWidget(self.scan_btn)

        self.stop_btn = PushButton(FIF.CLOSE, "Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_requested.emit)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Scan")
        if directory:
            self.path_input.setText(directory)

    def on_scan_clicked(self):
        path = self.path_input.text()
        if not path:
            QMessageBox.warning(self, "Error", "Please select a directory to scan")
            return
        mode = self.mode_combo.currentText()
        self.scan_requested.emit(path, mode)


class MonitorPanel(QWidget):
    """Panel for real-time monitoring."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        self.header = SubtitleLabel("Real-Time Monitor")
        layout.addWidget(self.header)

        self.status_label = StrongBodyLabel("STATUS: INACTIVE")
        self.status_label.setTextColor(QColor("#ff3e3e"))
        layout.addWidget(self.status_label)

        self.toggle_btn = PrimaryPushButton("Enable Monitoring")
        self.toggle_btn.clicked.connect(self.toggle_monitor)
        layout.addWidget(self.toggle_btn)

        layout.addWidget(BodyLabel("Recent Activity:"))
        self.activity_log = TableWidget()
        self.activity_log.setColumnCount(3)
        self.activity_log.setHorizontalHeaderLabels(["Time", "File", "Event"])
        self.activity_log.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.activity_log)

    def toggle_monitor(self):
        if self.toggle_btn.text() == "Enable Monitoring":
            self.toggle_btn.setText("Disable Monitoring")
            self.status_label.setText("STATUS: ACTIVE")
            self.status_label.setTextColor(QColor("#00ffaa"))
        else:
            self.toggle_btn.setText("Enable Monitoring")
            self.status_label.setText("STATUS: INACTIVE")
            self.status_label.setTextColor(QColor("#ff3e3e"))


class SettingsPanel(QWidget):
    """Panel for application settings."""
    
    settings_saved = Signal(list, int)
    password_change_requested = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        layout.addWidget(SubtitleLabel("General Settings"))
        
        layout.addWidget(BodyLabel("Scanning Exclusions (comma separated):"))
        self.exclude_input = LineEdit()
        self.exclude_input.setText("node_modules, venv, .git, .venv")
        layout.addWidget(self.exclude_input)

        layout.addWidget(BodyLabel("Max Scan Threads:"))
        self.threads_spin = SpinBox()
        self.threads_spin.setRange(1, 32)
        self.threads_spin.setValue(4)
        layout.addWidget(self.threads_spin)

        layout.addWidget(SubtitleLabel("Vault Security"))
        
        layout.addWidget(BodyLabel("Current Master Password:"))
        self.old_pass = PasswordLineEdit()
        layout.addWidget(self.old_pass)

        layout.addWidget(BodyLabel("New Master Password:"))
        self.new_pass = PasswordLineEdit()
        layout.addWidget(self.new_pass)

        self.save_btn = PrimaryPushButton("Save All Settings")
        self.save_btn.clicked.connect(self.on_save_clicked)
        layout.addWidget(self.save_btn)

        layout.addStretch()

    def on_save_clicked(self):
        excludes = [s.strip() for s in self.exclude_input.text().split(",") if s.strip()]
        threads = self.threads_spin.value()
        self.settings_saved.emit(excludes, threads)
        
        if self.old_pass.text() and self.new_pass.text():
            self.password_change_requested.emit(self.old_pass.text(), self.new_pass.text())
        
        QMessageBox.information(self, "Settings", "Settings saved successfully!")


class ResultsTable(TableWidget):
    """Table widget for displaying scan results with dynamic filtering."""

    def __init__(self):
        super().__init__()
        self.all_findings = []
        self._current_filter = "All Types"
        self.init_ui()

    def init_ui(self):
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels([
            "File Path", "Type", "Risk", "Confidence", "Detected"
        ])
        self.horizontalHeader().setStretchLastSection(True)
        self.setBorderVisible(True)
        self.setBorderRadius(10)

    def add_finding(self, finding):
        # Store for filtering
        self.all_findings.append(finding)
        
        # Only add to UI if it matches current filter
        is_dict = isinstance(finding, dict)
        f_type = finding["pattern_name"] if is_dict else finding.pattern_name
        
        if self._current_filter == "All Types" or f_type == self._current_filter:
            self._display_finding(finding)

    def _display_finding(self, finding):
        row = self.rowCount()
        self.insertRow(row)

        is_dict = isinstance(finding, dict)
        file_path = finding["file_path"] if is_dict else finding.file_path
        pattern_name = finding["pattern_name"] if is_dict else finding.pattern_name
        risk_score = finding["risk_score"] if is_dict else finding.risk_score
        confidence = finding["confidence"] if is_dict else finding.confidence
        
        found_at = finding["found_at"] if is_dict else finding.found_at
        if isinstance(found_at, str):
            from datetime import datetime
            try:
                found_at = datetime.fromisoformat(found_at)
            except:
                found_at = datetime.now()

        self.setItem(row, 0, QTableWidgetItem(file_path))
        self.setItem(row, 1, QTableWidgetItem(pattern_name))
        
        risk_pct = int(risk_score * 100) if risk_score <= 1.0 else int(risk_score)
        risk_item = QTableWidgetItem(f"{risk_pct}%")
        if risk_pct >= 85:
            risk_item.setForeground(QColor("#ff4d4d"))
        elif risk_pct >= 50:
            risk_item.setForeground(QColor("#ffaa00"))
        else:
            risk_item.setForeground(QColor("#00ffaa"))
        self.setItem(row, 2, risk_item)

        confidence_str = f"{int(confidence * 100)}%"
        self.setItem(row, 3, QTableWidgetItem(confidence_str))
        self.setItem(row, 4, QTableWidgetItem(found_at.strftime("%H:%M:%S")))
        
        self.scrollToBottom()
        self.viewport().update()

    def set_filter(self, filter_type: str):
        """Apply a filter by type and rebuild the table view."""
        self._current_filter = filter_type
        self.setRowCount(0)
        for finding in self.all_findings:
            is_dict = isinstance(finding, dict)
            f_type = finding["pattern_name"] if is_dict else finding.pattern_name
            if filter_type == "All Types" or f_type == filter_type:
                self._display_finding(finding)

    def clear_results(self):
        self.all_findings = []
        self.setRowCount(0)


class ProgressWidget(QWidget):
    """Widget for displaying scan progress."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)

        self.progress_label = StrongBodyLabel("Ready to scan")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setTextColor(QColor("#00f2ff"))
        layout.addWidget(self.progress_label)

        self.progress_bar = ProgressBar()
        self.progress_bar.setFixedHeight(6)
        layout.addWidget(self.progress_bar)

        self.status_label = BodyLabel("Files scanned: 0/0")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def update_progress(self, current: int, total: int):
        if total > 0:
            if current == 0 and total > 1:
                # Signal for discovery phase
                self.progress_bar.setRange(0, 0) # Indeterminate mode
                self.progress_label.setText("Analyzing file system...")
                self.status_label.setText(f"Files found: {total}...")
                return
            
            self.progress_bar.setRange(0, 100)
            percent = int((current / total) * 100)
            self.progress_bar.setValue(percent)
            self.status_label.setText(f"Files scanned: {current}/{total}")
            
            if percent < 100:
                self.progress_label.setText(f"Scanning... {percent}%")
            else:
                self.progress_label.setText("Scan Complete")
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.status_label.setText("Files scanned: 0/0")


class VaultPanel(QWidget):
    """Panel for vault operations."""

    unlock_requested = Signal(str)
    lock_requested = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(50, 50, 50, 50)

        self.icon_widget = IconWidget(FIF.FINGERPRINT)
        self.icon_widget.setFixedSize(120, 120)
        layout.addWidget(self.icon_widget, 0, Qt.AlignCenter)

        self.title = SubtitleLabel("Secure Vault Storage")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        self.password_input = PasswordLineEdit()
        self.password_input.setPlaceholderText("Enter Master Password")
        self.password_input.setFixedWidth(350)
        layout.addWidget(self.password_input, 0, Qt.AlignCenter)

        self.status_label = StrongBodyLabel("VAULT LOCKED")
        self.status_label.setTextColor(QColor("#ff3e3e"))
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.unlock_btn = PrimaryPushButton("Unlock Secure Vault")
        self.unlock_btn.setFixedWidth(250)
        self.unlock_btn.clicked.connect(self.on_unlock_clicked)
        layout.addWidget(self.unlock_btn, 0, Qt.AlignCenter)

        self.lock_btn = PushButton(FIF.CLOSE, "Lock Vault")
        self.lock_btn.setFixedWidth(250)
        self.lock_btn.clicked.connect(self.on_lock_clicked)
        self.lock_btn.hide()
        layout.addWidget(self.lock_btn, 0, Qt.AlignCenter)

        layout.addStretch()

    def on_unlock_clicked(self):
        password = self.password_input.text()
        if not password:
            return
        self.unlock_requested.emit(password)

    def on_lock_clicked(self):
        self.lock_requested.emit()

    def set_unlocked(self, unlocked: bool):
        if unlocked:
            self.status_label.setText("VAULT UNLOCKED")
            self.status_label.setTextColor(QColor("#00ffaa"))
            self.icon_widget.setIcon(FIF.COMPLETED)
            self.unlock_btn.hide()
            self.lock_btn.show()
        else:
            self.status_label.setText("VAULT LOCKED")
            self.status_label.setTextColor(QColor("#ff3e3e"))
            self.icon_widget.setIcon(FIF.FINGERPRINT)
            self.password_input.clear()
            self.lock_btn.hide()
            self.unlock_btn.show()
