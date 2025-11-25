"""
Compatibility helpers for bcrypt / passlib.

Passlib 1.x expects bcrypt to expose ``bcrypt.__about__.__version__`` which
was removed in bcrypt>=5.0. This module ensures the attribute exists so that
passlib can read the version without crashing, even if the environment happens
to have a newer bcrypt build installed.
"""

from __future__ import annotations

try:
    import bcrypt
except Exception:  # pragma: no cover
    bcrypt = None  # type: ignore[assignment]

if bcrypt is not None and not hasattr(bcrypt, "__about__"):
    class _About:
        __slots__ = ("__version__",)

        def __init__(self) -> None:
            self.__version__ = getattr(bcrypt, "__version__", "0")

    bcrypt.__about__ = _About()  # type: ignore[attr-defined]


