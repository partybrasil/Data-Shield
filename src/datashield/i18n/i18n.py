"""Internationalization support."""

import json
from pathlib import Path
from typing import Optional, Dict


class I18n:
    """Internationalization manager."""

    def __init__(self, language: str = "es"):
        """Initialize i18n.

        Args:
            language: Language code ('es' or 'en')
        """
        self.language = language
        self.translations: Dict[str, str] = {}
        self.load_language(language)

    def load_language(self, language: str):
        """Load language translations.

        Args:
            language: Language code
        """
        # Default translations
        if language == "en":
            self.translations = {
                "scan": "Scan",
                "vault": "Vault",
                "monitor": "Monitor",
                "export": "Export",
                "target_path": "Target Path",
                "start_scan": "Start Scan",
                "scanning": "Scanning...",
                "found_credentials": "Found {count} credentials",
                "no_credentials": "No credentials found",
                "error": "Error",
                "success": "Success",
                "cancel": "Cancel",
                "ok": "OK",
                "exit": "Exit",
                "about": "About",
                "theme": "Toggle Theme",
                "help": "Help",
                "file": "File",
                "view": "View",
                "vault_locked": "Vault: Locked",
                "vault_unlocked": "Vault: Unlocked",
                "unlock": "Unlock",
                "lock": "Lock",
            }
        else:  # Spanish (default)
            self.translations = {
                "scan": "Escanear",
                "vault": "Bóveda",
                "monitor": "Monitor",
                "export": "Exportar",
                "target_path": "Ruta de Destino",
                "start_scan": "Iniciar Escaneo",
                "scanning": "Escaneando...",
                "found_credentials": "Se encontraron {count} credenciales",
                "no_credentials": "No se encontraron credenciales",
                "error": "Error",
                "success": "Éxito",
                "cancel": "Cancelar",
                "ok": "Aceptar",
                "exit": "Salir",
                "about": "Acerca de",
                "theme": "Cambiar Tema",
                "help": "Ayuda",
                "file": "Archivo",
                "view": "Ver",
                "vault_locked": "Bóveda: Bloqueada",
                "vault_unlocked": "Bóveda: Desbloqueada",
                "unlock": "Desbloquear",
                "lock": "Bloquear",
            }

        self.language = language

    def translate(self, key: str, **kwargs) -> str:
        """Get translation for key.

        Args:
            key: Translation key
            **kwargs: Format arguments

        Returns:
            Translated string
        """
        text = self.translations.get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text

    def t(self, key: str, **kwargs) -> str:
        """Shorthand for translate.

        Args:
            key: Translation key
            **kwargs: Format arguments

        Returns:
            Translated string
        """
        return self.translate(key, **kwargs)

    def set_language(self, language: str):
        """Set current language.

        Args:
            language: Language code
        """
        self.load_language(language)

    def get_language(self) -> str:
        """Get current language code.

        Returns:
            Language code
        """
        return self.language
