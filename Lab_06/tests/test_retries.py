from inspect import signature

import pytest

from decorators import retries


def test_retries_succeeds_on_third_attempt_with_backoff_and_jitter() -> None:
    calls = 0
    sleeps: list[float] = []
    logs: list[str] = []
    random_values = iter((0.5, 0.25))

    def unstable(value: int, *, offset: int) -> int:
        """Return a value after transient failures."""
        nonlocal calls
        calls += 1
        if calls < 3:
            raise TimeoutError("not yet")
        return value + offset

    wrapped = retries(
        attempts=3,
        exceptions=(TimeoutError,),
        delay=1.0,
        backoff=2.0,
        jitter=0.2,
        sleep=sleeps.append,
        logger=logs.append,
        random_fn=random_values.__next__,
    )(unstable)

    assert wrapped(4, offset=3) == 7
    assert calls == 3
    assert sleeps == pytest.approx([1.1, 2.05])
    assert len(logs) == 2
    assert wrapped.__name__ == unstable.__name__
    assert wrapped.__doc__ == unstable.__doc__
    assert getattr(wrapped, "__wrapped__") is unstable
    assert signature(wrapped) == signature(unstable)


def test_retries_reraises_last_error_and_does_not_sleep_after_last_attempt() -> None:
    sleeps: list[float] = []
    logs: list[str] = []
    failures = iter((TimeoutError("first"), TimeoutError("last")))

    @retries(
        attempts=2, exceptions=(TimeoutError,), sleep=sleeps.append, logger=logs.append
    )
    def fail() -> None:
        raise next(failures)

    with pytest.raises(TimeoutError, match="last"):
        fail()

    assert sleeps == [0.0]
    assert "fail after 2 attempts" in logs[-1]


def test_retries_does_not_catch_unlisted_exceptions() -> None:
    sleeps: list[float] = []
    calls = 0

    @retries(attempts=3, exceptions=(TimeoutError,), sleep=sleeps.append)
    def fail() -> None:
        nonlocal calls
        calls += 1
        raise ValueError("permanent")

    with pytest.raises(ValueError, match="permanent"):
        fail()

    assert calls == 1
    assert sleeps == []


@pytest.mark.parametrize(
    ("attempts", "delay", "backoff", "jitter", "field"),
    [
        (0, 0.0, 1.0, 0.0, "attempts"),
        (3, -1.0, 1.0, 0.0, "delay"),
        (3, 0.0, 0.5, 0.0, "backoff"),
        (3, 0.0, 1.0, float("inf"), "jitter"),
    ],
)
def test_retries_rejects_invalid_settings(
    attempts: int, delay: float, backoff: float, jitter: float, field: str
) -> None:
    with pytest.raises(ValueError, match=field):
        retries(attempts=attempts, delay=delay, backoff=backoff, jitter=jitter)
