"""
remnant why
-----------
Record and retrieve the human reason behind a file,
folder, config, or any path on your system.

Usage:
    remnant why set ./config "Exists because of Ubuntu 22.04 bug"
    remnant why get ./config
    remnant why list
    remnant why search "ubuntu"
    remnant why remove ./config
    remnant why history ./config
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from remnant.core.database import db, init_db
from remnant.output.terminal import (
    confirm,
    print_error,
    print_header,
    print_info,
    print_key_value,
    print_success,
    print_table,
    print_warning,
)

app = typer.Typer(
    help="Record and retrieve WHY files and configs exist.",
    no_args_is_help=True,
)


def _resolve_path(path: str) -> str:
    """Normalize a path to an absolute string."""
    return str(Path(path).resolve())


def _get_reason(path: str) -> dict | None:
    """Fetch a reason record from the database."""
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM reasons WHERE path = ?", (path,)
        ).fetchone()
    return dict(row) if row else None


# ── Commands ──────────────────────────────────────────────────────────────────

@app.command("set")
def set_reason(
    path: str = typer.Argument(..., help="File or folder path"),
    reason: str = typer.Argument(..., help="Why this path exists"),
) -> None:
    """Set or update the reason for a path."""
    init_db()
    resolved = _resolve_path(path)

    with db() as conn:
        existing = conn.execute(
            "SELECT id FROM reasons WHERE path = ?", (resolved,)
        ).fetchone()

        if existing:
            conn.execute(
                """UPDATE reasons
                   SET reason = ?, updated_at = datetime('now')
                   WHERE path = ?""",
                (reason, resolved),
            )
            print_success(f"Updated reason for [bold]{path}[/bold]")
        else:
            conn.execute(
                "INSERT INTO reasons (path, reason) VALUES (?, ?)",
                (resolved, reason),
            )
            print_success(f"Recorded reason for [bold]{path}[/bold]")


@app.command("get")
def get_reason(
    path: str = typer.Argument(..., help="File or folder path"),
) -> None:
    """Get the reason for a path."""
    init_db()
    resolved = _resolve_path(path)
    record = _get_reason(resolved)

    if not record:
        print_warning(f"No reason recorded for [bold]{path}[/bold]")
        print_info("Use: remnant why set <path> \"<reason>\"")
        raise typer.Exit(1)

    print_header(f"WHY: {path}")
    print_key_value("Reason",   record["reason"])
    print_key_value("Recorded", record["created_at"][:10])
    if record["created_at"] != record["updated_at"]:
        print_key_value("Last updated", record["updated_at"][:10])


@app.command("list")
def list_reasons(
    limit: int = typer.Option(20, "--limit", "-n", help="Max results to show"),
) -> None:
    """List all recorded reasons."""
    init_db()

    with db() as conn:
        rows = conn.execute(
            """SELECT path, reason, updated_at
               FROM reasons
               ORDER BY updated_at DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()

    if not rows:
        print_info("No reasons recorded yet.")
        print_info("Use: remnant why set <path> \"<reason>\"")
        return

    print_header(f"ALL REASONS ({len(rows)})")
    print_table(
        columns=["Path", "Reason", "Updated"],
        rows=[[r["path"], r["reason"][:60], r["updated_at"][:10]] for r in rows],
    )


@app.command("search")
def search_reasons(
    query: str = typer.Argument(..., help="Search term"),
) -> None:
    """Search reasons by keyword."""
    init_db()

    with db() as conn:
        rows = conn.execute(
            """SELECT path, reason, updated_at
               FROM reasons
               WHERE reason LIKE ? OR path LIKE ?
               ORDER BY updated_at DESC""",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()

    if not rows:
        print_info(f"No results for [bold]{query}[/bold]")
        return

    print_header(f"SEARCH: {query} ({len(rows)} results)")
    print_table(
        columns=["Path", "Reason", "Updated"],
        rows=[[r["path"], r["reason"][:60], r["updated_at"][:10]] for r in rows],
    )


@app.command("remove")
def remove_reason(
    path: str = typer.Argument(..., help="File or folder path"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Remove the reason for a path."""
    init_db()
    resolved = _resolve_path(path)
    record = _get_reason(resolved)

    if not record:
        print_error(f"No reason recorded for: {path}")
        raise typer.Exit(1)

    if not force and not confirm(f"Remove reason for {path}?"):
        print_info("Cancelled.")
        return

    with db() as conn:
        conn.execute("DELETE FROM reasons WHERE path = ?", (resolved,))

    print_success(f"Removed reason for [bold]{path}[/bold]")


@app.command("history")
def history_reason(
    path: str = typer.Argument(..., help="File or folder path"),
) -> None:
    """Show full details for a path's reason record."""
    init_db()
    resolved = _resolve_path(path)
    record = _get_reason(resolved)

    if not record:
        print_warning(f"No reason recorded for [bold]{path}[/bold]")
        raise typer.Exit(1)

    print_header(f"HISTORY: {path}")
    print_key_value("Resolved path", resolved)
    print_key_value("Reason",        record["reason"])
    print_key_value("First recorded", record["created_at"])
    print_key_value("Last updated",   record["updated_at"])
