from collections.abc import Callable, Iterable, Iterator
from itertools import count

import pytest

from streams import drop, naturals, take


def test_take_advances_an_existing_iterator_once() -> None:
    values = count(1)

    assert take(5, values) == [1, 2, 3, 4, 5]
    assert take(3, values) == [6, 7, 8]


def test_drop_works_on_an_infinite_iterator() -> None:
    assert take(3, drop(10, naturals(0))) == [10, 11, 12]


def test_zero_does_not_discard_or_read_values() -> None:
    source = count(5)

    assert take(0, source) == []
    assert next(drop(0, source)) == 5


def test_empty_and_exhausted_inputs() -> None:
    assert take(3, ()) == []
    assert list(drop(5, [1, 2])) == []


@pytest.mark.parametrize("operation", [take, drop])
def test_take_and_drop_reject_negative_sizes(
    operation: Callable[[int, Iterable[int]], Iterable[int]],
) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        operation(-1, [1, 2])


def test_drop_is_lazy_and_take_reads_only_what_it_requests() -> None:
    visited: list[int] = []

    def readings() -> Iterator[int]:
        for value in count():
            visited.append(value)
            yield value

    skipped = drop(3, readings())
    assert visited == []

    assert take(2, skipped) == [3, 4]
    assert visited == [0, 1, 2, 3, 4]
