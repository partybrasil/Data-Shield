"""
App Fingerprinter — Layer 7 enrichment: maps file paths to responsible apps.

Uses the AppSignaturesDB to identify which software owns a discovered
credential file.  Falls back to psutil process inspection when needed.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

import psutil
from loguru import logger

from datashield.core.models import AppSignature, AppSignaturesDB, Confidence
from datashield.patterns.app_signatures import get_db


def _expand(path_str: str) -> str:
    """Expand Windows environment variables in a path string."""
    return os.path.expandvars(path_str)


def _glob_match(pattern: str, path_lower: str) -> bool:
    """Simplified glob: handles '*' wildcards in path patterns."""
    expanded = _expand(pattern).lower()
    # Convert glob '*' to regex '.*'
    regex = re.escape(expanded).replace(r"\*", ".*")
    try:
        return bool(re.match(regex, path_lower))
    except re.error:
        return False


class AppFingerprinter:
    """
    Identifies which application is responsible for a credential file.

    Matching is done in two passes:
    1. Path-based: compare the file path against each signature's ``paths`` list.
    2. Process-based: check running processes for open handles to the file
       (requires admin privileges; silently skipped if unavailable).
    """

    def __init__(self, db: Optional[AppSignaturesDB] = None) -> None:
        self._db: AppSignaturesDB = db or get_db()
        self._running_procs: dict[str, list[int]] = {}   # exe_lower → [pid, ...]
        self._refresh_procs()

    def _refresh_procs(self) -> None:
        """Snapshot the currently running processes (exe name → PIDs)."""
        self._running_procs = {}
        try:
            for proc in psutil.process_iter(["pid", "name"]):
                name_lower = (proc.info["name"] or "").lower()
                self._running_procs.setdefault(name_lower, []).append(proc.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # ── Public API ────────────────────────────────────────────────────────

    def identify(self, file_path: str, quick: bool = False) -> tuple[Optional[AppSignature], bool, Optional[int]]:
        """
        Identify the app responsible for *file_path*.

        Args:
            file_path: Absolute path to the file.
            quick: If True, skip expensive process handle scanning (significant speedup).

        Returns:
            Tuple of ``(signature, app_is_running, pid)``.
        """
        path_lower = file_path.lower()

        # Pass 1 — path matching
        for sig in self._db.apps:
            for pattern in sig.paths:
                expanded = _expand(pattern).lower()
                if path_lower.startswith(expanded) or _glob_match(pattern, path_lower):
                    running, pid = self._check_running(sig)
                    return sig, running, pid

        # Pass 2 — process file-handle scan (admin required, skipped if quick=True)
        if not quick:
            sig, pid = self._scan_open_handles(file_path)
            if sig:
                return sig, True, pid

        return None, False, None

    def identify_by_path_prefix(self, file_path: str) -> list[AppSignature]:
        """Return all signatures whose paths are a prefix of file_path.

        Useful for bulk enrichment where multiple apps may claim a path.

        Args:
            file_path: Absolute path string.

        Returns:
            List of matching AppSignature objects.
        """
        path_lower = file_path.lower()
        matches: list[AppSignature] = []
        for sig in self._db.apps:
            for pattern in sig.paths:
                expanded = _expand(pattern).lower()
                if path_lower.startswith(expanded) or _glob_match(pattern, path_lower):
                    matches.append(sig)
                    break
        return matches

    # ── Internal helpers ──────────────────────────────────────────────────

    def _check_running(self, sig: AppSignature) -> tuple[bool, Optional[int]]:
        """Check whether any of the signature's processes are running."""
        for proc_name in sig.process_names:
            key = proc_name.lower()
            pids = self._running_procs.get(key, [])
            if pids:
                return True, pids[0]
        return False, None

    def _scan_open_handles(
        self, file_path: str
    ) -> tuple[Optional[AppSignature], Optional[int]]:
        """
        Check whether any running process has *file_path* open.

        Requires administrator privileges; silently returns (None, None)
        if access is denied.
        """
        try:
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    open_files = proc.open_files()
                    for of in open_files:
                        if of.path.lower() == file_path.lower():
                            proc_name = (proc.info["name"] or "").lower()
                            # Match against signatures
                            for sig in self._db.apps:
                                if any(
                                    pn.lower() == proc_name
                                    for pn in sig.process_names
                                ):
                                    return sig, proc.info["pid"]
                            return None, proc.info["pid"]
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"Handle scan skipped: {exc}")
        return None, None
