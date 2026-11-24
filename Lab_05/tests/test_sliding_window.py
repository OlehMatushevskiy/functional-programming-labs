from itertools import repeat

import pytest

from streams import moving_average, naturals, sliding_window, take


@pytest.mark.parametrize(
    ("items", "size", "expected"),
    [
        ([1, 2, 3, 4], 3, [(1, 2, 3), (2, 3, 4)]),
        ([1, 2, 3], 1, [(1,), (2,), (3,)]),
        ([1, 2, 3], 3, [(1, 2, 3)]),
        ([1, 2], 3, []),
        ([], 2, []),
    ],
)
def test_windows_and_finite_boundaries(
    items: list[int], size: int, expected: list[tuple[int, ...]]
) -> None:
    assert list(sliding_window(iter(items), size)) == expected


@pytest.mark.parametrize("invalid_size", [0, -1])
def test_window_rejects_invalid_size(invalid_size: int) -> None:
    with pytest.raises(ValueError, match="Window size"):
        list(sliding_window([1, 2], invalid_size))


def test_moving_average_works_on_a_finite_and_an_infinite_source() -> None:
    assert list(moving_average([2, 4, 6, 8], 2)) == [3.0, 5.0, 7.0]
    assert take(4, moving_average(repeat(10), 3)) == [10.0] * 4


def test_windows_do_not_read_ahead() -> None:
    source = naturals()

    assert take(2, sliding_window(source, 3)) == [(1, 2, 3), (2, 3, 4)]
    assert next(source) == 5
