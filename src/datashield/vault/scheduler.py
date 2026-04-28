"""Task Scheduler integration for automatic vault operations."""

import subprocess
import sys
from typing import Optional
from datetime import time
from pathlib import Path


class SchedulerConfig:
    """Configuration for automatic vault operations."""

    def __init__(
        self,
        enabled: bool = False,
        auto_lock_time: Optional[time] = None,
        auto_encrypt_time: Optional[time] = None,
        auto_scan_time: Optional[time] = None,
    ):
        """Initialize scheduler config."""
        self.enabled = enabled
        self.auto_lock_time = auto_lock_time
        self.auto_encrypt_time = auto_encrypt_time
        self.auto_scan_time = auto_scan_time


def schedule_vault_lock(task_name: str = "DataShield-AutoLock", time_str: str = "17:00"):
    """Schedule automatic vault lock via Windows Task Scheduler.

    Args:
        task_name: Name of task in Task Scheduler
        time_str: Time in HH:MM format
    """
    try:
        # Get path to current executable or python script
        exe_path = sys.executable
        script_path = Path(__file__).parents[2] / "__main__.py"
        
        cmd = [
            "schtasks", "/create", "/tn", task_name,
            "/tr", f'"{exe_path}" "{script_path}" vault lock',
            "/sc", "daily", "/st", time_str, "/f"
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except Exception:
        return False


def schedule_auto_scan(task_name: str = "DataShield-AutoScan", frequency: str = "daily"):
    """Schedule automatic credential scan.

    Args:
        task_name: Name of task
        frequency: 'daily', 'weekly', 'monthly'
    """
    try:
        exe_path = sys.executable
        script_path = Path(__file__).parents[2] / "__main__.py"
        
        cmd = [
            "schtasks", "/create", "/tn", task_name,
            "/tr", f'"{exe_path}" "{script_path}" scan --mode safe',
            "/sc", frequency, "/st", "03:00", "/f"
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except Exception:
        return False


def remove_scheduled_task(task_name: str):
    """Remove scheduled task.

    Args:
        task_name: Name of task to remove
    """
    try:
        subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], check=True, capture_output=True)
        return True
    except Exception:
        return False
