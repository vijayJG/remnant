"""
Shared pytest fixtures for remnant tests.
"""

import pytest
import sqlite3
from pathlib import Path
from unittest.mock import patch


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    """
    Redirect all database operations to a temporary test database.
    This ensures tests never touch the real ~/.local/share/remnant/remnant.db
    """
    test_db = tmp_path / "test_remnant.db"

    monkeypatch.setattr("remnant.core.config.DATABASE_FILE", test_db)
    monkeypatch.setattr("remnant.core.config.CONFIG_DIR",    tmp_path / "config")
    monkeypatch.setattr("remnant.core.config.DATA_DIR",      tmp_path / "data")
    monkeypatch.setattr("remnant.core.config.CACHE_DIR",     tmp_path / "cache")

    # Also patch wherever database.py imports it from
    monkeypatch.setattr("remnant.core.database.DATABASE_FILE", test_db)

    from remnant.core.database import init_db
    init_db()

    return test_db


@pytest.fixture
def sample_project(tmp_path):
    """Create a minimal fake git project for context tests."""
    project = tmp_path / "my_project"
    project.mkdir()
    (project / ".git").mkdir()
    (project / "main.py").write_text("print('hello')\n")
    (project / "README.md").write_text("# My Project\n")
    return project
