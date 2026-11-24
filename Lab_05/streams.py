from collections import deque
from collections.abc import Callable, Iterable, Iterator
from itertools import accumulate, count, cycle, dropwhile, islice, takewhile
from math import isfinite
from operator import mul
from typing import TypeVar

T = TypeVar("T")


def fib_stream() -> Iterator[int]:
    previous, current = 0, 1
    while True:
        yield previous
        previous, current = current, previous + current


def naturals(start: int = 1) -> Iterator[int]:
    yield from count(start)


def take(n: int, it: Iterable[T]) -> list[T]:
    if n < 0:
        raise ValueError("n must be non-negative")
    return list(islice(it, n))


def drop(n: int, it: Iterable[T]) -> Iterator[T]:
    if n < 0:
        raise ValueError("n must be non-negative")
    return islice(it, n, None)


def sliding_window(it: Iterable[T], k: int) -> Iterator[tuple[T, ...]]:
    if k <= 0:
        raise ValueError("Window size must be positive")

    window: deque[T] = deque(maxlen=k)
    for item in it:
        window.append(item)
        if len(window) == k:
            yield tuple(window)


def moving_average(it: Iterable[float], k: int) -> Iterator[float]:
    return (sum(window) / k for window in sliding_window(it, k))


def prefix_sums(it: Iterable[float]) -> Iterator[float]:
    return accumulate(it)


def prefix_products(it: Iterable[float]) -> Iterator[float]:
    return accumulate(it, mul)


def take_while(predicate: Callable[[T], bool], it: Iterable[T]) -> Iterator[T]:
    return takewhile(predicate, it)


def drop_while(predicate: Callable[[T], bool], it: Iterable[T]) -> Iterator[T]:
    return dropwhile(predicate, it)


def chunked(it: Iterable[T], k: int) -> Iterator[tuple[T, ...]]:
    """Yield batches of up to k items, including any final short batch."""
    if k <= 0:
        raise ValueError("Batch size must be positive")

    source = iter(it)
    while True:
        batch = tuple(islice(source, k))
        if not batch:
            return
        yield batch


def sensor_stream() -> Iterator[float]:
    """Repeat a fixed series of example readings indefinitely."""
    yield from cycle((12.0, 18.0, 20.0, 22.0, 18.0, 24.0, 25.0, 26.0, 27.0, 75.0, 31.0))


def sensor_batches(
    it: Iterable[float],
    noise_threshold: float,
    emergency_threshold: float,
    batch_size: int,
) -> Iterator[tuple[float, ...]]:
    """Skip initial noise, stop before the emergency value and yield full batches."""
    if (
        not isfinite(noise_threshold)
        or not isfinite(emergency_threshold)
        or noise_threshold >= emergency_threshold
    ):
        raise ValueError("Thresholds must be finite and noise must be below emergency")
    if batch_size <= 0:
        raise ValueError("Batch size must be positive")

    after_noise = drop_while(lambda value: value < noise_threshold, it)
    safe = take_while(lambda value: value < emergency_threshold, after_noise)
    for batch in chunked(safe, batch_size):
        if len(batch) == batch_size:
            yield batch
