"""Data-Shield main entry point with CLI/GUI detection."""

import sys
from pathlib import Path


def should_launch_gui(args):
    """Determine if GUI should launch.

    Args:
        args: Command line arguments

    Returns:
        True if GUI should launch
    """
    if not args:
        return True
    if "--gui" in args:
        return True
    if "--help" in args or "-h" in args:
        return False
        
    cli_commands = ["scan", "vault", "monitor", "export", "history"]
    if args and args[0] in cli_commands:
        return False
        
    return True


def main():
    """Main entry point for datashield command."""
    if should_launch_gui(sys.argv[1:]):
        # Launch GUI
        try:
            from .gui.app import GuiApp
            from .config.loader import load_config
            from .storage.database import init_db, get_session
            from .core.scanner import Scanner
            from .core.pattern_engine import PatternEngine
            from .core.events import EventBus
            from .vault.vault import Vault
            from .monitor.monitor import Monitor
            from .export.exporter import Exporter

            # Initialize components
            config = load_config()
            SessionLocal = init_db(str(config.database_url))

            scanner = Scanner(config.scan, SessionLocal, EventBus())
            vault = Vault()
            monitor = Monitor(PatternEngine(), EventBus())
            exporter = Exporter()

            # Launch GUI
            app = GuiApp(scanner, vault, monitor, exporter)
            sys.exit(app.run())
        except ImportError:
            print("GUI dependencies not installed. Install with: pip install -e '.[gui]'")
            sys.exit(1)
    else:
        # Launch CLI
        from .cli import main as cli_main

        cli_main()


def admin_main():
    """Admin entry point for datashield-admin command."""
    from .cli import main as cli_main

    # Admin commands (signature updates, etc.)
    cli_main()


if __name__ == "__main__":
    main()
