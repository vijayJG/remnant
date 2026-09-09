"""
remnant.analyzers.python_ast
-----------------------------
Static analysis of Python source files using the built-in ast module.
No LLM. No guessing. Only what the code actually says.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FunctionInfo:
    name: str
    lineno: int
    is_method: bool = False


@dataclass
class ClassInfo:
    name: str
    lineno: int
    methods: list[str] = field(default_factory=list)


@dataclass
class FileAnalysis:
    path: Path
    imports: list[str] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)
    error: str | None = None


def analyze_file(path: Path) -> FileAnalysis:
    """
    Parse a single Python file and extract its structure.
    Returns a FileAnalysis even on error — check .error field.
    """
    result = FileAnalysis(path=path)

    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as e:
        result.error = f"SyntaxError: {e}"
        return result
    except Exception as e:
        result.error = str(e)
        return result

    for node in ast.walk(tree):
        # Imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                result.imports.append(alias.name.split(".")[0])

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                result.imports.append(node.module.split(".")[0])

        # Top-level functions
        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            result.functions.append(
                FunctionInfo(name=node.name, lineno=node.lineno)
            )

        # Classes and their methods
        elif isinstance(node, ast.ClassDef):
            methods = [
                n.name for n in ast.walk(node)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            result.classes.append(
                ClassInfo(name=node.name, lineno=node.lineno, methods=methods)
            )

        # Function calls
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                result.calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                result.calls.append(node.func.attr)

    # Remove duplicates while preserving order
    result.imports = list(dict.fromkeys(result.imports))
    result.calls = list(dict.fromkeys(result.calls))

    return result


def analyze_project(root: Path, ignore: list[str] | None = None) -> list[FileAnalysis]:
    """
    Analyze all Python files in a directory tree.
    Skips directories in the ignore list.
    """
    ignore = ignore or ["__pycache__", ".venv", "venv", ".git",
                        "node_modules", "dist", "build", ".eggs"]

    results = []
    for py_file in sorted(root.rglob("*.py")):
        if any(part in ignore for part in py_file.parts):
            continue
        results.append(analyze_file(py_file))

    return results


def find_dead_functions(analysis: list[FileAnalysis]) -> list[dict]:
    """
    Find functions that are defined but never called anywhere in the project.
    Only checks same-file calls for now (cross-file is v0.5).

    Returns a list of dicts with path, function name, line, and confidence.
    Never claims certainty — always returns a confidence level.
    """
    dead = []

    for file_analysis in analysis:
        if file_analysis.error:
            continue

        called = set(file_analysis.calls)

        for fn in file_analysis.functions:
            # Skip private/dunder functions — too risky to flag
            if fn.name.startswith("__") and fn.name.endswith("__"):
                continue

            if fn.name not in called:
                # Private functions (_name) get MEDIUM confidence
                # Public functions get HIGH confidence
                confidence = "MEDIUM" if fn.name.startswith("_") else "HIGH"

                dead.append({
                    "path": file_analysis.path,
                    "function": fn.name,
                    "lineno": fn.lineno,
                    "confidence": confidence,
                    "reason": "No calls detected in this file",
                })

    return dead


def find_unused_imports(
    analysis: list[FileAnalysis],
    declared_deps: list[str],
) -> list[dict]:
    """
    Find declared dependencies that are never imported anywhere in the project.
    Compares requirements/pyproject deps against actual import statements.

    Returns list of dicts with package name and confidence.
    """
    all_imports: set[str] = set()
    for fa in analysis:
        all_imports.update(fa.imports)

    unused = []
    for dep in declared_deps:
        # Normalize: requests-toolbelt -> requests_toolbelt
        normalized = dep.lower().replace("-", "_")
        imported = any(
            i.lower().replace("-", "_") == normalized
            for i in all_imports
        )
        if not imported:
            unused.append({
                "package": dep,
                "confidence": "HIGH",
                "reason": "Not found in any import statement",
            })

    return unused
