# Changelog

All notable changes to remnant will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [0.1.0] — 2026-09-09

### Added

- `remnant why` — record and retrieve reasons for files and configs
  - `set`, `get`, `list`, `search`, `remove`, `history` subcommands
- `remnant scar` — personal incident knowledge base
  - `add`, `list`, `search`, `show`, `remove` subcommands
- `remnant context` — restore project working context
  - `note`, `notes`, `clear` subcommands
- SQLite-backed local storage at `~/.local/share/remnant/remnant.db`
- XDG-compliant config at `~/.config/remnant/config.toml`
- `--format json` output support (coming in 0.1.1)
- `--version` flag

### Philosophy

- Local-first: no telemetry, no cloud, no accounts
- Honest: observed facts are clearly distinguished from inferences
- Composable: JSON output for piping into other tools
