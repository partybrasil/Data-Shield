"""Default configuration for Data-Shield."""

from pathlib import Path
from .settings import AppConfig, ScanConfig, VaultConfig, MonitorConfig

# Default configuration instance
DEFAULT_CONFIG = AppConfig(
    scan=ScanConfig(
        mode="safe",
        max_file_size=104857600,  # 100MB
        thread_count=4,
        timeout=300,
        resume=True,
    ),
    vault=VaultConfig(
        vault_path=Path.home() / ".datashield" / "vault.db",
        cipher="AES-256-GCM",
        hash_algorithm="pbkdf2",
        auto_lock_minutes=15,
    ),
    monitor=MonitorConfig(
        enabled=False,
        check_interval=5,
        alert_threshold=70,
    ),
    log_level="INFO",
    data_dir=Path.home() / ".datashield",
    database_url="sqlite:///~/.datashield/datashield.db",
)
