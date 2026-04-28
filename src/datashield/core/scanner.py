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
        files = self._get_files(path)
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
                        break

                    try:
                        findings = future.result()
                        for finding in findings:
                            service.create_finding(
                                file_path=finding.file_path,
                                pattern_name=finding.data_type,
                                match_text=finding.sensitive_value or "",
                                risk_score=float(finding.risk_score),
                                confidence=1.0,
                                session_id=session_id,
                            )
                    except Exception:
                        pass

                    if callback:
                        callback(i + 1, total)
                
                session.commit()
            finally:
                session.close()

    def _get_files(self, path: Path) -> List[Path]:
        """Get all files from directory recursively."""
        files = []
        exclude_dirs = set(self.config.exclude_dirs)

        for item in path.rglob("*"):
            if item.is_file():
                # Only exclude if the excluded directory is WITHIN the target path
                try:
                    relative_path = item.relative_to(path)
                    if any(excluded in relative_path.parts for excluded in exclude_dirs):
                        continue
                except ValueError:
                    # Fallback for paths that might not be relative for some reason
                    if any(excluded in item.parts for excluded in exclude_dirs):
                        continue
                
                if item.stat().st_size <= self.config.max_file_size:
                    files.append(item)

        return files

    def _scan_file(self, file_path: Path, session_id: str) -> List[Finding]:
        """Scan a single file and return findings."""
        findings = []

        try:
            # Try text reading
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(1000000)  # First 1MB
            except Exception:
                return findings

            # Detect patterns using engine
            findings = self.pattern_engine.detect_in_text(content, str(file_path))
            
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
