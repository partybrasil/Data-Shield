"""Encryption vault for Data-Shield."""

import os
from pathlib import Path
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import bcrypt


class Vault:
    """AES-256-GCM encryption vault with PBKDF2 + bcrypt."""

    def __init__(self, vault_path: Path = None, master_password: str = None):
        """Initialize vault.

        Args:
            vault_path: Path to vault database
            master_password: Master password for encryption
        """
        self.vault_path = vault_path or Path.home() / ".datashield" / "vault.db"
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        self.master_key = None
        self.is_locked = True

        if master_password:
            self.master_key = self._derive_key(master_password)
            self.is_locked = False

    def _derive_key(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """Derive encryption key from password using PBKDF2.

        Args:
            password: Master password
            salt: Optional salt (generated if not provided)

        Returns:
            32-byte key for AES-256
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        return kdf.derive(password.encode())

    def encrypt(self, plaintext: str) -> Tuple[str, str, str]:
        """Encrypt sensitive data.

        Args:
            plaintext: Data to encrypt

        Returns:
            Tuple of (ciphertext_hex, iv_hex, tag_hex)
        """
        if self.is_locked or not self.master_key:
            raise ValueError("Vault is locked")

        # Generate random IV
        iv = os.urandom(12)

        # Create cipher
        cipher = AESGCM(self.master_key)

        # Encrypt
        ciphertext = cipher.encrypt(iv, plaintext.encode(), None)

        # Split ciphertext and tag
        ct = ciphertext[:-16]
        tag = ciphertext[-16:]

        return (
            ct.hex(),
            iv.hex(),
            tag.hex(),
        )

    def decrypt(self, ciphertext_hex: str, iv_hex: str, tag_hex: str) -> str:
        """Decrypt sensitive data.

        Args:
            ciphertext_hex: Encrypted data (hex)
            iv_hex: Initialization vector (hex)
            tag_hex: Authentication tag (hex)

        Returns:
            Decrypted plaintext
        """
        if self.is_locked or not self.master_key:
            raise ValueError("Vault is locked")

        iv = bytes.fromhex(iv_hex)
        ct = bytes.fromhex(ciphertext_hex)
        tag = bytes.fromhex(tag_hex)

        cipher = AESGCM(self.master_key)

        try:
            plaintext = cipher.decrypt(iv, ct + tag, None)
            return plaintext.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

    def lock(self):
        """Lock vault."""
        self.master_key = None
        self.is_locked = True

    def unlock(self, password: str) -> bool:
        """Unlock vault with password.

        Args:
            password: Master password

        Returns:
            True if unlocked successfully
        """
        try:
            key = self._derive_key(password)
            self.master_key = key
            self.is_locked = False
            return True
        except Exception:
            return False

    def set_password(self, new_password: str) -> None:
        """Set or change master password.

        Args:
            new_password: New master password
        """
        self.master_key = self._derive_key(new_password)
        self.is_locked = False
