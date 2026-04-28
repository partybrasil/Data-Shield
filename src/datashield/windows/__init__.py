"""Windows-specific integration."""

import os
import ctypes
import winreg
from typing import List, Optional

try:
    import win32cred
except ImportError:
    win32cred = None


def request_elevation() -> bool:
    """Request UAC elevation if needed.

    Returns:
        True if already elevated or elevation successful.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def get_credential_manager_entries() -> List[dict]:
    """Get entries from Windows Credential Manager.

    Returns:
        List of credential entries.
    """
    if win32cred is None:
        return []
        
    entries = []
    try:
        # CRED_TYPE_GENERIC = 1
        creds = win32cred.CredEnumerate(None, 0)
        for cred in creds:
            entries.append({
                "target": cred["TargetName"],
                "type": cred["Type"],
                "user": cred["UserName"],
                "last_written": str(cred["LastWritten"]),
            })
    except Exception:
        pass
    return entries


def scan_registry_for_credentials() -> List[str]:
    """Scan Windows Registry for common credential storage paths.

    Returns:
        List of registry paths with potential credentials.
    """
    paths_to_check = [
        (winreg.HKEY_CURRENT_USER, r"Software\OpenSSH\Agent\Keys"),
        (winreg.HKEY_CURRENT_USER, r"Software\SimonTatham\PuTTY\Sessions"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\LogonUI"),
    ]
    
    findings = []
    for hkey, subkey in paths_to_check:
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                findings.append(f"{'HKLM' if hkey == winreg.HKEY_LOCAL_MACHINE else 'HKCU'}\\{subkey}")
        except FileNotFoundError:
            continue
        except Exception:
            continue
            
    return findings


def show_notification(title: str, message: str, icon: str = "info"):
    """Show Windows notification.

    Args:
        title: Notification title
        message: Notification message
        icon: Icon type (info, warning, error)
    """
    try:
        from winotify import Notification

        notif = Notification(app_id="Data-Shield", title=title, msg=message)
        notif.show()
    except Exception:
        # Fallback to simple print if winotify fails
        print(f"NOTIFICATION: {title} - {message}")
