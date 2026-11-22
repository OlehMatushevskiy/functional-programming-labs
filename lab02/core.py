from collections.abc import Callable, Iterable, Iterator
from fractions import Fraction
from functools import reduce
from itertools import islice
from typing import Any, TypedDict, TypeVar


class Product(TypedDict):
    id: int
    name: str
    category: str
    price: float
    stock: int


class Record(Product, total=False):
    total: float


class Stats(TypedDict):
    count: int
    inventory_value: float
    avg_value: float


T = TypeVar("T")
R = TypeVar("R")
Transform = Callable[[Iterable[Record]], Iterator[Record]]
Pipeline = Callable[[Iterable[Record]], list[Record]]


# Adjacent functions can accept and return different types.
def pipe(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Apply the functions in the order they are passed."""

    def run(value: Any) -> Any:
        for function in funcs:
            value = function(value)
        return value

    return run


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Apply the functions from right to left."""
    return pipe(*reversed(funcs))


def juxt(*funcs: Callable[[T], R]) -> Callable[[T], tuple[R, ...]]:
    """Apply each function to the same input and return their results."""

    def run(value: T) -> tuple[R, ...]:
        return tuple(function(value) for function in funcs)

    return run


def _multiply(amount: float, multiplier: float | int) -> float:
    # Keep decimal prices and factors exact until the result is converted to float.
    return float(Fraction(str(amount)) * Fraction(str(multiplier)))


def with_total() -> Transform:
    return lambda records: map(
        lambda record: {**record, "total": _multiply(record["price"], record["stock"])},
        records,
    )


def boost_category(category: str, factor: float) -> Transform:
    def boost(record: Record) -> Record:
        total = record.get("total", 0.0)
        if record["category"] == category:
            total = _multiply(total, factor)
        return {**record, "total": total}

    return lambda records: map(boost, records)


def filter_by_stock(min_stock: int = 1) -> Transform:
    return lambda records: filter(lambda record: record["stock"] >= min_stock, records)


def sort_by_total_desc() -> Pipeline:
    key: Callable[[Record], tuple[float, ...]] = juxt(
        lambda record: -record.get("total", 0.0), lambda record: record["id"]
    )
    return lambda records: sorted(records, key=key)


def take(n: int) -> Pipeline:
    if n < 0:
        raise ValueError("Top-N must be non-negative")
    return lambda records: list(islice(records, n))


def reduce_stats(records: Iterable[Record]) -> Stats:
    def accumulate(
        current: tuple[int, Fraction], record: Record
    ) -> tuple[int, Fraction]:
        count, total = current
        return count + 1, total + Fraction(str(record.get("total", 0.0)))

    count, total = reduce(accumulate, records, (0, Fraction(0)))
    return {
        "count": count,
        "inventory_value": float(total),
        "avg_value": float(total / count) if count else 0.0,
    }


def build_pipeline(
    top_n: int = 2,
    category: str = "Електроніка",
    factor: float = 1.1,
    min_stock: int = 1,
) -> Pipeline:
    return compose(
        take(top_n),
        sort_by_total_desc(),
        filter_by_stock(min_stock),
        boost_category(category, factor),
        with_total(),
    )
