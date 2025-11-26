"""Helpers for bootstrapping ConSys models.

`make_base` wires a MongoDB connection into a concrete `BaseModel` subclass so
user-defined models inherit the descriptor behavior documented in the handbook.
"""

from ._db import get_db
from .model import BaseModel


def make_base(host, name, login=None, password=None):
    """Return a ready-to-subclass `BaseModel` bound to a Mongo database.

    Args:
        host (str): Mongo host/port pair in `host:port` form.
        name (str): Database name.
        login (str | None): Mongo username (optional).
        password (str | None): Mongo password (optional).
    """

    class Base(BaseModel):
        """Project-specific base model wired to the requested database."""

        _db = get_db(host, name, login, password)

        @property
        def _name(self) -> str:
            """Collection name placeholder; subclasses must override."""
            return None

    return Base
