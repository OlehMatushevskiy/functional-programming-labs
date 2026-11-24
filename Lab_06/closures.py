from collections.abc import Callable


def make_counter(start: int = 0) -> Callable[[], int]:
    """Return a function with its own call counter."""
    value = start

    def increment() -> int:
        nonlocal value
        value += 1
        return value

    return increment


def make_logger(
    prefix: str, *, sink: Callable[[str], None] = print
) -> Callable[[str], None]:
    """Prefix messages before passing them to the supplied sink."""

    def log(message: str) -> None:
        sink(f"[{prefix}] {message}")

    return log


def make_query_normalizer(*, case_sensitive: bool = False) -> Callable[[str], str]:
    """Return a query normalizer with a fixed case policy."""

    def normalize(query: str) -> str:
        collapsed = " ".join(query.split())
        return collapsed if case_sensitive else collapsed.casefold()

    return normalize
