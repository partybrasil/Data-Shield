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
        self.horizontalHeader().setStretchLastSection(True)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)

    def add_finding(self, finding):
        """Add a finding to the table."""
        row = self.rowCount()
        self.insertRow(row)

        self.setItem(row, 0, QTableWidgetItem(finding.file_path))
        self.setItem(row, 1, QTableWidgetItem(finding.data_type))
        
        # Risk score with color (handled by QSS selection or manual if needed)
        risk_item = QTableWidgetItem(str(finding.risk_score))
        if finding.risk_score >= 70:
            risk_item.setForeground(Qt.red)
        elif finding.risk_score >= 40:
            risk_item.setForeground(Qt.yellow)
        else:
            risk_item.setForeground(Qt.green)
        self.setItem(row, 2, risk_item)

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
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00f2ff;")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(25)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Files scanned: 0/0")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def update_progress(self, current: int, total: int):
        """Update progress display."""
        if total > 0:
            percent = int((current / total) * 100)
            self.progress_bar.setValue(percent)
            self.status_label.setText(f"Files scanned: {current}/{total}")


class VaultPanel(QWidget):
    """Panel for vault operations."""

    def __init__(self):
        """Initialize vault panel."""
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        # Padlock Icon (Decorative)
        self.icon_label = QLabel("🔒")
        self.icon_label.setStyleSheet("font-size: 80px;")
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)

        # Title
        title = QLabel("Secure Vault Storage")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00f2ff;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Master Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(300)
        layout.addWidget(self.password_input, alignment=Qt.AlignCenter)

        # Vault status
        self.status_label = QLabel("VAULT LOCKED")
        self.status_label.setStyleSheet("color: #ff3e3e; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Buttons
        self.unlock_btn = QPushButton("Unlock Vault")
        self.unlock_btn.setFixedWidth(200)
        self.unlock_btn.clicked.connect(self.on_unlock_clicked)
        layout.addWidget(self.unlock_btn, alignment=Qt.AlignCenter)

        self.lock_btn = QPushButton("Lock Vault")
        self.lock_btn.setObjectName("secondary")
        self.lock_btn.setFixedWidth(200)
        self.lock_btn.clicked.connect(self.on_lock_clicked)
        self.lock_btn.hide()
        layout.addWidget(self.lock_btn, alignment=Qt.AlignCenter)

        layout.addStretch()
        self.setLayout(layout)

    def on_unlock_clicked(self):
        """Handle unlock button."""
        self.status_label.setText("VAULT UNLOCKED")
        self.status_label.setStyleSheet("color: #00ffaa; font-weight: bold;")
        self.icon_label.setText("🔓")
        self.unlock_btn.hide()
        self.lock_btn.show()

    def on_lock_clicked(self):
        """Handle lock button."""
        self.status_label.setText("VAULT LOCKED")
        self.status_label.setStyleSheet("color: #ff3e3e; font-weight: bold;")
        self.icon_label.setText("🔒")
        self.password_input.clear()
        self.lock_btn.hide()
        self.unlock_btn.show()
