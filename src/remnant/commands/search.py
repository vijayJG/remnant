"""
remnant search
--------------
Cross-record search across why, scar, and context.
One command to find anything you have recorded.

Usage:
    remnant search "nvidia"
    remnant search "oauth" --type why
    remnant search "kernel" --type scar
    remnant search "ubuntu" --detail
"""

from __future__ import annotations

from typing import Optional

import typer

from remnant.core.database import db, init_db
from remnant.output.terminal import (
    console,
    print_header,
    print_info,
    print_table,
)

app = typer.Typer(
    help="Search across all recorded history — why, scar, and context.",
    no_args_is_help=True,
)


def _search_records(query: str, record_type: Optional[str] = None) -> list[dict]:
    like = f"%{query}%"
    with db() as conn:
        if record_type:
            rows = conn.execute(
                """SELECT id, type, title, body, path, project, branch, created_at
                   FROM records
                   WHERE (title LIKE ? OR body LIKE ? OR tags LIKE ? OR path LIKE ?)
                     AND type = ?
                   ORDER BY created_at DESC""",
                (like, like, like, like, record_type),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT id, type, title, body, path, project, branch, created_at
                   FROM records
                   WHERE title LIKE ? OR body LIKE ? OR tags LIKE ? OR path LIKE ?
                   ORDER BY created_at DESC""",
                (like, like, like, like),
            ).fetchall()
    return [dict(r) for r in rows]


@app.command("query")
def search(
    query: str = typer.Argument(..., help="Search term"),
    type_filter: Optional[str] = typer.Option(
        None, "--type", "-t",
        help="Filter by type: why, scar, context"
    ),
    detail: bool = typer.Option(
        False, "--detail", "-d",
        help="Show full body of each result"
    ),
) -> None:
    """Search all recorded history by keyword."""
    init_db()
    results = _search_records(query, type_filter)

    if not results:
        if type_filter:
            print_info(f"No {type_filter} records found for: {query}")
        else:
            print_info(f"No records found for: {query}")
        print_info("Try a different keyword or remove the --type filter.")
        return

    label = f"SEARCH: {query}"
    if type_filter:
        label += f" (type: {type_filter})"
    label += f" — {len(results)} result(s)"
    print_header(label)

    if detail:
        for r in results:
            console.print(f"\n[bold]{r['type'].upper()}[/bold]  {r['title']}")
            console.print(f"  [dim]{r['created_at'][:10]}[/dim]")
            if r["path"]:
                console.print(f"  Path:    {r['path']}")
            if r["project"]:
                console.print(f"  Project: {r['project']}")
            if r["branch"]:
                console.print(f"  Branch:  {r['branch']}")
            console.print(f"  {r['body'][:200]}")
    else:
        print_table(
            columns=["Type", "Summary", "Project", "Date"],
            rows=[
                [
                    r["type"].upper(),
                    r["title"][:45],
                    r["project"] or "-",
                    r["created_at"][:10],
                ]
                for r in results
            ],
        )
        print_info("Use --detail to see full content.")
