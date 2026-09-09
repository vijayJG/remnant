"""
remnant.core.database
---------------------
SQLite connection and schema management.
All persistent data lives in ~/.local/share/remnant/remnant.db
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Generator

from remnant.core.config import DATABASE_FILE, ensure_dirs


def get_connection() -> sqlite3.Connection:
    """Return a configured SQLite connection."""
    ensure_dirs()
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
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
            -- CORE HISTORICAL LAYER
            -- Every why, scar, and context note is a record.
            -- Commands are views over this table.
            CREATE TABLE IF NOT EXISTS records (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                type         TEXT NOT NULL,
                title        TEXT NOT NULL,
                body         TEXT NOT NULL,
                tags         TEXT,
                path         TEXT,
                project      TEXT,
                repository   TEXT,
                branch       TEXT,
                commit_hash  TEXT,
                machine      TEXT,
                created_at   TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at   TEXT NOT NULL DEFAULT (datetime('now'))
            );

            -- full-text search over records
            CREATE VIRTUAL TABLE IF NOT EXISTS records_fts USING fts5(
                title,
                body,
                tags,
                path,
                content='records',
                content_rowid='id'
            );

            -- extra structured fields for 'why' records
            CREATE TABLE IF NOT EXISTS reasons (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id   INTEGER NOT NULL REFERENCES records(id) ON DELETE CASCADE,
                path        TEXT    NOT NULL UNIQUE
            );

            -- extra structured fields for 'scar' records
            CREATE TABLE IF NOT EXISTS scars (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id   INTEGER NOT NULL REFERENCES records(id) ON DELETE CASCADE,
                problem     TEXT    NOT NULL,
                cause       TEXT,
                solution    TEXT    NOT NULL
            );

            -- known project directories
            CREATE TABLE IF NOT EXISTS projects (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                path        TEXT    NOT NULL UNIQUE,
                name        TEXT    NOT NULL,
                first_seen  TEXT    NOT NULL DEFAULT (datetime('now')),
                last_seen   TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            -- context notes per project
            CREATE TABLE IF NOT EXISTS sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id   INTEGER REFERENCES records(id) ON DELETE CASCADE,
                project_id  INTEGER NOT NULL REFERENCES projects(id),
                started_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                ended_at    TEXT,
                note        TEXT
            );

            -- indexes
            CREATE INDEX IF NOT EXISTS idx_records_type       ON records(type);
            CREATE INDEX IF NOT EXISTS idx_records_path       ON records(path);
            CREATE INDEX IF NOT EXISTS idx_records_project    ON records(project);
            CREATE INDEX IF NOT EXISTS idx_records_created_at ON records(created_at);
        """)
