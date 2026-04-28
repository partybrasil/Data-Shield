"""GUI Widgets for Data-Shield."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QProgressBar, QTableWidget, QTableWidgetItem, QComboBox,
    QFileDialog, QMessageBox, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from typing import Optional


class ScanPanel(QWidget):
    """Panel for configuring and starting scans."""

    scan_requested = Signal(str, str)  # path, mode

    def __init__(self):
        """Initialize scan panel."""
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()

        # Path selection
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Target Path:"))
        self.path_input = QLineEdit()
        path_layout.addWidget(self.path_input)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_directory)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["safe", "fast", "interactive"])
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # Scan button
        self.scan_btn = QPushButton("Start Scan")
        self.scan_btn.clicked.connect(self.on_scan_clicked)
        layout.addWidget(self.scan_btn)

        self.setLayout(layout)

    def browse_directory(self):
        """Browse for directory to scan."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Scan")
        if directory:
            self.path_input.setText(directory)

    def on_scan_clicked(self):
        """Handle scan button click."""
        path = self.path_input.text()
        if not path:
            QMessageBox.warning(self, "Error", "Please select a directory to scan")
            return
        mode = self.mode_combo.currentText()
        self.scan_requested.emit(path, mode)


class ResultsTable(QTableWidget):
    """Table widget for displaying scan results."""

    def __init__(self):
        """Initialize results table."""
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels([
            "File Path", "Type", "Risk", "Confidence", "Detected"
        ])
        self.resizeColumnsToContents()

    def add_finding(self, finding):
        """Add a finding to the table.

        Args:
            finding: Finding object
        """
        row = self.rowCount()
        self.insertRow(row)

        self.setItem(row, 0, QTableWidgetItem(finding.file_path[:100]))
        self.setItem(row, 1, QTableWidgetItem(finding.data_type))
        self.setItem(row, 2, QTableWidgetItem(str(finding.risk_score)))
        confidence_str = finding.confidence.value if hasattr(finding.confidence, "value") else str(finding.confidence)
        self.setItem(row, 3, QTableWidgetItem(confidence_str))
        self.setItem(row, 4, QTableWidgetItem(finding.discovered_at.strftime("%H:%M:%S")))

    def clear_results(self):
        """Clear all results."""
        self.setRowCount(0)


class ProgressWidget(QWidget):
    """Widget for displaying scan progress."""

    def __init__(self):
        """Initialize progress widget."""
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()

        self.progress_label = QLabel("Ready to scan")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Files scanned: 0/0")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def update_progress(self, current: int, total: int):
        """Update progress display.

        Args:
            current: Current file count
            total: Total files
        """
        if total > 0:
            percent = int((current / total) * 100)
            self.progress_bar.setValue(percent)
            self.status_label.setText(f"Files scanned: {current}/{total}")


class VaultPanel(QWidget):
    """Panel for vault operations."""

    encrypt_requested = Signal(str)  # finding_id
    decrypt_requested = Signal(str)  # finding_id

    def __init__(self):
        """Initialize vault panel."""
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()

        # Password input
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Master Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(self.password_input)
        layout.addLayout(pass_layout)

        # Vault status
        self.status_label = QLabel("Vault: Locked")
        layout.addWidget(self.status_label)

        # Buttons
        btn_layout = QHBoxLayout()
        unlock_btn = QPushButton("Unlock")
        unlock_btn.clicked.connect(self.on_unlock_clicked)
        btn_layout.addWidget(unlock_btn)

        lock_btn = QPushButton("Lock")
        lock_btn.clicked.connect(self.on_lock_clicked)
        btn_layout.addWidget(lock_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def on_unlock_clicked(self):
        """Handle unlock button."""
        self.status_label.setText("Vault: Unlocked")

    def on_lock_clicked(self):
        """Handle lock button."""
        self.status_label.setText("Vault: Locked")
        self.password_input.clear()
