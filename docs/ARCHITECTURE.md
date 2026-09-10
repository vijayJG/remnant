# Remnant — Architecture

## What Remnant Is

Remnant is a local CLI toolkit that preserves the context, rationale, and
incident history that developers normally lose.

Git remembers what changed.
Your OS knows current state.
Remnant remembers the missing layer:

- Why a file or config exists
- What broke and how it was fixed
- Where you left off in a project
- All of this connected to git context and searchable in one place

---

## What Remnant Is Not

- Not a system monitor
- Not a backup tool
- Not a note-taking app
- Not an AI assistant
- Not a cloud service

It is a local, terminal-native memory layer. Nothing leaves your machine.

---

## The Core Design Decision

The most important architectural decision in Remnant is this:

> Every why, scar, and context note is a record in one shared table.
> Commands are views over that table, not independent databases.

This was not the original design. The first version had separate isolated
tables for reasons, scars, and sessions. That made cross-command search
impossible and meant each command had no awareness of the others.

The unified records table fixed this. Now:

- remnant context shows related whys and scars automatically
- remnant search finds anything across all commands in one query
- Every record carries shared metadata: path, project, branch, commit, machine

---

## Directory Structure

```
remnant/
├── src/remnant/
│   ├── __init__.py          version number lives here
│   ├── cli.py               main entry point, all commands registered here
│   ├── commands/
│   │   ├── why.py           remnant why subcommands
│   │   ├── scar.py          remnant scar subcommands
│   │   ├── context.py       remnant context subcommands
│   │   └── search.py        not used — search lives in cli.py directly
│   ├── core/
│   │   ├── config.py        loads ~/.config/remnant/config.toml
│   │   ├── database.py      SQLite connection, schema, init_db()
│   │   ├── errors.py        custom exception classes
│   │   └── git.py           git context extraction via GitPython
│   ├── analyzers/
│   │   └── python_ast.py    placeholder — used in future map command
│   └── output/
│       └── terminal.py      all terminal output via Rich
├── tests/
│   ├── conftest.py          shared fixtures — tmp_db redirects to temp SQLite
│   └── unit/
│       ├── test_why.py
│       ├── test_scar.py
│       └── test_search.py
├── docs/                    this documentation
├── pyproject.toml           packaging, dependencies, tool config
├── README.md                public-facing project description
├── CONTRIBUTING.md          how to contribute
├── CHANGELOG.md             version history
└── LICENSE                  MIT
```

---

## Database Schema

All data lives in a single SQLite file at:

```
~/.local/share/remnant/remnant.db
```

### The records table

This is the heart of the system. Every piece of information Remnant stores
starts here.

```sql
CREATE TABLE records (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    type         TEXT NOT NULL,   -- 'why' | 'scar' | 'context'
    title        TEXT NOT NULL,
    body         TEXT NOT NULL,
    tags         TEXT,            -- comma-separated
    path         TEXT,            -- file or folder this relates to
    project      TEXT,            -- project root directory name
    repository   TEXT,            -- git remote URL
    branch       TEXT,            -- git branch at time of recording
    commit_hash  TEXT,            -- git commit hash at time of recording
    machine      TEXT,            -- hostname
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### Full-text search index

```sql
CREATE VIRTUAL TABLE records_fts USING fts5(
    title, body, tags, path,
    content='records',
    content_rowid='id'
);
```

Currently search uses LIKE queries. The FTS5 table is in place for
upgrade to full-text search in a future version.

### Command-specific tables

These store structured fields that do not fit cleanly in records.
Each row links back to records via record_id.

```sql
-- extra fields for 'why' records
CREATE TABLE reasons (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id  INTEGER NOT NULL REFERENCES records(id) ON DELETE CASCADE,
    path       TEXT NOT NULL UNIQUE
);

-- extra fields for 'scar' records
CREATE TABLE scars (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id  INTEGER NOT NULL REFERENCES records(id) ON DELETE CASCADE,
    problem    TEXT NOT NULL,
    cause      TEXT,
    solution   TEXT NOT NULL
);

-- known projects
CREATE TABLE projects (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    path       TEXT NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    first_seen TEXT NOT NULL DEFAULT (datetime('now')),
    last_seen  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- context notes per project
CREATE TABLE sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id  INTEGER REFERENCES records(id) ON DELETE CASCADE,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    ended_at   TEXT,
    note       TEXT
);
```

### Delete behaviour

When a record is deleted, CASCADE removes the linked row in reasons or
scars automatically. Foreign keys are enabled on every connection.

---

## Git Context

Every record written by why, scar, or context note automatically captures:

- project name (from git working directory)
- repository URL (from first git remote)
- current branch
- current commit hash (short, 12 characters)
- machine hostname

This happens in core/git.py via GitPython. If the path is not inside a
git repository, all git fields are stored as NULL. The command still works.

---

## How Each Command Uses the Records Table

### remnant why set

1. Resolves path to absolute
2. Calls get_git_context() on the path
3. Inserts a row into records with type='why'
4. Inserts a row into reasons linking to that record
5. On update: updates the records row, not the reasons row

### remnant scar add

1. Prompts user interactively for title, problem, cause, solution, tags
2. Calls get_git_context() on cwd
3. Inserts a row into records with type='scar'
4. Inserts a row into scars linking to that record

### remnant context note

1. Finds project root by walking up from cwd looking for .git
2. Upserts a row in projects
3. Calls get_git_context() on root
4. Inserts a row into records with type='context'
5. Inserts a row into sessions linking to that record and the project

### remnant search

1. Takes a query string
2. Runs a LIKE search across title, body, tags, path in records
3. Optionally filters by type
4. Returns results from one table — no joins needed for basic search

### remnant context (show)

1. Finds project root
2. Upserts project row
3. Gets git info
4. Fetches last session note for this project
5. Fetches related records WHERE project = current project name
6. Displays everything together

---

## Output Layer

All terminal output goes through output/terminal.py using the Rich library.
No command prints directly to stdout.

Functions available:

```python
print_header(title)
print_success(message)
print_error(message)
print_warning(message)
print_info(message)
print_key_value(key, value)
print_table(columns, rows, title)
confirm(prompt) -> bool
```

This means changing the visual style of all output requires editing
one file.

---

## Configuration

Remnant follows the XDG Base Directory specification:

```
~/.config/remnant/config.toml   # user configuration
~/.local/share/remnant/          # persistent data
~/.cache/remnant/                # temporary cache
```

If no config file exists, defaults are used. The config is loaded on
every command via core/config.py.

---

## Dependency Decisions

| Package    | Why                                              |
|------------|--------------------------------------------------|
| typer      | CLI framework with subcommand support            |
| rich       | Terminal output formatting                       |
| gitpython  | Git context extraction                           |
| pytest     | Testing                                          |
| ruff       | Linting                                          |

SQLite is used via Python's built-in sqlite3 module. No ORM.
No external database. No cloud dependency.

---

## What Was Deliberately Left Out

These were considered and rejected for v0.1:

- Background daemon for automatic capture
- AI-generated summaries
- Web dashboard
- Cloud synchronisation
- Full-text search (FTS5 table exists but search uses LIKE for now)
- map command (planned but postponed until core is proven useful)
- drift command (postponed — too much scope risk)
- aliasAI and confess (removed from roadmap entirely)

The rule applied: every feature must reinforce the core thesis.
The core thesis is: local historical memory for decisions, failures,
and context that developers normally lose.
