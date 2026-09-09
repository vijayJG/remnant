"""
remnant.core.database
---------------------
SQLite connection and schema management.
All persistent data lives in ~/.local/share/remnant/remnant.db
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from remnant.core.config import DATABASE_FILE, ensure_dirs


def get_connection() -> sqlite3.Connection:
    """Return a configured SQLite connection."""
    ensure_dirs()
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row       # rows behave like dicts
    conn.execute("PRAGMA journal_mode=WAL")   # safer concurrent writes
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def db() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database access.

    Usage:
        with db() as conn:
            conn.execute(...)
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """
    Create all tables if they don't already exist.
    Safe to call multiple times (idempotent).
    """
    with db() as conn:
        conn.executescript("""
            -- reasons: stores WHY a file/folder exists
            CREATE TABLE IF NOT EXISTS reasons (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                path        TEXT    NOT NULL UNIQUE,
                reason      TEXT    NOT NULL,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            -- scars: personal incident knowledge base
            CREATE TABLE IF NOT EXISTS scars (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                problem     TEXT    NOT NULL,
                cause       TEXT,
                solution    TEXT    NOT NULL,
                tags        TEXT,   -- comma-separated
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            -- projects: tracks known project directories
            CREATE TABLE IF NOT EXISTS projects (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                path        TEXT    NOT NULL UNIQUE,
                name        TEXT    NOT NULL,
                first_seen  TEXT    NOT NULL DEFAULT (datetime('now')),
                last_seen   TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            -- sessions: activity inside a project
            CREATE TABLE IF NOT EXISTS sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  INTEGER NOT NULL REFERENCES projects(id),
                started_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                ended_at    TEXT,
                note        TEXT
            );

            -- events: central event log (used by drift + report)
            CREATE TABLE IF NOT EXISTS events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT    NOT NULL DEFAULT (datetime('now')),
                type        TEXT    NOT NULL,
                source      TEXT,
                payload     TEXT    -- JSON blob
            );

            -- snapshots: system state at a point in time
            CREATE TABLE IF NOT EXISTS snapshots (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT    NOT NULL DEFAULT (datetime('now')),
                type        TEXT    NOT NULL,
                data        TEXT    NOT NULL  -- JSON blob
            );

            -- deletions: log of deleted files
            CREATE TABLE IF NOT EXISTS deletions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                path        TEXT    NOT NULL,
                size        INTEGER,
                file_hash   TEXT,
                deleted_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );
        """)
