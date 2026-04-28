"""
Data-Shield custom exception hierarchy.

All exceptions raised by Data-Shield derive from DataShieldError so callers
can catch the base class without accidentally swallowing unrelated exceptions.
"""


class DataShieldError(Exception):
    """Base exception for all Data-Shield errors."""


# ── Scanner ──────────────────────────────────────────────────────────────────

class ScanError(DataShieldError):
    """Raised when the scanner encounters an unrecoverable error."""


class ScanAbortedError(ScanError):
    """Raised when the user explicitly aborts a scan."""


class ScanCheckpointError(ScanError):
    """Raised when a checkpoint cannot be saved or loaded."""


class DepthLimitError(ScanError):
    """Raised when a path exceeds the user-configured depth limit."""


# ── Pattern Engine ────────────────────────────────────────────────────────────

class PatternEngineError(DataShieldError):
    """Raised for failures inside the pattern-matching engine."""


class YaraCompileError(PatternEngineError):
    """Raised when a YARA rule fails to compile."""


class EntropyError(PatternEngineError):
    """Raised when entropy analysis cannot be performed on a file."""


# ── Vault ─────────────────────────────────────────────────────────────────────

class VaultError(DataShieldError):
    """Base class for Vault-related errors."""


class VaultAuthError(VaultError):
    """Raised when the master password is wrong or missing."""


class VaultIntegrityError(VaultError):
    """Raised when an encrypted file fails GCM authentication (tampering)."""


class VaultAlreadyEncryptedError(VaultError):
    """Raised when trying to encrypt a file that is already encrypted."""


class VaultNotEncryptedError(VaultError):
    """Raised when trying to decrypt a file that is not a .ds-vault file."""


class VaultSchedulerError(VaultError):
    """Raised when Windows Task Scheduler integration fails."""


# ── Storage ───────────────────────────────────────────────────────────────────

class StorageError(DataShieldError):
    """Raised for database / persistence failures."""


class MigrationError(StorageError):
    """Raised when a schema migration fails."""


# ── Windows Integration ───────────────────────────────────────────────────────

class WindowsError(DataShieldError):
    """Base class for Windows-specific integration errors."""


class ElevationError(WindowsError):
    """Raised when UAC elevation cannot be performed."""


class CredentialManagerError(WindowsError):
    """Raised when Windows Credential Manager access fails."""


class RegistryScanError(WindowsError):
    """Raised when registry scanning encounters an error."""


# ── Export ────────────────────────────────────────────────────────────────────

class ExportError(DataShieldError):
    """Raised when an export operation fails."""


# ── Configuration ─────────────────────────────────────────────────────────────

class ConfigError(DataShieldError):
    """Raised when configuration loading or validation fails."""


class ProfileNotFoundError(ConfigError):
    """Raised when a named scan profile does not exist."""


# ── Monitor ───────────────────────────────────────────────────────────────────

class MonitorError(DataShieldError):
    """Raised when the file-system monitor encounters an error."""
