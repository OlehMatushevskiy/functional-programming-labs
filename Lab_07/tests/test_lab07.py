import json
from collections.abc import Callable
from functools import partial
from io import StringIO
from operator import attrgetter, itemgetter, methodcaller
from pathlib import Path

import pytest

from lab07 import clean_and_rank, pipeline
from loaders import load_bookings
from models import Booking

_DATA = Path(__file__).resolve().parents[1] / "sample_data.json"


def test_pipeline_uses_initial_value_and_passes_each_result() -> None:
    assert pipeline(3) == 3
    assert pipeline("  Alice ", methodcaller("strip"), methodcaller("upper"), len) == 5


@pytest.mark.parametrize(
    "source", [str, Path, lambda path: path.read_text(encoding="utf-8")]
)
@pytest.mark.parametrize("suffix", [".json", ".csv"])
def test_dispatch_loads_both_formats(
    source: Callable[[Path], object], suffix: str
) -> None:
    expected = load_bookings(_DATA)
    assert load_bookings(source(_DATA.with_suffix(suffix))) == expected


@pytest.mark.parametrize("suffix", [".json", ".csv"])
def test_dispatch_reads_open_text_file_without_closing_it(suffix: str) -> None:
    with _DATA.with_suffix(suffix).open(encoding="utf-8") as file:
        assert load_bookings(file) == load_bookings(_DATA)
        assert not file.closed


def test_dispatch_handles_text_stream_without_a_filename() -> None:
    source = StringIO(_DATA.with_suffix(".csv").read_text(encoding="utf-8"))
    assert load_bookings(source) == load_bookings(_DATA)
    assert not source.closed


def test_dispatch_accepts_a_list_of_dicts_and_empty_sources() -> None:
    records = [{"guest": "Alice", "nights": 2, "price": 1200}]
    assert load_bookings(records) == records
    assert load_bookings([]) == []
    assert load_bookings("[]") == []


def test_dispatch_accepts_csv_header_in_any_column_order() -> None:
    assert load_bookings("price,status,guest,nights,room_type") == []


def test_dispatch_preserves_csv_values_across_source_types(tmp_path: Path) -> None:
    raw = "guest,nights,room_type,price,status\nAlice,2,suite,10,confirmed  \n"
    path = tmp_path / "bookings.csv"
    path.write_text(raw, encoding="utf-8")

    assert load_bookings(raw) == load_bookings(path) == load_bookings(StringIO(raw))
    assert load_bookings(raw)[0]["status"] == "confirmed  "


def test_dispatch_treats_csv_path_with_comma_as_a_path(tmp_path: Path) -> None:
    path = tmp_path / "hotel,2026.CSV"
    path.write_text(
        _DATA.with_suffix(".csv").read_text(encoding="utf-8-sig"),
        encoding="utf-8-sig",
    )
    assert load_bookings(str(path)) == load_bookings(_DATA)


def test_dispatch_rejects_invalid_input_types(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="Unsupported booking source"):
        load_bookings(1)
    with pytest.raises(ValueError, match="list of booking dictionaries"):
        load_bookings([{"guest": "Alice"}, "Bob"])
    with pytest.raises(ValueError, match="list of booking dictionaries"):
        load_bookings('{"guest": "Alice"}')

    path = tmp_path / "wrong.json"
    path.write_text(json.dumps(str(_DATA)), encoding="utf-8")
    with pytest.raises(ValueError, match="list of booking dictionaries"):
        load_bookings(path)


def test_clean_and_rank_normalizes_filters_and_sorts() -> None:
    result = clean_and_rank(_DATA)
    assert list(map(itemgetter("guest"), result)) == ["Bob", "Alice", "Dan"]
    assert list(map(itemgetter("total_price"), result)) == [3600.0, 3000.0, 3000.0]
    assert result[1] == {
        "guest": "Alice",
        "nights": 2,
        "room_type": "standard",
        "price": 1500.0,
        "status": "confirmed",
        "total_price": 3000.0,
    }


def test_rank_equal_totals_by_guest_even_if_input_order_is_reversed() -> None:
    records = list(reversed(load_bookings(_DATA)))
    assert [row["guest"] for row in clean_and_rank(records)] == ["Bob", "Alice", "Dan"]


def test_partial_tariffs_change_ranking_without_mutating_inputs() -> None:
    records = load_bookings(_DATA)
    before = [row.copy() for row in records]
    rates = {" Suite ": 0.5}
    rank_two = partial(clean_and_rank, top=2, tariffs=rates)

    assert [row["guest"] for row in rank_two(records)] == ["Alice", "Dan"]
    assert rank_two(records) == rank_two(_DATA.with_suffix(".csv"))
    assert clean_and_rank(records, tariffs=rates)[2]["total_price"] == 1800.0
    assert records == before
    assert rates == {" Suite ": 0.5}


@pytest.mark.parametrize(("top", "count"), [(-1, 0), (0, 0), (1, 1), (10, 4)])
def test_clean_and_rank_limits_result_size(top: int, count: int) -> None:
    assert len(clean_and_rank(_DATA, top=top)) == count


def test_rank_accepts_numeric_json_and_empty_records() -> None:
    raw = (
        '[{"guest":" ALICE ","nights":2,"room_type":"standard",'
        '"price":1200.5,"status":"confirmed"}]'
    )
    assert clean_and_rank(raw)[0]["total_price"] == 2401.0
    assert clean_and_rank([]) == []


def test_booking_implements_all_comparisons() -> None:
    first = Booking("Alice", 2, "standard", 1500, "confirmed")
    same = Booking("Alice", 2, "standard", 1500, "confirmed")
    second = Booking("Dan", 3, "standard", 1000, "confirmed")
    third = Booking("Bob", 3, "suite", 1200, "confirmed", rate=1.25)

    assert first == same
    assert first != second
    assert first < second < third
    assert first <= same and first <= second
    assert third > second
    assert third >= second and same >= first
    assert sorted([third, first, second]) == [first, second, third]
    assert list(map(attrgetter("total_price"), [first, second, third])) == [
        3000.0,
        3000.0,
        4500.0,
    ]


def test_booking_returns_not_implemented_for_unrelated_types() -> None:
    booking = Booking("Alice", 2, "standard", 1500, "confirmed")
    assert booking.__eq__(object()) is NotImplemented
    assert booking.__lt__(object()) is NotImplemented
