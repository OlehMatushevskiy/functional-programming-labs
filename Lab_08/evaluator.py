from typing import TypeVar

from model import Failure, Result, Success, Transform

T = TypeVar("T")
U = TypeVar("U")


def divide(dividend: int, divisor: int) -> Result[float]:
    match divisor:
        case 0:
            return Failure("Ділення на нуль", code="division_by_zero")
        case _:
            try:
                return Success(dividend / divisor)
            except OverflowError:
                return Failure("Частка завелика для float", code="overflow")


def map_result(result: Result[T], transform: Transform[T, U]) -> Result[U]:
    match result:
        case Success(value=value):
            return Success(transform(value))
        case Failure():
            return result


def unwrap_or(result: Result[T], default: T) -> T:
    match result:
        case Success(value=value):
            return value
        case Failure():
            return default
