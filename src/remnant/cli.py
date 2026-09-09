"""
remnant.cli
-----------
The main CLI entry point.
All subcommands are registered here.

Usage:
    remnant --help
    remnant --version
    remnant why set ./config "Reason it exists"
    remnant scar add
    remnant context
"""

from __future__ import annotations

import typer

from remnant import __version__
from remnant.commands import why, scar, context

app = typer.Typer(
    name="remnant",
    help=(
        "Memory and history for your machine and code.\n\n"
        "remnant remembers what your other tools forget:\n"
        "why files exist, what broke and how you fixed it,\n"
        "and where you left off in your projects."
    ),
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Register subcommands
app.add_typer(why.app,     name="why",     help="Record WHY a file or config exists.")
app.add_typer(scar.app,    name="scar",    help="Personal incident knowledge base.")
app.add_typer(context.app, name="context", help="Restore project context.")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"remnant v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """remnant — memory and history for your machine and code."""
    pass
