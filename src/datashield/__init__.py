"""Data-Shield package initialization."""

__version__ = "0.1.0"
__author__ = "Data-Shield Team"

from .core.models import Finding, ScanSession
from .config.loader import load_config
from .storage.database import init_db
from .core.scanner import Scanner

__all__ = [
    "__version__",
    "__author__",
    "Finding",
    "ScanSession",
    "load_config",
    "init_db",
    "Scanner",
]
