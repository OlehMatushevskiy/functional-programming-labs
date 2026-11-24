from collections.abc import Callable
from functools import wraps
from math import isfinite
from random import random
from threading import RLock
from time import monotonic, perf_counter
from time import sleep as wait
from typing import Literal, ParamSpec, Protocol, TypeVar, cast

P = ParamSpec("P")
R = TypeVar("R")
R_co = TypeVar("R_co", covariant=True)
TimeUnit = Literal["s", "ms", "us"]
CacheKey = tuple[tuple[object, ...], tuple[tuple[str, object], ...]]
CachePredicate = Callable[[tuple[object, ...], dict[str, object]], bool]


class CachedFunction(Protocol[P, R_co]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...

    def cache_clear(self) -> None: ...

    def cache_invalidate(self, predicate: CachePredicate) -> int: ...


def _discard(message: str) -> None:
    pass


def timed(
    label: str | None = None,
    *,
    unit: TimeUnit = "ms",
    logger: Callable[[str], None] = print,
    clock: Callable[[], float] = perf_counter,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Measure one function call and log its duration, including on failure."""
    factors = {"s": 1.0, "ms": 1_000.0, "us": 1_000_000.0}
    if unit not in factors:
        raise ValueError("unit must be 's', 'ms' or 'us'")
    factor = factors[unit]

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        name = label or getattr(func, "__name__", type(func).__name__)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            started = clock()
            try:
                return func(*args, **kwargs)
            finally:
                duration = (clock() - started) * factor
                logger(f"[timed] {name} took {duration:.3f} {unit}")

        return wrapper

    return decorator


def retries(
    attempts: int = 3,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    delay: float = 0.0,
    backoff: float = 1.0,
    jitter: float = 0.0,
    *,
    sleep: Callable[[float], None] = wait,
    logger: Callable[[str], None] = _discard,
    random_fn: Callable[[], float] = random,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Retry selected exceptions, counting the initial call as an attempt."""
    if type(attempts) is not int or attempts < 1:
        raise ValueError("attempts must be a positive integer")
    if not isfinite(delay) or delay < 0:
        raise ValueError("delay must be finite and non-negative")
    if not isfinite(backoff) or backoff < 1:
        raise ValueError("backoff must be finite and at least 1")
    if not isfinite(jitter) or jitter < 0:
        raise ValueError("jitter must be finite and non-negative")

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as error:
                    if attempt == attempts:
                        logger(f"[retries] fail after {attempt} attempts: {error!r}")
                        raise
                    pause = delay * backoff ** (attempt - 1)
                    if jitter:
                        pause += random_fn() * jitter
                    logger(
                        f"[retries] attempt {attempt} failed: {error!r}; sleeping {pause:.3f}s"
                    )
                    sleep(pause)
                    attempt += 1

        return wrapper

    return decorator


def make_key(args: tuple[object, ...], kwargs: dict[str, object]) -> CacheKey:
    """Include both argument groups independently of keyword order."""
    return args, tuple(sorted(kwargs.items()))


def cached(
    *,
    ttl: float | None = None,
    time_fn: Callable[[], float] = monotonic,
) -> Callable[[Callable[P, R]], CachedFunction[P, R]]:
    """Cache successful calls with hashable arguments and optional expiration."""
    if ttl is not None and (not isfinite(ttl) or ttl < 0):
        raise ValueError("ttl must be finite and non-negative")

    def decorator(func: Callable[P, R]) -> CachedFunction[P, R]:
        cache: dict[CacheKey, tuple[float | None, R]] = {}
        lock = RLock()
        version = 0

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = make_key(args, kwargs)
            with lock:
                entry = cache.get(key)
                if entry is not None:
                    expires_at, result = entry
                    if expires_at is None or time_fn() < expires_at:
                        return result
                    del cache[key]
                initial_version = version

            result = func(*args, **kwargs)
            with lock:
                # An older calculation must not repopulate an invalidated cache.
                if version == initial_version:
                    expires_at = None if ttl is None else time_fn() + ttl
                    cache[key] = expires_at, result
            return result

        def cache_clear() -> None:
            nonlocal version
            with lock:
                cache.clear()
                version += 1

        def cache_invalidate(predicate: CachePredicate) -> int:
            nonlocal version
            with lock:
                keys = [key for key in list(cache) if predicate(key[0], dict(key[1]))]
                removed = 0
                for key in keys:
                    if key in cache:
                        del cache[key]
                        removed += 1
                version += 1
                return removed

        setattr(wrapper, "cache_clear", cache_clear)
        setattr(wrapper, "cache_invalidate", cache_invalidate)
        return cast(CachedFunction[P, R], wrapper)

    return decorator
