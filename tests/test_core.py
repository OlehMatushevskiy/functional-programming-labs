from collections.abc import Callable, Sequence
from copy import deepcopy

import pytest

from core import BillingReport, MeterReading, calculate_consumption, make_processor

Processor = Callable[[Sequence[MeterReading]], BillingReport]


@pytest.fixture
def sample_readings() -> list[MeterReading]:
    return [
        {"meter_id": "A", "previous": 100, "current": 150, "tariff_group": "standard"},
        {"meter_id": "B", "previous": 80, "current": 120, "tariff_group": "reduced"},
    ]


@pytest.fixture
def processor() -> Processor:
    def tariff_for(group: str) -> float:
        return {"standard": 4.0, "reduced": 3.0}[group]

    def apply_benefit(group: str, subtotal: float) -> float:
        return subtotal * 0.75 if group == "reduced" else subtotal

    return make_processor(tariff_for=tariff_for, apply_benefit=apply_benefit)


def test_same_input_and_policies_give_same_result(
    sample_readings: list[MeterReading], processor: Processor
) -> None:
    assert processor(sample_readings) == processor(deepcopy(sample_readings))


def test_processing_preserves_input_records(
    sample_readings: list[MeterReading], processor: Processor
) -> None:
    original = deepcopy(sample_readings)

    report = processor(sample_readings)

    assert sample_readings == original
    assert report["bills"][0] is not sample_readings[0]
    assert report["bills"][1] is not sample_readings[1]


def test_applies_tariff_before_benefit(
    sample_readings: list[MeterReading], processor: Processor
) -> None:
    report = processor(sample_readings)
    standard_bill, reduced_bill = report["bills"]

    assert standard_bill["consumption"] == 50
    assert standard_bill["amount_due"] == 200
    assert reduced_bill["consumption"] == 40
    assert reduced_bill["rate"] == 3.0
    assert reduced_bill["subtotal"] == 120
    assert reduced_bill["amount_due"] == 90
    assert report["total_due"] == 290


def test_can_use_different_policies(sample_readings: list[MeterReading]) -> None:
    processor = make_processor(
        tariff_for=lambda group: 2.0,
        apply_benefit=lambda group, subtotal: subtotal,
    )

    assert processor(sample_readings)["total_due"] == 180


def test_empty_report(processor: Processor) -> None:
    assert processor([]) == {"bills": [], "total_due": 0.0}


def test_zero_consumption() -> None:
    assert calculate_consumption(120, 120) == 0


@pytest.mark.parametrize(("previous", "current"), [(120, 119), (-1, 120)])
def test_rejects_invalid_readings(previous: float, current: float) -> None:
    with pytest.raises(ValueError, match="0 <= previous <= current"):
        calculate_consumption(previous, current)
