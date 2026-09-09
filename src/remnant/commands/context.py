"""
remnant context
---------------
Restore your working context when you return to a project.
Shows git status, your last note, recent activity — observed
facts only, no guessing.

Usage:
    remnant context
    remnant context note "Working on auth refactor"
    remnant context notes
    remnant context clear
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import typer

from remnant.core.database import db, init_db
from remnant.core.errors import PathError
from remnant.output.terminal import (
    print_error,
    print_header,
    print_info,
    print_key_value,
    print_success,
    print_table,
    print_warning,
)

app = typer.Typer(
    help="Restore your project context — where you left off, what branch, what changed.",
    no_args_is_help=False,
)


def _get_project_root() -> Path:
    """Walk up from cwd to find a project root (git repo or known project)."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".git").exists():
            return parent
    return cwd  # fallback: use current directory


def _get_git_info(root: Path) -> dict:
    """Extract git information without requiring gitpython at import time."""
    info: dict = {}
    try:
        import git  # type: ignore
        repo = git.Repo(root, search_parent_directories=True)
        info["branch"] = repo.active_branch.name
        info["uncommitted"] = len(repo.index.diff(None)) + len(repo.untracked_files)
        info["last_commit"] = repo.head.commit.message.strip().split("\n")[0][:60]
        info["last_commit_time"] = datetime.fromtimestamp(
            repo.head.commit.committed_date
        ).strftime("%Y-%m-%d %H:%M")
    except Exception:
        pass
    return info


def _upsert_project(path: str, name: str) -> int:
    """Insert or update a project record, returning its ID."""
    with db() as conn:
        conn.execute(
            """INSERT INTO projects (path, name)
               VALUES (?, ?)
               ON CONFLICT(path) DO UPDATE SET
                   last_seen = datetime('now'),
                   name = excluded.name""",
            (path, name),
        )
        row = conn.execute(
            "SELECT id FROM projects WHERE path = ?", (path,)
        ).fetchone()
    return row["id"]


def _get_last_note(project_id: int) -> Optional[dict]:
    """Get the most recent note for a project."""
    with db() as conn:
        row = conn.execute(
            """SELECT note, started_at FROM sessions
               WHERE project_id = ? AND note IS NOT NULL
               ORDER BY started_at DESC LIMIT 1""",
            (project_id,),
        ).fetchone()
    return dict(row) if row else None


def _time_ago(dt_str: str) -> str:
    """Convert a datetime string to a human-readable 'X ago' string."""
    try:
        dt = datetime.fromisoformat(dt_str)
        now = datetime.now()
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return f"{seconds}s ago"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        elif seconds < 86400:
            return f"{seconds // 3600}h ago"
        else:
            return f"{diff.days}d ago"
    except Exception:
        return dt_str[:10]


# ── Commands ──────────────────────────────────────────────────────────────────

@app.callback(invoke_without_command=True)
def show_context(ctx: typer.Context) -> None:
    """Show context for the current project directory."""
    if ctx.invoked_subcommand is not None:
        return

    init_db()
    root = _get_project_root()
    name = root.name
    project_id = _upsert_project(str(root), name)

    print_header(f"PROJECT CONTEXT: {name}")
    print_key_value("Directory", str(root))

    # Git info (observed facts only)
    git = _get_git_info(root)
    if git:
        print_key_value("Branch",      git.get("branch", "unknown"))
        print_key_value("Last commit",  git.get("last_commit", "—"))
        print_key_value("Commit time",  git.get("last_commit_time", "—"))
        uncommitted = git.get("uncommitted", 0)
        uncommitted_label = f"{uncommitted} file(s)" if uncommitted else "clean"
        print_key_value("Uncommitted",  uncommitted_label)
    else:
        print_key_value("Git", "Not a git repository")

    # Last note
    note = _get_last_note(project_id)
    if note:
        print_key_value("Last note",   note["note"])
        print_key_value("Note saved",  _time_ago(note["started_at"]))
    else:
        print_key_value("Last note",   "None — add one with: remnant context note \"...\"")


@app.command("note")
def add_note(
    text: str = typer.Argument(..., help="Your note about what you're working on"),
) -> None:
    """Add a note to remember where you left off."""
    init_db()
    root = _get_project_root()
    name = root.name
    project_id = _upsert_project(str(root), name)

    with db() as conn:
        conn.execute(
            "INSERT INTO sessions (project_id, note) VALUES (?, ?)",
            (project_id, text),
        )

    print_success(f"Note saved for [bold]{name}[/bold]")
    print_info(f"  → {text}")


@app.command("notes")
def list_notes(
    limit: int = typer.Option(10, "--limit", "-n", help="Max notes to show"),
) -> None:
    """List recent notes for the current project."""
    init_db()
    root = _get_project_root()
    project_id = _upsert_project(str(root), root.name)

    with db() as conn:
        rows = conn.execute(
            """SELECT note, started_at FROM sessions
               WHERE project_id = ? AND note IS NOT NULL
               ORDER BY started_at DESC LIMIT ?""",
            (project_id, limit),
        ).fetchall()

    if not rows:
        print_info("No notes for this project yet.")
        print_info("Use: remnant context note \"what you're working on\"")
        return

    print_header(f"NOTES: {root.name}")
    print_table(
        columns=["Note", "Saved"],
        rows=[[r["note"], _time_ago(r["started_at"])] for r in rows],
    )


@app.command("clear")
def clear_notes(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Clear all notes for the current project."""
    init_db()
    root = _get_project_root()
    project_id = _upsert_project(str(root), root.name)

    from remnant.output.terminal import confirm
    if not force and not confirm(f"Clear all notes for {root.name}?"):
        print_info("Cancelled.")
        return

    with db() as conn:
        conn.execute(
            "UPDATE sessions SET note = NULL WHERE project_id = ?",
            (project_id,),
        )

    print_success(f"Cleared all notes for [bold]{root.name}[/bold]")
