from collections.abc import Callable
from typing import cast

import pytest

from algorithms import fib, fib_iter


def test_first_fibonacci_numbers() -> None:
    assert [fib(n) for n in range(10)] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_recursive_and_iterative_fibonacci_agree() -> None:
    assert [fib(n) for n in range(51)] == [fib_iter(n) for n in range(51)]


def test_cache_reports_hits_and_can_be_cleared() -> None:
    fib.cache_clear()
    assert fib(12) == 144
    first = fib.cache_info()

    assert fib(12) == 144
    second = fib.cache_info()
    assert second.hits == first.hits + 1
    assert second.misses == first.misses
    assert second.currsize == 13

    fib.cache_clear()
    assert fib.cache_info().currsize == 0


@pytest.mark.parametrize("fibonacci", [fib, fib_iter])
def test_invalid_fibonacci_indices(fibonacci: Callable[[int], int]) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        fibonacci(-1)
    assert fibonacci(3) == 2
    for invalid in (True, 3.0):
        with pytest.raises(TypeError, match="integer"):
            fibonacci(cast(int, invalid))
