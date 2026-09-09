"""
Unit tests for remnant search command.
"""

from typer.testing import CliRunner
from remnant.cli import app

runner = CliRunner()


def test_search_no_results(tmp_db):
    """Search with no matching records should not crash."""
    result = runner.invoke(app, ["search", "xyznothing"])
    assert result.exit_code == 0
    assert "No records found" in result.output


def test_search_finds_why(tmp_db):
    """Search should find a why record by keyword."""
    runner.invoke(app, ["why", "set", "/tmp/config", "Exists because of Ubuntu 22.04 bug"])
    result = runner.invoke(app, ["search", "Ubuntu"])
    assert result.exit_code == 0
    assert "WHY" in result.output


def test_search_finds_scar(tmp_db):
    """Search should find a scar record by keyword."""
    runner.invoke(app, ["scar", "add"], input=(
        "NVIDIA broken\nGPU not detected\nKernel update\nReinstall DKMS\nnvidia\n"
    ))
    result = runner.invoke(app, ["search", "nvidia"])
    assert result.exit_code == 0
    assert "SCAR" in result.output


def test_search_type_filter(tmp_db):
    """Search with --type should only return that type."""
    runner.invoke(app, ["why", "set", "/tmp/config", "Ubuntu workaround"])
    runner.invoke(app, ["scar", "add"], input=(
        "Ubuntu crash\nSystem crashed\nUnknown\nRebooted\nubuntu\n"
    ))
    result = runner.invoke(app, ["search", "ubuntu", "--type", "why"])
    assert result.exit_code == 0
    assert "WHY" in result.output
    assert "SCAR" not in result.output


def test_search_cross_record(tmp_db):
    """Search should find results across why and scar simultaneously."""
    runner.invoke(app, ["why", "set", "/tmp/cfg", "nvidia config workaround"])
    runner.invoke(app, ["scar", "add"], input=(
        "nvidia broken\nGPU issue\nKernel\nFix DKMS\nnvidia\n"
    ))
    result = runner.invoke(app, ["search", "nvidia"])
    assert result.exit_code == 0
    assert "WHY" in result.output
    assert "SCAR" in result.output


def test_search_detail_flag(tmp_db):
    """Search with --detail should show full body content."""
    runner.invoke(app, ["why", "set", "/tmp/hosts", "Maps local dev domains"])
    result = runner.invoke(app, ["search", "local", "--detail"])
    assert result.exit_code == 0
    assert "Maps local dev domains" in result.output
