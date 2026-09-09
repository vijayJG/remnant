"""
Unit tests for remnant scar command.
"""

import pytest
from typer.testing import CliRunner
from remnant.cli import app

runner = CliRunner()


def test_scar_add(tmp_db):
    """Adding a scar interactively should succeed."""
    result = runner.invoke(app, ["scar", "add"], input=(
        "Kernel panic after update\n"   # title
        "System wouldn't boot\n"         # problem
        "Conflicting kernel modules\n"   # cause
        "Boot into recovery, remove module\n"  # solution
        "kernel boot\n"                  # tags
    ))
    assert result.exit_code == 0
    assert "recorded" in result.output.lower()


def test_scar_list_empty(tmp_db):
    """Listing with no scars should not crash."""
    result = runner.invoke(app, ["scar", "list"])
    assert result.exit_code == 0
    assert "No incidents" in result.output


def test_scar_list_shows_entries(tmp_db):
    """Listing should show recorded scars."""
    runner.invoke(app, ["scar", "add"], input=(
        "NVIDIA broke\nDriver issue\nKernel update\nReinstall DKMS\nnvidia\n"
    ))
    result = runner.invoke(app, ["scar", "list"])
    assert result.exit_code == 0
    assert "NVIDIA" in result.output


def test_scar_search_finds_match(tmp_db):
    """Search should find matching scars."""
    runner.invoke(app, ["scar", "add"], input=(
        "NVIDIA broken\nGPU not detected\nKernel update\nReinstall DKMS\nnvidia gpu\n"
    ))
    result = runner.invoke(app, ["scar", "search", "nvidia"])
    assert result.exit_code == 0
    assert "NVIDIA" in result.output


def test_scar_search_no_match(tmp_db):
    """Search with no results should not crash."""
    result = runner.invoke(app, ["scar", "search", "totallymadeupterm"])
    assert result.exit_code == 0
    assert "No incidents" in result.output


def test_scar_show(tmp_db):
    """Showing a scar should display full details."""
    runner.invoke(app, ["scar", "add"], input=(
        "Test incident\nSomething broke\nUnknown\nFixed it\ntest\n"
    ))
    result = runner.invoke(app, ["scar", "show", "1"])
    assert result.exit_code == 0
    assert "Test incident" in result.output


def test_scar_show_missing(tmp_db):
    """Showing a non-existent scar should exit with code 1."""
    result = runner.invoke(app, ["scar", "show", "9999"])
    assert result.exit_code == 1


def test_scar_remove_with_force(tmp_db):
    """Removing with --force should not ask for confirmation."""
    runner.invoke(app, ["scar", "add"], input=(
        "To remove\nSomething\nCause\nSolution\ntag\n"
    ))
    result = runner.invoke(app, ["scar", "remove", "1", "--force"])
    assert result.exit_code == 0
    assert "Removed" in result.output
