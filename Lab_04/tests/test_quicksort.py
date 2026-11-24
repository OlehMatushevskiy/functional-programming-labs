from random import Random

import pytest

from algorithms import quicksort


@pytest.mark.parametrize("items", [[], [4], [3, 2, 1], [2, 2, 1, 3, 2], [-3, 0, -1]])
def test_quicksort_small_inputs(items: list[int]) -> None:
    original = items.copy()

    result = quicksort(items)

    assert result == sorted(original)
    assert result is not items
    assert items == original


def test_quicksort_matches_sorted_on_random_input() -> None:
    random = Random(7)
    items = tuple(random.randint(-1000, 1000) for _ in range(1000))

    assert quicksort(items) == sorted(items)


def test_three_way_quicksort_handles_many_equal_keys() -> None:
    items = [8] * 4000

    assert quicksort(items) == items
