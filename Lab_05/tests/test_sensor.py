from collections.abc import Iterator
from itertools import repeat

import pytest

from streams import chunked, sensor_batches, sensor_stream, take


def test_sensor_demo_forms_two_full_batches() -> None:
    assert take(10, sensor_batches(sensor_stream(), 20, 75, 3)) == [
        (20, 22, 18),
        (24, 25, 26),
    ]


def test_noise_is_only_dropped_at_start_and_emergency_stops_the_stream() -> None:
    visited: list[float] = []

    def readings() -> Iterator[float]:
        for value in (10.0, 20.0, 18.0, 21.0, 22.0, 75.0, 30.0):
            visited.append(value)
            yield value

    source = readings()
    packets = sensor_batches(source, 20, 75, 2)

    assert visited == []
    assert next(packets) == (20.0, 18.0)
    assert visited == [10.0, 20.0, 18.0]
    assert list(packets) == [(21.0, 22.0)]
    assert visited[-1] == 75.0
    assert next(source) == 30.0


def test_only_fixed_size_sensor_packets_are_emitted() -> None:
    source = iter([20, 21, 22, 75, 30])

    assert list(sensor_batches(source, 20, 75, 2)) == [(20, 21)]
    assert next(source) == 30


@pytest.mark.parametrize("source", [[], [1, 2, 3], [75, 20]])
def test_empty_noise_only_and_immediate_emergency(source: list[float]) -> None:
    assert list(sensor_batches(source, 20, 75, 3)) == []


def test_continuous_safe_stream_can_be_bounded_by_take() -> None:
    assert take(3, sensor_batches(repeat(25), 20, 75, 2)) == [(25, 25)] * 3


def test_chunked_keeps_an_incomplete_batch_for_a_finite_source() -> None:
    assert list(chunked([1, 2, 3, 4, 5], 2)) == [(1, 2), (3, 4), (5,)]
    assert list(chunked([], 2)) == []


@pytest.mark.parametrize("invalid_size", [0, -1])
def test_batch_size_must_be_positive(invalid_size: int) -> None:
    with pytest.raises(ValueError, match="Batch size"):
        list(chunked([20], invalid_size))
    with pytest.raises(ValueError, match="Batch size"):
        list(sensor_batches([20], 20, 75, invalid_size))


@pytest.mark.parametrize(
    ("noise", "emergency"), [(75, 75), (80, 75), (20, float("inf"))]
)
def test_thresholds_must_be_finite_and_ordered(noise: float, emergency: float) -> None:
    with pytest.raises(ValueError, match="Thresholds"):
        list(sensor_batches([21], noise, emergency, 2))
