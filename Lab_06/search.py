from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import wraps
from itertools import islice
from time import monotonic, perf_counter
from typing import Protocol, cast

from closures import make_query_normalizer
from decorators import CachePredicate, cached, timed


@dataclass(frozen=True, slots=True)
class Product:
    id: int
    name: str
    category: str


class SearchFunction(Protocol):
    def __call__(
        self, query: str, *, category: str | None = None, limit: int | None = None
    ) -> tuple[Product, ...]: ...

    def cache_clear(self) -> None: ...

    def cache_invalidate(self, predicate: CachePredicate) -> int: ...


def make_search(
    products: Iterable[Product],
    *,
    normalize: Callable[[str], str] | None = None,
    ttl: float | None = None,
    time_fn: Callable[[], float] = monotonic,
    clock: Callable[[], float] = perf_counter,
    logger: Callable[[str], None] = print,
) -> SearchFunction:
    """Return a timed search with its own cache and query normalization."""
    catalog = tuple(products)
    normalize_query = make_query_normalizer() if normalize is None else normalize

    @cached(ttl=ttl, time_fn=time_fn)
    @timed("search", logger=logger, clock=clock)
    def find(
        query: str, *, category: str | None = None, limit: int | None = None
    ) -> tuple[Product, ...]:
        matches = (
            product
            for product in catalog
            if query in normalize_query(product.name)
            and (category is None or category == normalize_query(product.category))
        )
        return tuple(islice(matches, limit))

    @wraps(find)
    def search(
        query: str, *, category: str | None = None, limit: int | None = None
    ) -> tuple[Product, ...]:
        if limit is not None and limit < 0:
            raise ValueError("limit must be non-negative")
        normalized_category = None if category is None else normalize_query(category)
        return find(normalize_query(query), category=normalized_category, limit=limit)

    return cast(SearchFunction, search)
