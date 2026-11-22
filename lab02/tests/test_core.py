from copy import deepcopy

import pytest

from ..core import (
    Record,
    boost_category,
    build_pipeline,
    compose,
    filter_by_stock,
    juxt,
    pipe,
    reduce_stats,
    sort_by_total_desc,
    take,
    with_total,
)


@pytest.fixture
def records() -> list[Record]:
    return [
        {"id": 3, "name": "Mouse", "category": "electronics", "price": 100, "stock": 2},
        {"id": 2, "name": "Labels", "category": "office", "price": 55, "stock": 4},
        {
            "id": 1,
            "name": "Keyboard",
            "category": "electronics",
            "price": 110,
            "stock": 2,
        },
        {"id": 4, "name": "Cable", "category": "electronics", "price": 400, "stock": 0},
        {"id": 5, "name": "Chair", "category": "office", "price": 300, "stock": 1},
    ]


def test_top_n_and_ties_by_id(records: list[Record]) -> None:
    pipeline = build_pipeline(top_n=2, category="electronics", factor=1.1, min_stock=2)

    result = pipeline(iter(records))

    assert [(record["id"], record["total"]) for record in result] == [
        (1, 242),
        (2, 220),
    ]


def test_changes_only_matching_category(records: list[Record]) -> None:
    result = list(boost_category("electronics", 1.1)(with_total()(records)))

    assert [record["total"] for record in result] == [220, 220, 242, 0, 300]


def test_filter_includes_threshold_and_zero_when_requested(
    records: list[Record],
) -> None:
    assert [record["id"] for record in filter_by_stock(2)(records)] == [3, 2, 1]
    assert list(filter_by_stock(0)(records)) == records


def test_sort_and_take_do_not_reorder_input_list(records: list[Record]) -> None:
    with_values = list(with_total()(records))

    result = take(2)(sort_by_total_desc()(with_values))

    assert [record["id"] for record in with_values] == [3, 2, 1, 4, 5]
    assert [record["id"] for record in result] == [5, 1]


def test_pipeline_does_not_mutate_input_records(records: list[Record]) -> None:
    original = deepcopy(records)
    pipeline = build_pipeline(top_n=10, category="electronics", factor=1.1)

    result = pipeline(records)

    assert records == original
    assert pipeline(records) == result
    by_id = {record["id"]: record for record in records}
    assert all(record is not by_id[record["id"]] for record in result)


@pytest.mark.parametrize("top_n", [0, 1, 8])
def test_top_n_bounds(records: list[Record], top_n: int) -> None:
    assert len(build_pipeline(top_n=top_n)(records)) == min(top_n, 4)


def test_negative_top_n_is_invalid() -> None:
    with pytest.raises(ValueError, match="Top-N must be non-negative"):
        build_pipeline(top_n=-1)


def test_stats_for_selected_records(records: list[Record]) -> None:
    selected = build_pipeline(top_n=2, category="electronics", factor=1.1, min_stock=2)(
        records
    )

    assert reduce_stats(iter(selected)) == {
        "count": 2,
        "inventory_value": 462.0,
        "avg_value": 231.0,
    }


def test_empty_input() -> None:
    assert build_pipeline()([]) == []
    assert reduce_stats(iter([])) == {
        "count": 0,
        "inventory_value": 0.0,
        "avg_value": 0.0,
    }


def test_compose_and_pipe_apply_functions_in_documented_order() -> None:
    def double(value: int) -> int:
        return value * 2

    def increment(value: int) -> int:
        return value + 1

    assert compose(double, increment)(3) == 8
    assert pipe(double, increment)(3) == 7
    assert compose(str, double)(3) == "6"
    assert compose()(3) == pipe()(3) == 3


def test_juxt_passes_same_input_to_each_function() -> None:
    def double(value: int) -> int:
        return value * 2

    assert juxt(double, abs)(-3) == (-6, 3)
