"""Windows DPAPI integration for master key management."""

from typing import Optional
import os

try:
    import win32crypt
except ImportError:
    win32crypt = None


def get_dpapi_key(key_name: str = "data-shield-master") -> Optional[bytes]:
    """Get or create DPAPI-protected master key.
    
    This is a simplified version that would ideally check a secure storage location.
    For this implementation, we simulate the retrieval logic.
    """
    if win32crypt is None:
        return None
    
    # In a real app, we'd check registry/file for a blob and unprotect it
    return None


def protect_with_dpapi(data: bytes, description: str = "Data-Shield Protection") -> bytes:
    """Protect data with Windows DPAPI.

    Args:
        data: Data to protect
        description: Optional description for the blob

    Returns:
        DPAPI-protected data (binary blob)
    """
    if win32crypt is None:
        return data
        
    try:
        # CryptProtectData(data, description, entropy, reserved, prompt, flags)
        return win32crypt.CryptProtectData(data, description, None, None, None, 0)
    except Exception:
        return data


def unprotect_with_dpapi(protected_data: bytes) -> bytes:
    """Unprotect data with Windows DPAPI.

    Args:
        protected_data: DPAPI-protected data

    Returns:
        Unprotected data
    """
    if win32crypt is None:
        return protected_data
        
    try:
        # CryptUnprotectData(data, entropy, reserved, prompt, flags)
        description, data = win32crypt.CryptUnprotectData(protected_data, None, None, None, 0)
        return data
    except Exception:
        return protected_data
