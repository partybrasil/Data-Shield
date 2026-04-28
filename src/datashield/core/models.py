"""
Data-Shield core data models.

All dataclasses / Pydantic models that flow between modules are defined here.
No other Data-Shield module is imported to keep this dependency-free.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Enumerations ──────────────────────────────────────────────────────────────

class RiskLevel(str, Enum):
    """Overall risk classification for a finding."""
    CRITICAL = "CRITICAL"   # 85-100
    HIGH     = "HIGH"       # 65-84
    MEDIUM   = "MEDIUM"     # 40-64
    LOW      = "LOW"        # 0-39


class DetectionLayer(str, Enum):
    """Which detection layer produced the finding."""
    FILENAME   = "filename"    # Layer 1: filename/extension match
    REGEX      = "regex"       # Layer 2: regex pattern match
    YARA       = "yara"        # Layer 3: YARA rule match
    ENTROPY    = "entropy"     # Layer 4: Shannon entropy anomaly
    PARSER     = "parser"      # Layer 5: structured data parser
    SPECIFIC   = "specific"    # Layer 6: app-specific parser
    REGISTRY   = "registry"    # Windows Registry scan
    CREDENTIAL = "credential"  # Windows Credential Manager


class Confidence(str, Enum):
    """Confidence level in the identification of an app or pattern."""
    HIGH   = "HIGH"
    MEDIUM = "MEDIUM"
    LOW    = "LOW"


class ScanStatus(str, Enum):
    """Lifecycle state of a scan session."""
    PENDING   = "pending"
    RUNNING   = "running"
    PAUSED    = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR     = "error"


class OperationMode(str, Enum):
    """Scan operation mode controlling resource usage and user interaction."""
    PERFORMANCE  = "performance"   # Max speed, all CPU/RAM
    SAFE         = "safe"          # Low resource footprint
    INTERACTIVE  = "interactive"   # Pause on each finding for user action
    TURBO        = "turbo"         # High-value extensions only (fast triage)
    DEEP         = "deep"          # Every file including binaries + entropy
    QUICK        = "quick"         # Pre-defined high-probability paths only


class ScanDepth(str, Enum):
    """Shorthand depth presets."""
    UNLIMITED = "unlimited"
    SHALLOW   = "shallow"    # depth=2
    STANDARD  = "standard"   # depth=5


# ── Core Models ───────────────────────────────────────────────────────────────

class Finding(BaseModel):
    """
    Represents a single sensitive-data discovery made during a scan.

    Attributes:
        id:                 Unique UUID for this finding.
        session_id:         UUID of the parent ScanSession.
        file_path:          Absolute path to the file containing the data.
        file_name:          Basename of the file.
        data_type:          Human-readable type label (e.g. "AWS Access Key").
        pattern_id:         Internal ID of the regex / YARA rule that fired.
        sensitive_value:    The raw matched value (censored in UI by default).
        context_snippet:    Short surrounding context (max 200 chars).
        responsible_app:    Internal app ID from APP_SIGNATURES (e.g. "vscode").
        app_display_name:   Human name of the responsible app.
        app_icon:           Relative icon filename inside gui/resources/icons/.
        app_is_running:     Whether the responsible app is currently running.
        pid:                PID of running app, if detected.
        risk_score:         0-100 numeric score.
        risk_level:         RiskLevel enum derived from risk_score.
        confidence:         Confidence of the detection.
        detection_layer:    Which layer fired.
        is_active_process:  Whether any process has this file open.
        ignored:            User marked this finding as ignored.
        in_vault:           File has been encrypted with Vault.
        discovered_at:      Timestamp of discovery.
        file_modified_at:   mtime of the file at scan time.
        file_size:          File size in bytes.
        line_number:        Line number in the file (if applicable).
        remediation_url:    URL for manual remediation (e.g. revoke token page).
        remediation_cmd:    CLI command for remediation.
        app_signature_version: Version of the AppSignaturesDB used.
    """
    id:                    str       = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id:            str       = ""
    file_path:             str       = ""
    file_name:             str       = ""
    data_type:             str       = ""
    pattern_id:            str       = ""
    sensitive_value:       str       = ""
    context_snippet:       str       = ""
    responsible_app:       str | None = None
    app_display_name:      str | None = None
    app_icon:              str | None = None
    app_is_running:        bool      = False
    pid:                   int | None = None
    risk_score:            int       = 0
    risk_level:            RiskLevel = RiskLevel.LOW
    confidence:            Confidence = Confidence.MEDIUM
    detection_layer:       DetectionLayer = DetectionLayer.REGEX
    is_active_process:     bool      = False
    ignored:               bool      = False
    in_vault:              bool      = False
    discovered_at:         datetime  = Field(default_factory=datetime.now)
    file_modified_at:      datetime | None = None
    file_size:             int       = 0
    line_number:           int | None = None
    remediation_url:       str | None = None
    remediation_cmd:       str | None = None
    app_signature_version: str       = "0.0.0"

    def censored_value(self, show_chars: int = 4) -> str:
        """Return the sensitive value with middle portion masked.

        Args:
            show_chars: Number of chars to show at each end.

        Returns:
            Censored string like ``AKIA****ABCD``.
        """
        v = self.sensitive_value
        if len(v) <= show_chars * 2:
            return "*" * len(v)
        return v[:show_chars] + "****" + v[-show_chars:]

    @property
    def risk_color(self) -> str:
        """Return the neon-palette color name for this risk level."""
        colors = {
            RiskLevel.CRITICAL: "#FF4C6E",
            RiskLevel.HIGH:     "#FFB347",
            RiskLevel.MEDIUM:   "#FFE566",
            RiskLevel.LOW:      "#4CFFA0",
        }
        return colors[self.risk_level]


class ScanProgressEvent(BaseModel):
    """Emitted periodically during scanning to drive progress UI."""
    session_id:      str
    current_file:    str
    files_scanned:   int  = 0
    total_estimated: int  = 0
    findings_count:  int  = 0
    errors_count:    int  = 0
    elapsed_seconds: float = 0.0
    scan_rate:       float = 0.0   # files/sec
    percent:         float = 0.0


class ScanCompleteEvent(BaseModel):
    """Emitted when a scan session finishes."""
    session_id:    str
    total_files:   int
    total_findings: int
    duration:      float
    errors:        int
    completed_at:  datetime = Field(default_factory=datetime.now)


class FindingActionEvent(BaseModel):
    """Emitted in INTERACTIVE mode when the scanner pauses for user action."""
    finding:      Finding
    session_id:   str
    timeout_secs: int = 300


class ScanConfig(BaseModel):
    """
    Full configuration for a scan session.

    All fields have sensible defaults so callers can pass minimal config.
    """
    root_path:          str             = r"C:\Users"
    mode:               OperationMode  = OperationMode.SAFE
    max_depth:          int            = 0        # 0 = unlimited
    include_hidden:     bool           = True
    follow_symlinks:    bool           = False
    max_file_size_mb:   float          = 50.0     # skip files larger than this
    max_threads:        int            = 0        # 0 = auto from mode
    progress_interval_ms: int         = 500
    interactive_timeout_secs: int     = 300
    checkpoint_every:   int            = 500      # files between checkpoints
    exclude_paths:      list[str]      = Field(default_factory=list)
    include_extensions: list[str]      = Field(default_factory=list)  # empty=all
    turbo_extensions:   list[str]      = Field(default_factory=lambda: [
        ".env", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
        ".key", ".pem", ".p12", ".pfx", ".sqlite", ".db", ".gitconfig",
        ".netrc", ".npmrc", ".htpasswd",
    ])
    high_priority_names: list[str]    = Field(default_factory=lambda: [
        "credentials", "token", "secret", "password", "auth", "id_rsa",
        "id_ed25519", "id_ecdsa", "id_dsa", ".git-credentials", ".netrc",
        "hosts.yml", "config", "passwd",
    ])
    default_excludes:   list[str]      = Field(default_factory=lambda: [
        r"C:\Windows\WinSxS",
        r"C:\Windows\SoftwareDistribution",
        r"$Recycle.Bin",
        r"System Volume Information",
        r"C:\Windows\Temp",
        r"C:\Program Files\WindowsApps",
    ])

    def effective_max_threads(self) -> int:
        """Return threads to use, respecting mode defaults."""
        if self.max_threads > 0:
            return self.max_threads
        return {
            OperationMode.PERFORMANCE: 16,
            OperationMode.SAFE:        4,
            OperationMode.INTERACTIVE: 4,
            OperationMode.TURBO:       8,
            OperationMode.DEEP:        8,
            OperationMode.QUICK:       8,
        }.get(self.mode, 4)

    def effective_progress_interval(self) -> int:
        """Return progress update interval in ms."""
        if self.progress_interval_ms != 500:
            return self.progress_interval_ms
        return {
            OperationMode.PERFORMANCE: 100,
            OperationMode.SAFE:        1000,
            OperationMode.INTERACTIVE: 500,
            OperationMode.TURBO:       200,
            OperationMode.DEEP:        500,
            OperationMode.QUICK:       200,
        }.get(self.mode, 500)

    def should_scan_file(self, filename: str) -> bool:
        """Return True if a file with this name should be analysed."""
        if self.mode == OperationMode.TURBO:
            ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            name_lower = filename.lower()
            return (
                ext in self.turbo_extensions
                or any(hp in name_lower for hp in self.high_priority_names)
            )
        return True   # SAFE / DEEP / PERFORMANCE / INTERACTIVE scan everything


class ScanSession(BaseModel):
    """Represents one complete scan session, persisted in the database."""
    id:              str      = Field(default_factory=lambda: str(uuid.uuid4()))
    started_at:      datetime = Field(default_factory=datetime.now)
    completed_at:    datetime | None = None
    root_path:       str      = ""
    mode:            str      = OperationMode.SAFE
    total_files:     int      = 0
    total_findings:  int      = 0
    status:          ScanStatus = ScanStatus.PENDING
    checkpoint_data: str      = ""  # JSON-serialised traversal state
    error_message:   str      = ""


class VaultEntry(BaseModel):
    """Tracks a file that has been encrypted by the Vault."""
    id:              str      = Field(default_factory=lambda: str(uuid.uuid4()))
    original_path:   str      = ""
    encrypted_path:  str      = ""
    original_hash:   str      = ""   # SHA-256 hex digest
    encrypted_at:    datetime = Field(default_factory=datetime.now)
    decrypted_at:    datetime | None = None
    in_auto_schedule: bool    = False
    file_size:       int      = 0


class MonitorWhitelistEntry(BaseModel):
    """A path that the Monitor Mode should never alert on."""
    id:       str      = Field(default_factory=lambda: str(uuid.uuid4()))
    path:     str      = ""
    added_at: datetime = Field(default_factory=datetime.now)
    note:     str      = ""


class RemediationSuggestion(BaseModel):
    """Auto-generated remediation advice for a given data_type."""
    data_type:   str
    description: str
    url:         str | None = None
    command:     str | None = None
    priority:    int        = 1   # lower = more urgent


class AppSignature(BaseModel):
    """
    Signature of a single application that may store credentials.

    Used by AppFingerprinter to map file paths back to the owning app.
    """
    id:                   str
    display_name:         str
    category:             str = "other"
    paths:                list[str] = Field(default_factory=list)
    process_names:        list[str] = Field(default_factory=list)
    registry_keys:        list[str] = Field(default_factory=list)
    credential_locations: list[dict[str, Any]] = Field(default_factory=list)
    icon:                 str | None = None
    confidence:           Confidence = Confidence.HIGH
    notes:                str | None = None
    reference_urls:       list[str]  = Field(default_factory=list)
    first_seen:           datetime   = Field(default_factory=datetime.now)
    last_updated:         datetime   = Field(default_factory=datetime.now)
    last_updated_source:  str        = "manual"


class AppSignaturesDB(BaseModel):
    """Versioned database of all known AppSignatures."""
    version:           str      = "1.0.0"
    timestamp:         datetime = Field(default_factory=datetime.now)
    apps:              list[AppSignature] = Field(default_factory=list)
    total_apps:        int      = 0
    last_update_check: datetime = Field(default_factory=datetime.now)

    def find_by_id(self, app_id: str) -> AppSignature | None:
        """Lookup an AppSignature by its ID."""
        return next((a for a in self.apps if a.id == app_id), None)
