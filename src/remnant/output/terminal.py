"""
remnant.output.terminal
------------------------
All terminal output goes through here.
Using Rich for beautiful, consistent formatting.
"""

from __future__ import annotations

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()
err_console = Console(stderr=True, style="bold red")


def print_header(title: str) -> None:
    """Print a section header."""
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print("─" * len(title), style="dim")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str) -> None:
    """Print an error message to stderr."""
    err_console.print(f"✗ {message}")


def print_warning(message: str) -> None:
    """Print a warning."""
    console.print(f"[bold yellow]![/bold yellow] {message}")


def print_info(message: str) -> None:
    """Print an informational message."""
    console.print(f"[dim]{message}[/dim]")


def print_key_value(key: str, value: str, key_width: int = 20) -> None:
    """Print a key-value pair, nicely aligned."""
    console.print(f"[bold]{key:<{key_width}}[/bold] {value}")


def print_panel(content: str, title: str = "", style: str = "cyan") -> None:
    """Print content inside a panel."""
    console.print(Panel(content, title=title, border_style=style))


def make_table(columns: list[str], rows: list[list[str]], title: str = "") -> Table:
    """Build and return a Rich table."""
    table = Table(title=title, box=box.SIMPLE, show_header=True, header_style="bold cyan")
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*row)
    return table


def print_table(columns: list[str], rows: list[list[str]], title: str = "") -> None:
    """Print a formatted table."""
    table = make_table(columns, rows, title)
    console.print(table)


def confirm(prompt: str) -> bool:
    """Ask the user for yes/no confirmation."""
    answer = console.input(f"[bold yellow]?[/bold yellow] {prompt} [dim](y/N)[/dim] ")
    return answer.strip().lower() in ("y", "yes")
