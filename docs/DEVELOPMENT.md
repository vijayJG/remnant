# Remnant — Development Guide

Everything you need to set up, run, test, and extend Remnant.

---

## Environment

Remnant is developed on Ubuntu WSL (Windows Subsystem for Linux).
All commands assume a Linux shell (bash).

Do not develop inside /mnt/c/ — use the Linux filesystem:

```
/home/<username>/remnant
```

---

## Initial Setup

Clone the repository:

```bash
cd ~
git clone https://github.com/vijayJG/remnant.git
cd remnant
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install in development mode with all dev dependencies:

```bash
pip install -e ".[dev]"
```

Verify the install:

```bash
remnant --version
remnant --help
```

---

## Daily Workflow

Every time you open WSL to work on Remnant:

```bash
cd ~/remnant
source .venv/bin/activate
git status
```

The pattern is:

```
write code
run pytest
fix failures
commit
push
```

Never commit with failing tests.

---

## Running Tests

Run the full test suite:

```bash
pytest
```

Run a specific test file:

```bash
pytest tests/unit/test_why.py
```

Run a single test:

```bash
pytest tests/unit/test_why.py::test_why_set_new
```

Run with verbose output:

```bash
pytest -v
```

Run with short traceback on failure:

```bash
pytest --tb=short
```

---

## Test Architecture

Tests never touch the real database at ~/.local/share/remnant/remnant.db.

The tmp_db fixture in tests/conftest.py redirects all database operations
to a temporary SQLite file that is created fresh for each test and
deleted after.

```python
@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_remnant.db"
    monkeypatch.setattr("remnant.core.database.DATABASE_FILE", test_db)
    monkeypatch.setattr("remnant.core.config.DATABASE_FILE", test_db)
    from remnant.core.database import init_db
    init_db()
    return test_db
```

Every test that touches the database must use this fixture.

---

## Adding a New Command

1. Create a new file in src/remnant/commands/

```bash
touch src/remnant/commands/mycommand.py
```

2. Write the command using Typer:

```python
import typer

app = typer.Typer(help="What this command does.")

@app.command("subcommand")
def my_subcommand() -> None:
    """Description shown in --help."""
    pass
```

3. Register it in src/remnant/cli.py:

```python
from remnant.commands import mycommand
app.add_typer(mycommand.app, name="mycommand", help="Short description.")
```

4. Write tests in tests/unit/test_mycommand.py

5. Run pytest — all tests must pass before committing

---

## Writing to the Database

Always write through the records table first, then the
command-specific table.

Example pattern from why.py:

```python
with db() as conn:
    cursor = conn.execute(
        """INSERT INTO records
           (type, title, body, path, project, branch, commit_hash, machine)
           VALUES ('why', ?, ?, ?, ?, ?, ?, ?)""",
        (title, body, path, project, branch, commit_hash, machine),
    )
    record_id = cursor.lastrowid

    conn.execute(
        "INSERT INTO reasons (record_id, path) VALUES (?, ?)",
        (record_id, resolved_path),
    )
```

Never insert into reasons or scars without a corresponding records row.
The foreign key constraint will reject it, and cascade delete will not
work correctly.

---

## Git Context

To attach git context to a record, call get_git_context() from core/git.py:

```python
from remnant.core.git import get_git_context
from pathlib import Path

git = get_git_context(Path.cwd())

# Returns a dict:
# {
#     "project":     "remnant",
#     "repository":  "https://github.com/vijayJG/remnant.git",
#     "branch":      "main",
#     "commit_hash": "4c94b4b12e3f",
# }
```

All values may be None if the path is not inside a git repository.
Always handle None gracefully.

---

## Output

Never use print() directly. Use the functions in output/terminal.py:

```python
from remnant.output.terminal import (
    print_success,
    print_error,
    print_warning,
    print_info,
    print_header,
    print_key_value,
    print_table,
    confirm,
)
```

This keeps all output consistent and makes future style changes easier.

---

## Commit Message Format

Use conventional commits:

```
feat: add new capability
fix: correct a bug
refactor: restructure without changing behaviour
docs: update documentation
test: add or fix tests
chore: dependency updates, config changes
```

Examples from this project:

```
feat: add remnant search — cross-record retrieval across why, scar, and context
fix: shorten why title to filename instead of full path
refactor: unify storage model — records table as shared historical layer
docs: rewrite README to reflect current architecture and commands
```

---

## Project Layout Explained

```
src/remnant/cli.py
```
The entry point. All Typer apps are registered here. The search command
lives directly in this file rather than a separate module — this is
intentional because search has no subcommands and registering a
single-command Typer app caused option-parsing conflicts.

```
src/remnant/core/database.py
```
Contains get_connection(), the db() context manager, and init_db().
init_db() is idempotent — safe to call multiple times. It uses
CREATE TABLE IF NOT EXISTS for every table.

```
src/remnant/core/config.py
```
Defines paths for config, data, and cache directories. Loads
~/.config/remnant/config.toml with deep merge against defaults.
Also exports DATABASE_FILE which database.py imports.

```
src/remnant/core/git.py
```
Single function get_git_context(path) that returns a dict.
Never raises — returns None values on any failure.

```
src/remnant/output/terminal.py
```
All Rich-based output functions. The console object is defined here
and imported by commands that need direct console access.

---

## Known Issues

The python_ast.py file in analyzers/ is a placeholder.
It contains code from an earlier abandoned iteration of the map
command and should not be imported anywhere. It will be rewritten
from scratch when map is properly designed.

The records_fts virtual table is created in init_db() but search
currently uses LIKE queries, not FTS5. This is intentional for now —
FTS5 requires careful handling of the content table sync. It will be
upgraded when search quality becomes a real user complaint.
