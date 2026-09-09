"""
remnant.core.git
----------------
Git context extraction for enriching records with
repository, branch, and commit information.
"""

from __future__ import annotations

from pathlib import Path


def get_git_context(path: Path) -> dict:
    """
    Extract git context from the given path.
    Returns a dict with whatever could be found.
    Never raises — returns empty values on any failure.
    """
    result: dict = {
        "project":     None,
        "repository":  None,
        "branch":      None,
        "commit_hash": None,
    }

    try:
        import git
        repo = git.Repo(path, search_parent_directories=True)
        result["project"]     = Path(repo.working_dir).name
        result["branch"]      = repo.active_branch.name
        result["commit_hash"] = repo.head.commit.hexsha[:12]

        # Get remote URL if available
        if repo.remotes:
            result["repository"] = repo.remotes[0].url

    except Exception:
        # Not a git repo, or git not available — that is fine
        pass

    return result
