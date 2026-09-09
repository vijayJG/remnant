"""
remnant.core.errors
-------------------
Custom exceptions for remnant.
Keeping errors explicit makes debugging much easier.
"""


class RemnantError(Exception):
    """Base exception for all remnant errors."""
    pass


class DatabaseError(RemnantError):
    """Raised when a database operation fails."""
    pass


class ConfigError(RemnantError):
    """Raised when configuration is invalid or missing."""
    pass


class NotFoundError(RemnantError):
    """Raised when a requested record doesn't exist."""
    pass


class PathError(RemnantError):
    """Raised when a filesystem path is invalid or inaccessible."""
    pass
