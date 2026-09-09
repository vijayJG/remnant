"""
remnant context
---------------
Restore your working context when you return to a project.
Shows git status, your last note, and related history from
why and scar — observed facts only, no guessing.

Usage:
    remnant context
    remnant context note "Working on auth refactor"
    remnant context notes
    remnant context clear
"""

from __future__ import annotations

import socket
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer

from remnant.core.database import db, init_db
from remnant.core.git import get_git_context
from remnant.output.terminal import (
    confirm,
    print_header,
    print_info,
    print_key_value,
    print_success,
    print_table,
    print_warning,
)

app = typer.Typer(
    help="Restore project context — where you left off, what branch, what changed.",
    no_args_is_help=False,
)


def _get_project_root() -> Path:
    """Walk up from cwd to find a git root, or fall back to cwd."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".git").exists():
            return parent
    return cwd


def _get_git_info(root: Path) -> dict:
    """Extract git information. Returns empty dict on failure."""
    info: dict = {}
    try:
        import git
        repo = git.Repo(root, search_parent_directories=True)
        info["branch"]           = repo.active_branch.name
        info["last_commit"]      = repo.head.commit.message.strip().split("\n")[0][:60]
        info["last_commit_time"] = datetime.fromtimestamp(
            repo.head.commit.committed_date
        ).strftime("%Y-%m-%d %H:%M")
        uncommitted = len(repo.index.diff(None)) + len(repo.untracked_files)
        info["uncommitted"] = uncommitted
    except Exception:
        pass
    return info


def _upsert_project(path: str, name: str) -> int:
    """Insert or update a project row, return its id."""
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
    """Get the most recent context note for a project."""
    with db() as conn:
        row = conn.execute(
            """SELECT s.note, s.started_at, r.branch, r.commit_hash
               FROM sessions s
               LEFT JOIN records r ON r.id = s.record_id
               WHERE s.project_id = ? AND s.note IS NOT NULL
               ORDER BY s.started_at DESC LIMIT 1""",
            (project_id,),
        ).fetchone()
    return dict(row) if row else None


def _get_related_records(project: str) -> list[dict]:
    """
    Fetch why and scar records related to this project.
    This is the unified model paying off — one query surfaces
    history from all commands.
    """
    with db() as conn:
        rows = conn.execute(
            """SELECT type, title, body, created_at
               FROM records
               WHERE project = ?
               ORDER BY created_at DESC
               LIMIT 5""",
            (project,),
        ).fetchall()
    return [dict(r) for r in rows]


def _time_ago(dt_str: str) -> str:
    """Convert a datetime string to a human-readable 'X ago' string."""
    try:
        dt = datetime.fromisoformat(dt_str)
        diff = datetime.now() - dt
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


# -- Commands ------------------------------------------------------------------

@app.callback(invoke_without_command=True)
def show_context(ctx: typer.Context) -> None:
    """Show context for the current project directory."""
    if ctx.invoked_subcommand is not None:
        return

    init_db()
    root       = _get_project_root()
    name       = root.name
    project_id = _upsert_project(str(root), name)

    print_header(f"PROJECT CONTEXT: {name}")
    print_key_value("Directory", str(root))

    # Git info — observed facts only
    git = _get_git_info(root)
    if git:
        print_key_value("Branch",      git.get("branch", "unknown"))
        print_key_value("Last commit",  git.get("last_commit", "-"))
        print_key_value("Commit time",  git.get("last_commit_time", "-"))
        uncommitted = git.get("uncommitted", 0)
        print_key_value("Uncommitted",  f"{uncommitted} file(s)" if uncommitted else "clean")
    else:
        print_key_value("Git", "Not a git repository")

    # Last note
    note = _get_last_note(project_id)
    if note:
        print_key_value("Last note",  note["note"])
        print_key_value("Note saved", _time_ago(note["started_at"]))
    else:
        print_key_value("Last note", "None — use: remnant context note \"...\"")

    # Related history from why + scar — this is what the unified model enables
    related = _get_related_records(name)
    if related:
        print_header("RELATED HISTORY")
        print_table(
            columns=["Type", "Summary", "Date"],
            rows=[
                [
                    r["type"].upper(),
                    r["title"][:55],
                    r["created_at"][:10],
                ]
                for r in related
            ],
        )


@app.command("note")
def add_note(
    text: str = typer.Argument(..., help="Your note about what you are working on"),
) -> None:
    """Add a note to remember where you left off."""
    init_db()
    root       = _get_project_root()
    name       = root.name
    project_id = _upsert_project(str(root), name)
    git        = get_git_context(root)

    with db() as conn:
        # Write through records first
        cursor = conn.execute(
            """INSERT INTO records
               (type, title, body, project, repository, branch, commit_hash, machine)
               VALUES ('context', ?, ?, ?, ?, ?, ?, ?)""",
            (
                f"Context: {name}",
                text,
                name,
                git.get("repository"),
                git.get("branch"),
                git.get("commit_hash"),
                socket.gethostname(),
            ),
        )
        record_id = cursor.lastrowid

        conn.execute(
            """INSERT INTO sessions (record_id, project_id, note)
               VALUES (?, ?, ?)""",
            (record_id, project_id, text),
        )

    print_success(f"Note saved for {name}")
    print_info(f"  {text}")


@app.command("notes")
def list_notes(
    limit: int = typer.Option(10, "--limit", "-n", help="Max notes to show"),
) -> None:
    """List recent notes for the current project."""
    init_db()
    root       = _get_project_root()
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
        print_info("Use: remnant context note \"what you are working on\"")
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
    root       = _get_project_root()
    project_id = _upsert_project(str(root), root.name)

    if not force and not confirm(f"Clear all notes for {root.name}?"):
        print_info("Cancelled.")
        return

    with db() as conn:
        conn.execute(
            "UPDATE sessions SET note = NULL WHERE project_id = ?",
            (project_id,),
        )

    print_success(f"Cleared all notes for {root.name}")
