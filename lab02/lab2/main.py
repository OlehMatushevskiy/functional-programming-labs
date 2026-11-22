"""Package entry point for the same CLI as app.py."""

from typing import TYPE_CHECKING

if TYPE_CHECKING or "." in (__package__ or ""):
    from ..app import main
else:
    from app import main


if __name__ == "__main__":
    raise SystemExit(main())
