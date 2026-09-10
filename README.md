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

remnant fills that gap with a local, terminal-native memory layer.

---

## Install

\`\`\`bash
pip install remnant
\`\`\`

Requires Python 3.10+ on Linux.

---

## Commands

### \`remnant why\` — Record why things exist

\`\`\`bash
remnant why set ./config "Required because of a bug in Ubuntu 22.04"
remnant why get ./config
remnant why list
remnant why search "Ubuntu"
remnant why remove ./config
\`\`\`

---

### \`remnant scar\` — Personal incident knowledge base

\`\`\`bash
remnant scar add
remnant scar list
remnant scar search "nvidia"
remnant scar show 3
remnant scar remove 3
\`\`\`

---

### \`remnant context\` — Restore project context

\`\`\`bash
remnant context
remnant context note "Working on auth refactor"
remnant context notes
\`\`\`

---

### \`remnant search\` — Search everything

\`\`\`bash
remnant search "nvidia"
remnant search "ubuntu" --type why
remnant search "kernel" --type scar
remnant search "oauth" --detail
\`\`\`

---

## How it works

Every record is stored in a shared local database with:

- the content you wrote
- the file or path it relates to
- the project it belongs to
- the git branch and commit at time of recording
- the machine it was recorded on

\`remnant search\` finds anything across all commands.
\`remnant context\` surfaces related history automatically.

Nothing leaves your machine.

---

## Data storage

\`\`\`
~/.config/remnant/config.toml      # configuration
~/.local/share/remnant/remnant.db  # all data (SQLite)
~/.cache/remnant/                  # temporary cache
\`\`\`

---

## Philosophy

- **Local-first** — no cloud, no telemetry, no accounts
- **Honest** — observed facts only, no guessing
- **Unified** — why, scar, and context are views over one shared history
- **Minimal** — one pip install, one command, no background daemons

---

## Roadmap

Current release:

- \`remnant why\` — rationale for files and configs
- \`remnant scar\` — personal incident knowledge base
- \`remnant context\` — project working context
- \`remnant search\` — cross-record retrieval

Planned:

- \`remnant map\` — code structure tied to recorded history
- \`remnant report\` — weekly digest of recorded history

---

## Contributing

remnant welcomes contributions. See [CONTRIBUTING.md](CONTRIBUTING.md).

Issues labeled
[\`good first issue\`](https://github.com/vijayJG/remnant/issues?q=label%3A%22good+first+issue%22)
are a great place to start.

---

## License

MIT — see [LICENSE](LICENSE).
