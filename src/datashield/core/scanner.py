"""Main scanning engine for Data-Shield."""

import asyncio
from pathlib import Path
from typing import Optional, List, Callable
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..core.models import Finding
from ..core.pattern_engine import PatternEngine
from ..core.risk_scorer import compute_risk_score
from ..core.app_fingerprint import AppFingerprinter
from ..core.events import EventBus, Event, EventType
from ..storage.database import ScanSession as ScanSessionDB
from ..storage.repository import ScanSessionRepository
from ..config.settings import ScanConfig


class Scanner:
    """Main scanning engine."""

    def __init__(self, config: ScanConfig, session: Session, event_bus: Optional[EventBus] = None):
        """Initialize scanner.

        Args:
            config: Scan configuration
            session: Database session
            event_bus: Optional event bus for notifications
        """
        self.config = config
        self.session = session
        self.event_bus = event_bus or EventBus()
        self.pattern_engine = PatternEngine()
        self.fingerprinter = AppFingerprinter()
        self.repo = ScanSessionRepository(session)
        self.is_paused = False
        self.should_stop = False

    def scan(self, target_path: str, callback: Optional[Callable] = None) -> str:
        """Perform a file system scan.

        Args:
            target_path: Path to scan
            callback: Optional progress callback

        Returns:
            Scan session ID
        """
        scan_id = str(uuid4())
        target = Path(target_path).expanduser()

        if not target.exists():
            raise ValueError(f"Path does not exist: {target}")

        # Create scan session
        scan_session = ScanSessionDB(
            id=scan_id,
            target_path=str(target),
            mode=self.config.mode,
            status="running",
        )
        self.repo.create(scan_session)

        # Emit start event
        self.event_bus.emit(
            Event(
                type=EventType.SCAN_STARTED,
                timestamp=datetime.utcnow(),
                data={"session_id": scan_id, "target": str(target)},
            )
        )

        try:
            self._scan_directory(target, scan_id, callback)
            self.repo.update(scan_id, status="completed", end_time=datetime.utcnow())
            self.event_bus.emit(
                Event(
                    type=EventType.SCAN_COMPLETED,
                    timestamp=datetime.utcnow(),
                    data={"session_id": scan_id},
                )
            )
        except Exception as e:
            self.repo.update(
                scan_id, status="failed", error_message=str(e), end_time=datetime.utcnow()
            )
            self.event_bus.emit(
                Event(
                    type=EventType.SCAN_FAILED,
                    timestamp=datetime.utcnow(),
                    error=str(e),
                    data={"session_id": scan_id},
                )
            )

        return scan_id

    def _scan_directory(
        self, path: Path, session_id: str, callback: Optional[Callable] = None
    ):
        """Recursively scan directory.

        Args:
            path: Directory to scan
            session_id: Associated scan session ID
            callback: Progress callback
        """
        files = self._get_files(path)
        total = len(files)

        with ThreadPoolExecutor(max_workers=self.config.thread_count) as executor:
            futures = {
                executor.submit(self._scan_file, f, session_id): f for f in files
            }

            for i, future in enumerate(as_completed(futures)):
                if self.should_stop:
                    break

                try:
                    future.result()
                except Exception:
                    pass

                if callback:
                    callback(i + 1, total)

    def _get_files(self, path: Path) -> List[Path]:
        """Get all files from directory recursively.

        Args:
            path: Directory path

        Returns:
            List of file paths.
        """
        files = []
        exclude_dirs = set(self.config.exclude_dirs)

        for item in path.rglob("*"):
            if item.is_file() and all(
                excluded not in item.parts for excluded in exclude_dirs
            ):
                if item.stat().st_size <= self.config.max_file_size:
                    files.append(item)

        return files

    def _scan_file(self, file_path: Path, session_id: str) -> List[Finding]:
        """Scan a single file.

        Args:
            file_path: File to scan
            session_id: Associated scan session ID

        Returns:
            List of findings.
        """
        findings = []

        try:
            # Try text reading
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(1000000)  # First 1MB
            except Exception:
                return findings

            # Detect patterns
            findings = self.pattern_engine.detect_in_text(content, str(file_path))

            # Score each finding
            for finding in findings:
                finding.risk_score = compute_risk_score(finding)

            # Store findings
            for finding in findings:
                from ..core.findings import FindingService

                service = FindingService(self.session)
                service.create_finding(
                    file_path=finding.file_path,
                    pattern_name=finding.pattern_name,
                    match_text=finding.match_text or "",
                    risk_score=finding.risk_score,
                    confidence=finding.confidence,
                    session_id=session_id,
                )

        except Exception:
            pass

        return findings

    def pause(self):
        """Pause scanning."""
        self.is_paused = True

    def resume(self):
        """Resume scanning."""
        self.is_paused = False

    def stop(self):
        """Stop scanning."""
        self.should_stop = True
