"""Vault module initialization."""

from .vault import Vault
from .dpapi import get_dpapi_key, protect_with_dpapi, unprotect_with_dpapi
from .scheduler import SchedulerConfig, schedule_vault_lock, schedule_auto_scan

__all__ = [
    "Vault",
    "get_dpapi_key",
    "protect_with_dpapi",
    "unprotect_with_dpapi",
    "SchedulerConfig",
    "schedule_vault_lock",
    "schedule_auto_scan",
]
