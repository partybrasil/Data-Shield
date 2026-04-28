"""Worker threads for long-running operations."""

from typing import Callable, Any, Optional
from PySide6.QtCore import QThread, Signal
from pathlib import Path


class ScanWorker(QThread):
    """Worker thread for scanning operations."""

    progress = Signal(int, int)  # current, total
    finding_discovered = Signal(object)  # finding object
    finished = Signal(str)  # session_id
    error = Signal(str)  # error message

    def __init__(self, scanner, path: str, mode: str = "safe"):
        super().__init__()
        self.scanner = scanner
        self.path = path
        self.mode = mode

    def run(self):
        """Run scan in worker thread."""
        try:
            def scan_callback(current, total, finding=None):
                if finding:
                    self.finding_discovered.emit(finding)
                if current >= 0:
                    self.progress.emit(current, total)

            session_id = self.scanner.scan(self.path, callback=scan_callback)
            self.finished.emit(session_id)
        except Exception as e:
            self.error.emit(str(e))


class VaultWorker(QThread):
    """Worker thread for vault operations."""

    finished = Signal()
    error = Signal(str)

    def __init__(self, vault, operation: str, *args, **kwargs):
        """Initialize vault worker.

        Args:
            vault: Vault instance
            operation: Operation name (encrypt, decrypt, lock, unlock)
            args: Operation arguments
            kwargs: Operation keyword arguments
        """
        super().__init__()
        self.vault = vault
        self.operation = operation
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """Run vault operation in worker thread."""
        try:
            method = getattr(self.vault, self.operation, None)
            if method:
                method(*self.args, **self.kwargs)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class MonitorWorker(QThread):
    """Worker thread for monitoring operations."""

    finding_detected = Signal(dict)  # finding data
    error = Signal(str)

    def __init__(self, monitor):
        """Initialize monitor worker.

        Args:
            monitor: Monitor instance
        """
        super().__init__()
        self.monitor = monitor

    def run(self):
        """Run monitoring in worker thread."""
        try:
            self.monitor.start()
            # Wait until stopped
            while self.monitor.is_running:
                self.msleep(100)
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        """Stop monitoring."""
        self.monitor.stop()
