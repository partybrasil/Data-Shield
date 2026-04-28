"""Real-time file monitoring with Watchdog."""

from pathlib import Path
from typing import List, Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from ..core.events import EventBus, Event, EventType


class CredentialFileHandler(FileSystemEventHandler):
    """Handler for file system events during monitoring."""

    def __init__(self, pattern_engine, event_bus: EventBus, alert_threshold: int = 70):
        """Initialize handler.

        Args:
            pattern_engine: Pattern detection engine
            event_bus: Event bus for notifications
            alert_threshold: Risk score threshold for alerts
        """
        self.pattern_engine = pattern_engine
        self.event_bus = event_bus
        self.alert_threshold = alert_threshold

    def on_modified(self, event: FileModifiedEvent):
        """Handle file modification."""
        if event.is_directory:
            return

        try:
            file_path = Path(event.src_path)
            # Read file
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(1000000)  # First 1MB

            # Detect patterns
            findings = self.pattern_engine.detect_in_text(content, str(file_path))

            # Emit events for high-risk findings
            for finding in findings:
                if finding.risk_score >= self.alert_threshold:
                    self.event_bus.emit(
                        Event(
                            type=EventType.FINDING_DETECTED,
                            data={"finding": finding, "file": str(file_path)},
                        )
                    )
        except Exception:
            pass


class Monitor:
    """Real-time credential file monitor."""

    def __init__(
        self,
        pattern_engine,
        event_bus: EventBus,
        alert_threshold: int = 70,
        watch_dirs: Optional[List[str]] = None,
    ):
        """Initialize monitor.

        Args:
            pattern_engine: Pattern detection engine
            event_bus: Event bus
            alert_threshold: Risk score threshold
            watch_dirs: Directories to watch
        """
        self.pattern_engine = pattern_engine
        self.event_bus = event_bus
        self.alert_threshold = alert_threshold
        self.watch_dirs = watch_dirs or [str(Path.home())]
        self.observer = Observer()
        self.is_running = False

    def start(self):
        """Start monitoring."""
        if self.is_running:
            return

        handler = CredentialFileHandler(
            self.pattern_engine, self.event_bus, self.alert_threshold
        )

        for watch_dir in self.watch_dirs:
            self.observer.schedule(handler, watch_dir, recursive=True)

        self.observer.start()
        self.is_running = True

        self.event_bus.emit(
            Event(type=EventType.MONITOR_STARTED, data={"dirs": self.watch_dirs})
        )

    def stop(self):
        """Stop monitoring."""
        if not self.is_running:
            return

        self.observer.stop()
        self.observer.join()
        self.is_running = False

        self.event_bus.emit(Event(type=EventType.MONITOR_STOPPED, data={}))

    def add_watch_dir(self, directory: str):
        """Add directory to watch list.

        Args:
            directory: Directory path to watch
        """
        if directory not in self.watch_dirs:
            self.watch_dirs.append(directory)

    def remove_watch_dir(self, directory: str):
        """Remove directory from watch list.

        Args:
            directory: Directory path to stop watching
        """
        if directory in self.watch_dirs:
            self.watch_dirs.remove(directory)
