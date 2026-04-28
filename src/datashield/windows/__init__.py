"""Windows-specific integration."""

from typing import List, Optional


def request_elevation() -> bool:
    """Request UAC elevation if needed.

    Returns:
        True if already elevated or elevation successful.
    """
    import ctypes

    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def get_credential_manager_entries() -> List[dict]:
    """Get entries from Windows Credential Manager.

    Returns:
        List of credential entries.
    """
    # Stub implementation - full requires pypyodpt or cmdkey parsing
    return []


def scan_registry_for_credentials() -> List[str]:
    """Scan Windows Registry for stored credentials.

    Returns:
        List of registry paths with potential credentials.
    """
    # Stub implementation - full requires winreg module
    return []


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
        pass
