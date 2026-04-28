"""Pydantic-based configuration models for Data-Shield."""

from typing import Optional
from pathlib import Path
from pydantic import BaseModel, Field, field_validator


class ScanConfig(BaseModel):
    """Scanning configuration."""

    mode: str = Field(default="safe", description="Scan mode: fast, safe, interactive")
    max_file_size: int = Field(default=104857600, description="Max file size in bytes (100MB)")
    thread_count: int = Field(default=4, description="Number of scan threads")
    timeout: int = Field(default=300, description="Scan timeout in seconds")
    resume: bool = Field(default=True, description="Enable checkpoint/resume")
    exclude_dirs: list[str] = Field(
        default_factory=lambda: [
            "node_modules",
            "venv",
            ".git",
            "__pycache__",
            "dist",
            "build",
        ],
        description="Directories to exclude",
    )

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        """Validate scan mode."""
        valid_modes = ("ultra_fast", "fast", "safe", "deep", "interactive")
        if v not in valid_modes:
            raise ValueError(f"mode must be one of {valid_modes}")
        return v


class VaultConfig(BaseModel):
    """Vault encryption configuration."""

    master_key_path: Optional[Path] = Field(default=None, description="Path to master key")
    vault_path: Path = Field(
        default_factory=lambda: Path.home() / ".datashield" / "vault.db",
        description="Vault database path",
    )
    cipher: str = Field(default="AES-256-GCM", description="Encryption cipher")
    hash_algorithm: str = Field(default="pbkdf2", description="Hashing algorithm")
    auto_lock_minutes: int = Field(default=15, description="Auto-lock timeout")


class MonitorConfig(BaseModel):
    """Real-time monitoring configuration."""

    enabled: bool = Field(default=False, description="Enable monitoring")
    watch_dirs: list[str] = Field(default_factory=list, description="Directories to watch")
    check_interval: int = Field(default=5, description="Check interval in seconds")
    alert_threshold: int = Field(default=70, description="Risk score threshold for alerts")


class AppConfig(BaseModel):
    """Root application configuration."""

    scan: ScanConfig = Field(default_factory=ScanConfig)
    vault: VaultConfig = Field(default_factory=VaultConfig)
    monitor: MonitorConfig = Field(default_factory=MonitorConfig)
    log_level: str = Field(default="INFO", description="Logging level")
    data_dir: Path = Field(
        default_factory=lambda: Path.home() / ".datashield",
        description="Data directory",
    )
    database_url: str = Field(
        default="sqlite:///:memory:", description="Database URL"
    )

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True
