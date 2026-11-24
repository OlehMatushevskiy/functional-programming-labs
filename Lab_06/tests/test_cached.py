from concurrent.futures import ThreadPoolExecutor
from inspect import signature
from threading import Event

import pytest

from decorators import cached


def test_cache_key_includes_args_and_kwargs_but_ignores_keyword_order() -> None:
    calls = 0

    def total(value: int, *, factor: int, offset: int) -> int:
        """Apply a factor and offset."""
        nonlocal calls
        calls += 1
        return value * factor + offset

    wrapped = cached()(total)

    assert wrapped(5, factor=2, offset=1) == 11
    assert wrapped(5, offset=1, factor=2) == 11
    assert wrapped(6, factor=2, offset=1) == 13
    assert wrapped(5, factor=3, offset=1) == 16
    assert calls == 3
    assert getattr(wrapped, "__name__") == total.__name__
    assert wrapped.__doc__ == total.__doc__
    assert getattr(wrapped, "__wrapped__") is total
    assert signature(wrapped) == signature(total)


def test_ttl_uses_injected_time_and_expires_at_the_boundary() -> None:
    now = 1_000.0
    calls = 0

    @cached(ttl=1, time_fn=lambda: now)
    def load(value: int) -> int:
        nonlocal calls
        calls += 1
        return value * 2

    assert load(10) == 20
    now = 1_000.99
    assert load(10) == 20 and calls == 1
    now = 1_001.0
    assert load(10) == 20 and calls == 2


def test_selective_invalidation_then_clear_preserves_other_entries() -> None:
    calls = 0

    @cached()
    def load(item: int, *, category: str) -> int:
        nonlocal calls
        calls += 1
        return item

    assert load(1, category="a") == 1
    assert load(1, category="b") == 1
    assert load(2, category="b") == 2
    assert (
        load.cache_invalidate(
            lambda args, kwargs: args == (1,) and kwargs["category"] == "b"
        )
        == 1
    )
    assert load(1, category="a") == 1
    assert load(2, category="b") == 2
    assert calls == 3
    assert load(1, category="b") == 1 and calls == 4
    load.cache_clear()
    assert load(1, category="a") == 1 and calls == 5


def test_cache_skips_exceptions_but_can_store_none() -> None:
    calls = 0

    @cached()
    def load() -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("temporary")

    with pytest.raises(RuntimeError, match="temporary"):
        load()

    assert load() is None
    assert load() is None
    assert calls == 2


def test_zero_ttl_does_not_reuse_a_result() -> None:
    calls = 0

    @cached(ttl=0, time_fn=lambda: 1_000.0)
    def next_value() -> int:
        nonlocal calls
        calls += 1
        return calls

    assert next_value() == 1
    assert next_value() == 2


def test_unhashable_arguments_are_rejected() -> None:
    @cached()
    def total(values: list[int]) -> int:
        return sum(values)

    with pytest.raises(TypeError, match="unhashable"):
        total([1, 2])


@pytest.mark.parametrize("ttl", [-1.0, float("nan"), float("inf")])
def test_invalid_ttl_is_rejected(ttl: float) -> None:
    with pytest.raises(ValueError, match="ttl"):
        cached(ttl=ttl)


def test_clearing_during_a_calculation_does_not_restore_its_stale_result() -> None:
    started = Event()
    release = Event()
    calls = 0

    @cached()
    def load() -> int:
        nonlocal calls
        calls += 1
        result = calls
        if result == 1:
            started.set()
            if not release.wait(timeout=3):
                raise TimeoutError("test did not release the first calculation")
        return result

    with ThreadPoolExecutor(max_workers=1) as executor:
        original = executor.submit(load)
        try:
            assert started.wait(timeout=3)
            load.cache_clear()
        finally:
            release.set()
        assert original.result(timeout=3) == 1

    assert load() == 2
    assert load() == 2
