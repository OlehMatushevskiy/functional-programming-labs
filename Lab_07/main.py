from operator import add, attrgetter, mul
from pathlib import Path

from lab07 import clean_and_rank, pipeline
from models import Booking

RUN_TESTS = True
_SAMPLE = Path(__file__).with_name("sample_data.json")


def _self_check() -> None:
    assert pipeline(3, lambda x: add(x, 1), lambda x: mul(x, 2)) == 8
    first = Booking("Alice", 2, "standard", 1000, "confirmed")
    second = Booking("Bob", 3, "suite", 1200, "confirmed")
    assert first <= second and second >= first
    assert sorted([second, first]) == [first, second]
    assert list(map(attrgetter("guest"), [first, second])) == ["Alice", "Bob"]
    assert clean_and_rank(_SAMPLE) == clean_and_rank(_SAMPLE.with_suffix(".csv"))
    print("✅ Усі тести пройдено!")


def main() -> None:
    print("Топ-3 підтверджених бронювань:")
    for booking in clean_and_rank(_SAMPLE, tariffs={"suite": 1.25}):
        print(
            f"{booking['guest']} ({booking['room_type']}): {booking['total_price']:.2f}"
        )

    if RUN_TESTS:
        _self_check()


if __name__ == "__main__":
    main()
