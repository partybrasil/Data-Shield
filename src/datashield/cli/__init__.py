"""CLI interface for Data-Shield."""

import click
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import Session

from ..config.loader import load_config
from ..storage.database import init_db, get_session
from ..core.scanner import Scanner
from ..core.events import EventBus
from ..config.settings import ScanConfig

console = Console()


@click.group()
def cli():
    """Data-Shield: Sensitive credential scanner and encryption vault."""
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option(
    "--mode",
    type=click.Choice(["fast", "safe", "interactive"]),
    default="safe",
    help="Scan mode",
)
@click.option("--max-size", type=int, default=104857600, help="Max file size (bytes)")
@click.option("--threads", type=int, default=4, help="Number of threads")
def scan(path: str, mode: str, max_size: int, threads: int):
    """Scan for sensitive credentials.

    Supports 3 modes:
    - fast: Quick scan, minimal checks
    - safe: Balanced speed and accuracy (default)
    - interactive: Pause on findings for user review
    """
    config = load_config()
    config.scan.mode = mode
    config.scan.max_file_size = max_size
    config.scan.thread_count = threads

    # Initialize database
    SessionLocal = init_db(str(config.database_url))
    session = get_session(SessionLocal)

    # Create scanner
    event_bus = EventBus()
    scanner = Scanner(config.scan, session, event_bus)

    # Simple progress callback
    def progress_callback(current, total):
        console.print(f"[cyan]Progress: {current}/{total}[/cyan]", end="\r")

    try:
        with console.status("[bold green]Scanning...[/bold green]") as status:
            session_id = scanner.scan(path, callback=progress_callback)

        # Display results
        from ..core.findings import FindingService

        service = FindingService(session)
        findings = service.get_session_findings(session_id)

        if findings:
            table = Table(title=f"Found {len(findings)} credentials")
            table.add_column("File", style="cyan")
            table.add_column("Pattern", style="magenta")
            table.add_column("Risk", style="red")

            for finding in findings[:100]:  # Show first 100
                table.add_row(finding.file_path, finding.pattern_name, f"{finding.risk_score:.0%}")

            console.print(table)
        else:
            console.print("[green]✓ No credentials found[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        session.close()


@cli.command()
def vault():
    """Manage credential vault (encrypt/decrypt)."""
    console.print("[yellow]Vault management - coming in Phase 2[/yellow]")


@cli.command()
def monitor():
    """Monitor for new credentials in real-time."""
    console.print("[yellow]Real-time monitoring - coming in Phase 2[/yellow]")


@cli.command()
def export():
    """Export findings to various formats."""
    console.print("[yellow]Export functionality - coming in Phase 2[/yellow]")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
