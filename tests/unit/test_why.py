"""
Unit tests for remnant why command.
"""

import pytest
from typer.testing import CliRunner
from remnant.cli import app

runner = CliRunner()


def test_why_set_new(tmp_db):
    """Setting a reason for a new path should succeed."""
    result = runner.invoke(app, ["why", "set", "/tmp/testfile", "Test reason"])
    assert result.exit_code == 0
    assert "Recorded" in result.output or "Updated" in result.output


def test_why_set_updates_existing(tmp_db):
    """Setting a reason twice should update, not duplicate."""
    runner.invoke(app, ["why", "set", "/tmp/testfile", "Original reason"])
    result = runner.invoke(app, ["why", "set", "/tmp/testfile", "Updated reason"])
    assert result.exit_code == 0
    assert "Updated" in result.output


def test_why_get_existing(tmp_db):
    """Getting a reason for a known path should show it."""
    runner.invoke(app, ["why", "set", "/tmp/testfile", "Because of Ubuntu bug"])
    result = runner.invoke(app, ["why", "get", "/tmp/testfile"])
    assert result.exit_code == 0
    assert "Because of Ubuntu bug" in result.output


def test_why_get_missing(tmp_db):
    """Getting a reason for an unknown path should exit with code 1."""
    result = runner.invoke(app, ["why", "get", "/nonexistent/path/xyz"])
    assert result.exit_code == 1


def test_why_list_empty(tmp_db):
    """Listing with no reasons recorded should not crash."""
    result = runner.invoke(app, ["why", "list"])
    assert result.exit_code == 0
    assert "No reasons" in result.output


def test_why_list_shows_entries(tmp_db):
    """Listing should show recorded reasons."""
    runner.invoke(app, ["why", "set", "/tmp/file1", "Reason one"])
    runner.invoke(app, ["why", "set", "/tmp/file2", "Reason two"])
    result = runner.invoke(app, ["why", "list"])
    assert result.exit_code == 0
    assert "Reason one" in result.output
    assert "Reason two" in result.output


def test_why_search_finds_match(tmp_db):
    """Search should find entries matching the query."""
    runner.invoke(app, ["why", "set", "/tmp/testfile", "Exists because of Ubuntu 22.04"])
    result = runner.invoke(app, ["why", "search", "Ubuntu"])
    assert result.exit_code == 0
    assert "Ubuntu" in result.output


def test_why_search_no_match(tmp_db):
    """Search with no results should say so."""
    result = runner.invoke(app, ["why", "search", "nonexistentterm"])
    assert result.exit_code == 0
    assert "No results" in result.output


def test_why_remove_with_force(tmp_db):
    """Removing with --force should not ask for confirmation."""
    runner.invoke(app, ["why", "set", "/tmp/testfile", "Some reason"])
    result = runner.invoke(app, ["why", "remove", "/tmp/testfile", "--force"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_why_remove_missing(tmp_db):
    """Removing a non-existent path should exit with code 1."""
    result = runner.invoke(app, ["why", "remove", "/tmp/doesnotexist", "--force"])
    assert result.exit_code == 1
