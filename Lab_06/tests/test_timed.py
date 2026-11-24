from inspect import signature
from typing import cast

import pytest

from decorators import TimeUnit, timed


@pytest.mark.parametrize(
    ("unit", "duration"), [("s", "0.012"), ("ms", "12.345"), ("us", "12345.000")]
)
def test_timed_uses_injected_clock_and_logger(unit: TimeUnit, duration: str) -> None:
    ticks = iter((0.0, 0.012345))
    logs: list[str] = []

    def square(value: int) -> int:
        """Square a number."""
        return value * value

    decorated = timed("work", unit=unit, logger=logs.append, clock=ticks.__next__)(
        square
    )

    assert decorated(5) == 25
    assert logs == [f"[timed] work took {duration} {unit}"]
    assert decorated.__name__ == square.__name__
    assert decorated.__doc__ == square.__doc__
    assert getattr(decorated, "__wrapped__") is square
    assert signature(decorated) == signature(square)


def test_timed_logs_even_when_the_original_call_fails() -> None:
    ticks = iter((0.0, 0.125))
    logs: list[str] = []
    error = RuntimeError("original error")

    @timed(logger=logs.append, clock=ticks.__next__)
    def fail() -> None:
        raise error

    with pytest.raises(RuntimeError) as raised:
        fail()

    assert raised.value is error
    assert logs == ["[timed] fail took 125.000 ms"]


def test_timed_rejects_unsupported_unit() -> None:
    with pytest.raises(ValueError, match="unit"):
        timed(unit=cast(TimeUnit, "minutes"))
