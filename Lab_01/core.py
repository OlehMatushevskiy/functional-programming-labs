# The assignment requires typing.Callable.
from collections.abc import Sequence
from typing import Callable, TypedDict, TypeVar  # noqa: UP035


class MeterReading(TypedDict):
    meter_id: str
    previous: float
    current: float
    tariff_group: str


class Bill(MeterReading):
    consumption: float
    rate: float
    subtotal: float
    amount_due: float


class BillingReport(TypedDict):
    bills: list[Bill]
    total_due: float


TariffPolicy = Callable[[str], float]
BenefitPolicy = Callable[[str, float], float]


def calculate_consumption(previous: float, current: float) -> float:
    if not 0 <= previous <= current:
        raise ValueError("Readings must satisfy 0 <= previous <= current")
    return current - previous


def calculate_bill(
    reading: MeterReading,
    *,
    tariff_for: TariffPolicy,
    apply_benefit: BenefitPolicy,
) -> Bill:
    consumption = calculate_consumption(reading["previous"], reading["current"])
    group = reading["tariff_group"]
    rate = tariff_for(group)
    subtotal = consumption * rate
    return {
        **reading,
        "consumption": consumption,
        "rate": rate,
        "subtotal": subtotal,
        "amount_due": apply_benefit(group, subtotal),
    }


def process_readings(
    readings: Sequence[MeterReading],
    *,
    tariff_for: TariffPolicy,
    apply_benefit: BenefitPolicy,
) -> BillingReport:
    bills = [
        calculate_bill(reading, tariff_for=tariff_for, apply_benefit=apply_benefit)
        for reading in readings
    ]
    return {
        "bills": bills,
        "total_due": sum((bill["amount_due"] for bill in bills), start=0.0),
    }


def make_processor(
    *,
    tariff_for: TariffPolicy,
    apply_benefit: BenefitPolicy,
) -> Callable[[Sequence[MeterReading]], BillingReport]:
    def process(readings: Sequence[MeterReading]) -> BillingReport:
        return process_readings(
            readings, tariff_for=tariff_for, apply_benefit=apply_benefit
        )

    return process


A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def compose(outer: Callable[[B], C], inner: Callable[[A], B]) -> Callable[[A], C]:
    def composed(value: A) -> C:
        return outer(inner(value))

    return composed


def make_multiplier(factor: int) -> Callable[[int], int]:
    def multiply(value: int) -> int:
        return value * factor

    return multiply
