# Remnant — Command Reference

Full reference for every command in Remnant v0.1.0.

---

## remnant why

Record and retrieve the human reason behind a file, folder, or configuration.

### remnant why set

```
remnant why set <path> "<reason>"
```

Records why a path exists. If a reason already exists for that path,
it is updated. The path is always stored as an absolute path regardless
of how you specify it.

Examples:

```bash
remnant why set ./config "Required because of a bug in Ubuntu 22.04"
remnant why set /etc/hosts "Added local dev domains for this machine"
remnant why set ~/.bashrc "Custom aliases and PATH modifications"
```

What gets stored alongside your reason:
- absolute path
- current git branch
- current git commit hash
- project name
- repository URL
- machine hostname

---

### remnant why get

```
remnant why get <path>
```

Retrieves the recorded reason for a path.

Example:

```bash
remnant why get ./config
```

Output:

```
WHY: ./config
────────────
Reason               Required because of a bug in Ubuntu 22.04
Recorded             2026-09-09
Branch               main
```

Exits with code 1 if no reason is recorded for that path.

---

### remnant why list

```
remnant why list [--limit N]
```

Lists all recorded reasons, most recently updated first.

Options:
- --limit, -n    maximum number of results to show (default: 20)

---

### remnant why search

```
remnant why search <query>
```

Searches reasons by keyword. Matches against both the reason text
and the path.

Example:

```bash
remnant why search "Ubuntu"
remnant why search "config"
```

---

### remnant why remove

```
remnant why remove <path> [--force]
```

Removes the recorded reason for a path. Asks for confirmation unless
--force is passed.

Options:
- --force, -f    skip confirmation prompt

---

### remnant why history

```
remnant why history <path>
```

Shows full details for a path including resolved absolute path,
first recorded date, and last updated date.

---

## remnant scar

Personal incident knowledge base. Record what broke and how you fixed it.

### remnant scar add

```
remnant scar add
```

Interactive prompt to record a new incident. No arguments — it asks
you each field one at a time.

Fields:
- Title (required) — short summary of the incident
- What broke? (required) — description of the problem
- What caused it? (optional) — root cause if known
- How did you fix it? (required) — the solution
- Tags (optional) — space-separated keywords for searching later

Example session:

```
RECORD INCIDENT

Title: NVIDIA stopped working after kernel update
What broke?: GPU not detected, black screen on login
What caused it?: DKMS module was not rebuilt for new kernel
How did you fix it?: sudo apt install --reinstall nvidia-dkms-535
Tags: nvidia kernel dkms

Incident recorded (id: 1)
```

---

### remnant scar list

```
remnant scar list [--limit N]
```

Lists all recorded incidents, most recent first.

Options:
- --limit, -n    maximum number of results to show (default: 20)

---

### remnant scar search

```
remnant scar search <query>
```

Searches incidents by keyword. Matches against title, problem
description, solution, and tags.

Example:

```bash
remnant scar search "nvidia"
remnant scar search "kernel"
remnant scar search "dkms"
```

---

### remnant scar show

```
remnant scar show <id>
```

Shows full details of an incident including problem, cause, solution,
tags, branch, and date.

Get the ID from remnant scar list or remnant scar search.

---

### remnant scar remove

```
remnant scar remove <id> [--force]
```

Removes an incident. Asks for confirmation unless --force is passed.

Options:
- --force, -f    skip confirmation prompt

---

## remnant context

Restore your working context when you return to a project.

### remnant context

```
remnant context
```

Run with no subcommand to see the current project context.

Shows:
- current directory
- git branch
- last commit message and time
- number of uncommitted files
- your last note for this project
- related why and scar records for this project

Example output:

```
PROJECT CONTEXT: remnant
────────────────────────
Directory            /home/vijay/remnant
Branch               main
Last commit          feat: add remnant search
Commit time          2026-09-09 11:00
Uncommitted          clean
Last note            unified storage done, search working

RELATED HISTORY
───────────────
Type   Summary                        Date
WHY    database.py                    2026-09-09
SCAR   needed to redesign arch twice  2026-09-09
```

The RELATED HISTORY section queries the records table for any why or
scar recorded while working in this project. This is the unified model
in action — context pulls from the same historical layer as everything else.

---

### remnant context note

```
remnant context note "<text>"
```

Saves a note for the current project so future-you knows where you
left off.

Example:

```bash
remnant context note "halfway through refactoring the database layer"
remnant context note "stopped at the search command, need to fix --type flag"
```

---

### remnant context notes

```
remnant context notes [--limit N]
```

Lists recent notes for the current project, most recent first.

Options:
- --limit, -n    maximum number of notes to show (default: 10)

---

### remnant context clear

```
remnant context clear [--force]
```

Clears all notes for the current project. Asks for confirmation
unless --force is passed.

---

## remnant search

Search across all recorded history in one query.

```
remnant search <query> [--type TYPE] [--detail]
```

Arguments:
- query    the keyword to search for (required)

Options:
- --type, -t      filter by record type: why, scar, or context
- --detail, -d    show full content of each result

Examples:

```bash
# Search everything
remnant search "nvidia"

# Only search why records
remnant search "ubuntu" --type why

# Only search scar records
remnant search "kernel" --type scar

# Show full details of each result
remnant search "oauth" --detail
```

Example output:

```
SEARCH: nvidia — 2 result(s)
─────────────────────────────
Type   Summary                                  Project    Date
WHY    nvidia.conf                              remnant    2026-09-08
SCAR   NVIDIA stopped working after kernel up…  remnant    2026-09-07

Use --detail to see full content.
```

Search matches against: title, body, tags, and path.

---

## Global options

```
remnant --version    show version and exit
remnant --help       show help
remnant <command> --help    show help for a specific command
```

---

## Exit codes

- 0    success
- 1    expected failure (record not found, user cancelled)
- 2    usage error (wrong arguments)
