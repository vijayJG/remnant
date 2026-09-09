# remnant

> Memory and history for your machine and code.

A Linux-first developer toolkit that remembers what your tools forget.

---

## The Problem

**Git** remembers what changed.
**Your OS** knows current state.
**Documentation** explains intended behavior.

But nobody remembers:

- Why does this config file exist?
- What broke on this machine last time, and how did I fix it?
- Where did I leave off in this project?
- How does this codebase actually connect together?
- What changed on my system this week?

**remnant does.**

---

## Install

```bash
pip install remnant
```

Requires Python 3.10+ on Linux.

---

## Commands

### `remnant why` — Record why things exist

```bash
# Set a reason
remnant why set ./config "Required because of a bug in Ubuntu 22.04"

# Read it back
remnant why ./config

# List everything you've recorded
remnant why list

# Search by keyword
remnant why search "Ubuntu"

# Remove a reason
remnant why remove ./config
```

---

### `remnant scar` — Personal incident knowledge base

When something breaks and you fix it — record it here.
Next time it breaks, you'll know exactly what to do.

```bash
# Record a new incident (interactive)
remnant scar add

# List all incidents
remnant scar list

# Search by keyword
remnant scar search "nvidia"

# Show full details of incident #3
remnant scar show 3

# Remove an incident
remnant scar remove 3
```

**Example session:**

```
$ remnant scar add

RECORD INCIDENT
Title: NVIDIA stopped working after kernel update
What broke?: GPU not detected, black screen on login
What caused it?: DKMS module was not rebuilt for new kernel
How did you fix it?: sudo apt install --reinstall nvidia-dkms-535
Tags: nvidia kernel dkms

✓ Incident recorded (id: 1)
```

Later:

```
$ remnant scar search nvidia

SEARCH: nvidia (1 result)

ID  Title                                    Tags          Date
1   NVIDIA stopped working after kernel up…  nvidia kern…  2026-09-09
```

---

### `remnant context` — Restore project context

Never spend 5 minutes asking "where was I?" again.

```bash
# Show current project context
remnant context

# Leave a note for future-you
remnant context note "Working on the auth refactor, halfway through OAuth flow"

# See all your notes for this project
remnant context notes
```

**Example output:**

```
PROJECT CONTEXT: my-app
──────────────────────
Directory        /home/user/projects/my-app
Branch           feature/auth
Last commit      Add OAuth2 token refresh logic
Commit time      2026-09-08 23:14
Uncommitted      3 file(s)
Last note        Working on the auth refactor, halfway through OAuth flow
Note saved       2h ago
```

---

## Coming Soon

| Command | What it does |
|---|---|
| `remnant map` | Understand your codebase structure |
| `remnant map dead` | Find potentially unused code |
| `remnant map deps` | Find potentially unused dependencies |
| `remnant drift` | Track how your Linux system changes over time |
| `remnant drift deleted` | See what files were recently deleted |
| `remnant report` | Weekly digest of everything remnant has recorded |

---

## Philosophy

remnant is:

- **Local-first** — no cloud account, no telemetry, your data stays on your machine
- **Honest** — it never claims certainty where analysis is heuristic
- **Composable** — every command supports `--format json` for piping into other tools
- **Minimal** — one `pip install`, one command, everything under `remnant`

---

## Data Storage

remnant stores everything locally:

```
~/.config/remnant/config.toml      # your configuration
~/.local/share/remnant/remnant.db  # your data (SQLite)
~/.cache/remnant/                  # temporary cache
```

Nothing leaves your machine.

---

## Configuration

Create `~/.config/remnant/config.toml` to customize behavior:

```toml
[core]
color = true
format = "human"   # or "json"

[drift]
watch_paths = ["~/.config", "~/.bashrc", "~/.zshrc"]
package_manager = "auto"

[map]
ignore = ["node_modules", ".git", "__pycache__", ".venv"]
```

---

## Contributing

remnant welcomes contributions. See [CONTRIBUTING.md](CONTRIBUTING.md).

Issues labeled [`good first issue`](https://github.com/yourusername/remnant/issues?q=label%3A%22good+first+issue%22) are a great place to start.

---

## License

MIT — see [LICENSE](LICENSE).
