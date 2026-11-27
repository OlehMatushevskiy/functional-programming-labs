from dataclasses import FrozenInstanceError

import pytest

from evaluator import divide, map_result, unwrap_or
from model import Failure, Result, Success
from pretty import render


def test_divide_returns_typed_success() -> None:
    assert divide(9, 2) == Success(4.5)
    assert divide(0, -2) == Success(0.0)
    assert divide(-6, 2) == Success(-3.0)


def test_divide_by_zero_returns_failure() -> None:
    assert divide(9, 0) == Failure("Ділення на нуль", code="division_by_zero")


def test_divide_returns_failure_for_float_overflow() -> None:
    assert divide(10**1000, 1) == Failure("Частка завелика для float", code="overflow")


def test_map_result_changes_the_value_type_without_mutating_the_input() -> None:
    original = Success(7)
    mapped: Result[str] = map_result(original, str)
    assert mapped == Success("7")
    assert original == Success(7)


def test_map_result_accepts_callable_objects() -> None:
    class Repeat:
        def __call__(self, value: int) -> str:
            return "x" * value

    assert map_result(Success(3), Repeat()) == Success("xxx")


def test_map_result_propagates_failure_without_calling_transform() -> None:
    def unexpected_call(value: int) -> str:
        raise AssertionError(f"Unexpected call with {value}")

    failure = Failure("Помилка")
    failed_result: Result[int] = failure
    mapped: Result[str] = map_result(failed_result, unexpected_call)
    assert mapped is failure


def test_map_result_can_process_nested_results() -> None:
    def increment_inner(result: Result[int]) -> Result[int]:
        return map_result(result, lambda value: value + 1)

    nested: Result[Result[int]] = Success(Success(7))
    assert map_result(nested, increment_inner) == Success(Success(8))

    inner_failure = Failure("Вкладена помилка")
    assert map_result(Success(inner_failure), increment_inner) == Success(inner_failure)


@pytest.mark.parametrize("value", [0, False, "", None])
def test_unwrap_or_preserves_falsy_success_values(value: object) -> None:
    fallback = object()
    assert unwrap_or(Success(value), fallback) is value


def test_unwrap_or_returns_the_fallback_on_failure() -> None:
    assert unwrap_or(Failure("Помилка"), "запасне значення") == "запасне значення"


def test_nested_result_can_be_unwrapped_one_level_at_a_time() -> None:
    nested: Result[Result[int]] = Success(Success(7))
    inner = unwrap_or(nested, Failure("Немає внутрішнього результату"))
    assert inner == Success(7)
    assert unwrap_or(inner, 0) == 7


def test_render_formats_both_variants() -> None:
    assert render(Success("4.50")) == "Success('4.50')"
    assert render(Failure("Щось пішло не так")) == (
        "Failure[operation_failed]: Щось пішло не так"
    )


@pytest.mark.parametrize(
    ("result", "attribute", "new_value"),
    [(Success(1), "value", 2), (Failure("Помилка"), "message", "Інша помилка")],
)
def test_result_nodes_are_frozen(
    result: Result[int], attribute: str, new_value: object
) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(result, attribute, new_value)
