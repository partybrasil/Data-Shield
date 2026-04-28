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

    def __init__(self, config: ScanConfig, session_factory: Callable[[], Session], event_bus: Optional[EventBus] = None):
        """Initialize scanner.

        Args:
            config: Scan configuration
            session_factory: Database session factory (SessionLocal)
            event_bus: Optional event bus for notifications
        """
        self.config = config
        self.session_factory = session_factory
        self.event_bus = event_bus or EventBus()
        self.pattern_engine = PatternEngine()
        self.fingerprinter = AppFingerprinter()
        self.is_paused = False
        self.should_stop = False

    def scan(self, target_path: str, callback: Optional[Callable] = None) -> str:
        """Perform a file system scan."""
        scan_id = str(uuid4())
        target = Path(target_path).expanduser()

        if not target.exists():
            raise ValueError(f"Path does not exist: {target}")

        session = self.session_factory()
        repo = ScanSessionRepository(session)
        
        try:
            # Create scan session
            scan_session = ScanSessionDB(
                id=scan_id,
                target_path=str(target),
                mode=self.config.mode,
                status="running",
            )
            repo.create(scan_session)

            # Emit start event
            self.event_bus.emit(
                Event(
                    type=EventType.SCAN_STARTED,
                    timestamp=datetime.utcnow(),
                    data={"session_id": scan_id, "target": str(target)},
                )
            )

            self._scan_directory(target, scan_id, callback)
            repo.update(scan_id, status="completed", end_time=datetime.utcnow())
            
            self.event_bus.emit(
                Event(
                    type=EventType.SCAN_COMPLETED,
                    timestamp=datetime.utcnow(),
                    data={"session_id": scan_id},
                )
            )
        except Exception as e:
            repo.update(
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
        finally:
            session.close()

        return scan_id

    def _scan_directory(
        self, path: Path, session_id: str, callback: Optional[Callable] = None
    ):
        """Recursively scan directory."""
        files = self._get_files(path, callback=callback)
        total = len(files)

        with ThreadPoolExecutor(max_workers=self.config.thread_count) as executor:
            futures = {
                executor.submit(self._scan_file, f, session_id): f for f in files
            }

            session = self.session_factory()
            from ..core.findings import FindingService
            service = FindingService(session)
            
            try:
                for i, future in enumerate(as_completed(futures)):
                    if self.should_stop:
                        # Attempt to cancel all pending tasks for immediate stop
                        executor.shutdown(wait=False, cancel_futures=True)
                        break

                    try:
                        findings = future.result()
                        for finding in findings:
                            db_finding = service.create_finding(
                                file_path=finding.file_path,
                                pattern_name=finding.data_type,
                                match_text=finding.sensitive_value or "",
                                risk_score=float(finding.risk_score),
                                confidence=1.0,
                                session_id=session_id,
                            )
                            if callback:
                                finding_dict = {
                                    "file_path": db_finding.file_path,
                                    "pattern_name": db_finding.pattern_name,
                                    "risk_score": db_finding.risk_score,
                                    "confidence": db_finding.confidence,
                                    "found_at": db_finding.found_at.isoformat()
                                }
                                callback(-1, -1, finding=finding_dict)
                    except Exception:
                        pass

                    if callback:
                        callback(i + 1, total)
                
                session.commit()
            finally:
                session.close()

    def _get_files(self, path: Path, callback: Optional[Callable] = None) -> List[Path]:
        """Get all files from directory recursively using a faster, interruptible method."""
        files = []
        exclude_dirs = set(self.config.exclude_dirs)
        
        # Add common system/junk dirs to auto-exclude for performance if not explicitly included
        auto_exclude = {
            "$RECYCLE.BIN", "System Volume Information", ".git", "node_modules",
            "AppData/Local/Temp", "AppData/Local/Microsoft/Windows/INetCache"
        }

        def _walk(current_path: Path):
            if self.should_stop:
                return

            try:
                # Use os.scandir for better performance on Windows
                with os.scandir(current_path) as it:
                    for entry in it:
                        if self.should_stop:
                            return

                        if entry.is_dir():
                            if entry.name in exclude_dirs or entry.name in auto_exclude:
                                continue
                            _walk(Path(entry.path))
                        elif entry.is_file():
                            try:
                                stats = entry.stat()
                                if stats.st_size <= self.config.max_file_size:
                                    files.append(Path(entry.path))
                                    # Periodically report discovery progress
                                    if callback and len(files) % 500 == 0:
                                        callback(0, len(files)) # Use 0 current to signal "discovery"
                            except OSError:
                                continue
            except PermissionError:
                pass # Skip folders we can't access
            except Exception:
                pass

        import os
        _walk(path)
        return files

    def _scan_file(self, file_path: Path, session_id: str) -> List[Finding]:
        """Scan a single file and return findings based on scan mode."""
        findings = []
        if self.should_stop:
            return findings

        mode = self.config.mode

        # Define content read limits based on mode
        limits = {
            "ultra_fast": 10240,       # 10 KB
            "fast": 102400,            # 100 KB
            "safe": 1048576,           # 1 MB
            "deep": self.config.max_file_size, # Full file
            "interactive": 1048576      # 1 MB
        }
        
        content_limit = limits.get(mode, 1048576)

        try:
            # Try text reading
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(content_limit)
            except Exception:
                return findings

            # Detect patterns using engine with mode awareness
            findings = self.pattern_engine.detect_in_text(content, str(file_path), mode=mode)
            
            # Additional scoring
            for finding in findings:
                score, level = compute_risk_score(
                    pattern_id=finding.pattern_id,
                    file_path=finding.file_path,
                    detection_layer=finding.detection_layer.value if hasattr(finding.detection_layer, "value") else str(finding.detection_layer)
                )
                finding.risk_score = score
                finding.risk_level = level

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
