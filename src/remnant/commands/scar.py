"""
remnant scar
------------
A personal incident knowledge base for your Linux machine.
When something breaks and you fix it — record it here.
Next time it breaks, you'll know exactly what to do.

Usage:
    remnant scar add
    remnant scar list
    remnant scar search "nvidia"
    remnant scar show 3
    remnant scar remove 3
"""

from __future__ import annotations

from typing import Optional

import typer

from remnant.core.database import db, init_db
from remnant.core.errors import NotFoundError
from remnant.output.terminal import (
    confirm,
    console,
    print_error,
    print_header,
    print_info,
    print_key_value,
    print_success,
    print_table,
    print_warning,
)

app = typer.Typer(
    help="Personal incident knowledge base — record what broke and how you fixed it.",
    no_args_is_help=True,
)


def _get_scar(scar_id: int) -> dict | None:
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM scars WHERE id = ?", (scar_id,)
        ).fetchone()
    return dict(row) if row else None


def _prompt(label: str, required: bool = True) -> str:
    """Prompt the user for input, re-asking if required and empty."""
    while True:
        value = console.input(f"[bold cyan]{label}:[/bold cyan] ").strip()
        if value or not required:
            return value
        print_warning("This field is required.")


# ── Commands ──────────────────────────────────────────────────────────────────

@app.command("add")
def add_scar() -> None:
    """Interactively record a new incident."""
    init_db()

    print_header("RECORD INCIDENT")
    print_info("Press Enter to skip optional fields.\n")

    title    = _prompt("Title (short summary)")
    problem  = _prompt("What broke?")
    cause    = _prompt("What caused it? (optional)", required=False)
    solution = _prompt("How did you fix it?")
    tags_raw = _prompt("Tags, space-separated (optional)", required=False)
    tags     = ",".join(tags_raw.split()) if tags_raw else ""

    with db() as conn:
        cursor = conn.execute(
            """INSERT INTO scars (title, problem, cause, solution, tags)
               VALUES (?, ?, ?, ?, ?)""",
            (title, problem, cause or None, solution, tags or None),
        )
        scar_id = cursor.lastrowid

    print_success(f"Incident recorded [dim](id: {scar_id})[/dim]")


@app.command("list")
def list_scars(
    limit: int = typer.Option(20, "--limit", "-n", help="Max results to show"),
) -> None:
    """List all recorded incidents."""
    init_db()

    with db() as conn:
        rows = conn.execute(
            """SELECT id, title, tags, created_at
               FROM scars
               ORDER BY created_at DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()

    if not rows:
        print_info("No incidents recorded yet.")
        print_info("Use: remnant scar add")
        return

    print_header(f"ALL INCIDENTS ({len(rows)})")
    print_table(
        columns=["ID", "Title", "Tags", "Date"],
        rows=[
            [
                str(r["id"]),
                r["title"][:50],
                r["tags"] or "—",
                r["created_at"][:10],
            ]
            for r in rows
        ],
    )


@app.command("search")
def search_scars(
    query: str = typer.Argument(..., help="Search term"),
) -> None:
    """Search incidents by keyword (searches title, problem, solution, tags)."""
    init_db()
    like = f"%{query}%"

    with db() as conn:
        rows = conn.execute(
            """SELECT id, title, tags, created_at
               FROM scars
               WHERE title LIKE ?
                  OR problem LIKE ?
                  OR solution LIKE ?
                  OR tags LIKE ?
               ORDER BY created_at DESC""",
            (like, like, like, like),
        ).fetchall()

    if not rows:
        print_info(f"No incidents found for: [bold]{query}[/bold]")
        return

    print_header(f"SEARCH: {query} ({len(rows)} results)")
    print_table(
        columns=["ID", "Title", "Tags", "Date"],
        rows=[
            [
                str(r["id"]),
                r["title"][:50],
                r["tags"] or "—",
                r["created_at"][:10],
            ]
            for r in rows
        ],
    )
    print_info(f"\nUse [bold]remnant scar show <id>[/bold] to see full details.")


@app.command("show")
def show_scar(
    scar_id: int = typer.Argument(..., help="Incident ID"),
) -> None:
    """Show full details of an incident."""
    init_db()
    record = _get_scar(scar_id)

    if not record:
        print_error(f"No incident found with ID: {scar_id}")
        raise typer.Exit(1)

    print_header(f"INCIDENT #{scar_id}: {record['title']}")
    print_key_value("Problem",  record["problem"])
    print_key_value("Cause",    record["cause"] or "Not recorded")
    print_key_value("Solution", record["solution"])
    print_key_value("Tags",     record["tags"] or "None")
    print_key_value("Recorded", record["created_at"][:10])


@app.command("remove")
def remove_scar(
    scar_id: int = typer.Argument(..., help="Incident ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Remove an incident record."""
    init_db()
    record = _get_scar(scar_id)

    if not record:
        print_error(f"No incident found with ID: {scar_id}")
        raise typer.Exit(1)

    if not force and not confirm(f"Remove incident #{scar_id}: {record['title']}?"):
        print_info("Cancelled.")
        return

    with db() as conn:
        conn.execute("DELETE FROM scars WHERE id = ?", (scar_id,))

    print_success(f"Removed incident #{scar_id}")
