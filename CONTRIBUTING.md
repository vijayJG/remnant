# Contributing to remnant

Thanks for your interest in contributing. remnant is a small, focused project
and every contribution matters.

---

## Getting Started

```bash
git clone https://github.com/yourusername/remnant
cd remnant
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

---

## How to Add a New Feature

1. Check the [issues](https://github.com/yourusername/remnant/issues) for something to work on
2. Comment on the issue to say you're working on it
3. Create a branch: `git checkout -b feature/your-feature`
4. Write your code in `src/remnant/commands/` or `src/remnant/core/`
5. Add tests in `tests/unit/`
6. Run `pytest` — all tests must pass
7. Open a pull request

---

## Code Style

- Follow existing patterns in the codebase
- Run `ruff check src/` before submitting
- Keep functions small and well-named
- Add docstrings to new modules and functions

---

## Good First Issues

Look for issues labeled `good first issue`. These are:
- Well-scoped
- Don't require deep knowledge of the codebase
- Have clear acceptance criteria

---

## Project Structure

```
src/remnant/
├── cli.py              # main entry point
├── commands/           # one file per subcommand
│   ├── why.py
│   ├── scar.py
│   └── context.py
├── core/               # shared infrastructure
│   ├── config.py
│   ├── database.py
│   └── errors.py
├── analyzers/          # static analysis (coming in v0.2)
└── output/             # terminal formatting
    └── terminal.py
```

---

## Questions?

Open an issue with the `question` label. There are no stupid questions.
