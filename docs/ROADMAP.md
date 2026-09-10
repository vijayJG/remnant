# Remnant — Roadmap

This document explains where Remnant is going and, more importantly, why.

---

## Current State — v0.1.0

What exists and works:

```
remnant why      record and retrieve rationale for files and configs
remnant scar     personal incident knowledge base
remnant context  project working context with related history
remnant search   cross-record retrieval across all commands
```

Underneath all of this is one shared records table. Every why, scar, and
context note is a record. Commands are views over that table, not
independent systems.

24 tests passing. All data local. No dependencies beyond Python, SQLite,
Typer, Rich, and GitPython.

---

## How Decisions Are Made

Features are not added because they sound useful in a specification.
They are added because real use reveals friction.

The process is:

```
use Remnant daily
notice friction
record the friction
design the fix
build it
repeat
```

This means the roadmap below is directional, not a commitment.
If daily use reveals that search is broken before context is useful,
search gets fixed before context gets expanded. Real friction beats
planned features.

---

## What Was Deliberately Removed

These ideas were considered and rejected:

aliasAI — observes shell commands and suggests aliases. Removed because
it weakens product identity and introduces shell-specific complexity.

confess — roasts your git commit history. Removed because it is fun
but does not reinforce the core thesis of historical memory.

These may return as optional plugins later. They will not be in core.

---

## What Was Postponed

drift — tracks how your Linux system changes over time: packages
installed, config files modified, files deleted.

Postponed because it carries high scope risk. It can easily turn
Remnant into a generic system monitor, which already has better
dedicated tools. Drift only belongs in Remnant if it feeds the
historical memory model directly. That connection is not clear yet.

map — understands codebase structure.

Postponed until the core three commands (why, scar, context) are proven
useful through daily use. A generic code inspector is not a strong
differentiator. Map earns its place only when it surfaces historical
records alongside code structure — showing not just what a file does
but why it exists, what incidents relate to it, and what the context
was when it was last touched.

---

## Next Phase — Friction Fixes

Before adding any new commands, known rough edges will be addressed
based on real use. Likely candidates:

Search quality — LIKE queries are broad. If search returns too much
noise or misses obvious matches, upgrade to FTS5 full-text search.

Why title display — currently shows the filename. May need to show
more context depending on how confusing it is in practice.

Context related history — currently matches on project name. May need
to also match on file path for more precise results.

Scar add flow — interactive prompts work but may feel slow if you
record incidents frequently. A quick mode may be needed.

These will be addressed based on what actually causes friction during
use, not based on assumption.

---

## Next Commands

### remnant map

Purpose: understand a file or codebase in the context of its history.

The wrong version of map:

```
remnant map .
→ here are the files and imports in your project
```

That is generic code analysis. Many tools do this better.

The right version of map:

```
remnant map src/auth.py
→ here is what this file does
→ here is why it exists (from remnant why)
→ here are incidents related to it (from remnant scar)
→ here is the context when it was last touched (from remnant context)
→ here is its current git state
```

That is historical context layered over code structure. That is what
makes map belong in Remnant rather than being a standalone tool.

Map will not be built until the core three commands have been used
enough to produce real why and scar records that map can surface.

---

### remnant report

Purpose: weekly digest of everything Remnant has recorded.

```
remnant report
```

Shows:

- why records added this week
- scars recorded this week
- projects worked on
- context notes

This is a consumer of existing data, not a new data source. It will
be straightforward to build once the other commands are stable.

---

### remnant ui

Purpose: interactive terminal interface.

A keyboard-navigable browser over all records. Built with Textual.
You would be able to scroll through history, open records, add new
ones, and search — without leaving a persistent interactive session.

This is a genuine improvement in usability. It is also the most
work. It will be built after the CLI commands are completely stable
and the data model is not changing frequently.

---

## What Success Looks Like

Remnant is successful when this workflow feels natural and saves
real time:

```
Something is broken or confusing
          ↓
remnant search "the thing"
          ↓
Remnant surfaces a scar or why from months ago
          ↓
Developer avoids rediscovering the same solution
```

And:

```
Developer returns to a project after two weeks away
          ↓
remnant context
          ↓
Branch, last note, related history all visible immediately
          ↓
Developer is back up to speed in under a minute
```

The number of commands does not determine success.
Whether future-you actually uses it without forcing yourself does.

---

## Go / No-Go Criteria

Continue building Remnant if:

- you use it without reminding yourself to
- search returns something useful at least once a week
- context saves you time when returning to a project
- the records accumulate naturally rather than feeling like maintenance
- map and report feel like they belong when you eventually build them

Reconsider the scope if:

- markdown notes consistently feel faster
- you mostly forget to use it
- every new feature feels unrelated to the others
- the database grows more sophisticated than the user value justifies
