"""CLI interface for Data-Shield."""

import click
from pathlib import Path
from typing import Optional, List
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
    type=click.Choice(["ultra_fast", "fast", "safe", "deep", "interactive"]),
    default="safe",
    help="Scan mode",
)
@click.option("--max-size", type=int, default=104857600, help="Max file size (bytes)")
@click.option("--threads", type=int, default=4, help="Number of threads")
def scan(path: str, mode: str, max_size: int, threads: int):
    """Scan for sensitive credentials."""
    config = load_config()
    config.scan.mode = mode
    config.scan.max_file_size = max_size
    
    # Interactive mode requires single-threading for clean terminal I/O
    if mode == "interactive":
        threads = 1
    config.scan.thread_count = threads

    # Initialize database
    SessionLocal = init_db(str(config.database_url))
    session = get_session(SessionLocal)

    # Create scanner
    event_bus = EventBus()
    scanner = Scanner(config.scan, SessionLocal, event_bus)

    # Interactive handler
    def progress_callback(current, total, finding=None):
        if finding:
            if mode == "interactive":
                console.print(f"\n[bold yellow]⚠ FINDING DETECTED[/bold yellow]")
                console.print(f"File: [cyan]{finding['file_path']}[/cyan]")
                console.print(f"Type: [magenta]{finding['pattern_name']}[/magenta]")
                console.print(f"Software: [green]{finding.get('software', 'Unknown')}[/green]")
                
                action = click.prompt(
                    "Action",
                    type=click.Choice(["s", "v", "q"]),
                    default="s",
                    show_choices=False,
                    prompt_suffix=" (Skip / Save to Vault / Quit scan) [s]"
                )
                
                if action == "v":
                    try:
                        from ..vault.vault import Vault
                        from ..storage.repository import VaultRepository
                        from ..storage.database import VaultEntry
                        import uuid
                        
                        v = Vault()
                        if v.is_locked:
                            pwd = click.prompt("Vault is locked. Enter Master Password", hide_input=True)
                            if not v.unlock(pwd):
                                console.print("[red]Invalid password. Skipping vault save.[/red]")
                                return
                        
                        match_text = finding.get("match_text", "N/A")
                        ct, iv, tag = v.encrypt(match_text)
                        
                        repo = VaultRepository(session)
                        entry = VaultEntry(
                            id=str(uuid.uuid4()),
                            finding_id=finding["id"],
                            encrypted_value=ct,
                            iv=iv,
                            tag=tag
                        )
                        repo.create(entry)
                        session.commit()
                        console.print("[green]✓ Saved to vault successfully![/green]")
                    except Exception as e:
                        console.print(f"[red]Error saving to vault: {e}[/red]")
                elif action == "q":
                    scanner.stop()
                    console.print("[yellow]Stopping scan...[/yellow]")
        else:
            if current >= 0:
                console.print(f"[cyan]Progress: {current}/{total}[/cyan]", end="\r")

    try:
        if mode == "interactive":
            console.print("[bold green]Starting Interactive Scan...[/bold green]")
            session_id = scanner.scan(path, callback=progress_callback)
        else:
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
@click.argument("action", type=click.Choice(["lock", "unlock", "status"]))
@click.option("--password", prompt=True, hide_input=True, required=False, help="Master password")
def vault(action: str, password: Optional[str] = None):
    """Manage credential vault (encrypt/decrypt)."""
    from ..vault.vault import Vault
    
    vault_inst = Vault()
    
    if action == "status":
        status = "Locked" if vault_inst.is_locked else "Unlocked"
        console.print(f"Vault Status: [bold]{status}[/bold]")
        return

    if not password:
        password = click.prompt("Enter master password", hide_input=True)

    if action == "unlock":
        if vault_inst.unlock(password):
            console.print("[green]✓ Vault unlocked successfully[/green]")
        else:
            console.print("[red]✗ Invalid password[/red]")
    elif action == "lock":
        vault_inst.lock()
        console.print("[yellow]Vault locked[/yellow]")


@cli.command()
@click.option("--dir", "directories", multiple=True, help="Directories to monitor")
@click.option("--threshold", type=int, default=70, help="Risk threshold for alerts")
def monitor(directories: List[str], threshold: int):
    """Monitor for new credentials in real-time."""
    from ..monitor.monitor import Monitor
    from ..core.pattern_engine import PatternEngine
    from ..core.events import EventBus
    
    if not directories:
        directories = [str(Path.home())]
        
    engine = PatternEngine()
    bus = EventBus()
    monitor_inst = Monitor(engine, bus, alert_threshold=threshold, watch_dirs=list(directories))
    
    console.print(f"[bold green]Monitoring started on {len(directories)} directories...[/bold green]")
    console.print("[dim]Press Ctrl+C to stop[/dim]")
    
    try:
        monitor_inst.start()
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor_inst.stop()
        console.print("\n[yellow]Monitoring stopped[/yellow]")


@cli.command()
@click.argument("format", type=click.Choice(["json", "csv", "txt", "html"]))
@click.option("--output", type=click.Path(), help="Output file path")
@click.option("--session", "session_id", help="Session ID to export")
def export(format: str, output: Optional[str], session_id: Optional[str]):
    """Export findings to various formats."""
    from ..export.exporter import Exporter
    from ..storage.database import init_db, get_session
    from ..core.findings import FindingService
    from ..config.loader import load_config
    
    config = load_config()
    SessionLocal = init_db(str(config.database_url))
    db_session = get_session(SessionLocal)
    
    try:
        service = FindingService(db_session)
        if not session_id:
            # Get latest session
            latest_session = service.get_latest_session()
            if not latest_session:
                console.print("[red]No scan sessions found[/red]")
                return
            session_id = latest_session.id
        
        scan_session = service.get_session(session_id)
        findings = service.get_session_findings(session_id)
        
        if not findings:
            console.print(f"[yellow]No findings found for session {session_id}[/yellow]")
            return
            
        exporter = Exporter(output_dir=Path(output).parent if output else None)
        filename = Path(output).name if output else f"export_{session_id}.{format}"
        
        path = None
        if format == "json":
            path = exporter.to_json(findings, scan_session, filename)
        elif format == "csv":
            path = exporter.to_csv(findings, filename)
        elif format == "txt":
            path = exporter.to_txt(findings, scan_session, filename)
        elif format == "html":
            path = exporter.to_html(findings, scan_session, filename)
            
        console.print(f"[green]✓ Exported {len(findings)} findings to {path}[/green]")
        
    finally:
        db_session.close()


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
