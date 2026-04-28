"""Data-Shield main entry point."""

from .cli import main as cli_main


def main():
    """Main entry point for datashield command."""
    cli_main()


def admin_main():
    """Admin entry point for datashield-admin command."""
    # Admin commands (signature updates, etc.)
    cli_main()


if __name__ == "__main__":
    main()
