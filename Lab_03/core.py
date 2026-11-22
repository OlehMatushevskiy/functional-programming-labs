from collections.abc import Mapping
from dataclasses import replace
from types import MappingProxyType

from model import Invoice, Rental, RentalOption, RentalStatus


def add_option(rental: Rental, option: RentalOption) -> Rental:
    return replace(rental, options=rental.options + (option,))


def extend_rental(rental: Rental, extra_days: int) -> Rental:
    if type(extra_days) is not int or extra_days < 1:
        raise ValueError("Extra days must be a positive integer")
    return replace(rental, days=rental.days + extra_days)


def change_status(rental: Rental, status: RentalStatus) -> Rental:
    return replace(rental, status=status)


def calculate_subtotal(rental: Rental) -> float:
    option_rate = sum(option.daily_rate for option in rental.options)
    return round((rental.car.daily_rate + option_rate) * rental.days, 2)


def apply_discount(rental: Rental, discount_rate: float) -> Invoice:
    if not 0 <= discount_rate <= 1:
        raise ValueError("Discount rate must be between 0 and 1")
    subtotal = calculate_subtotal(rental)
    return Invoice(
        rental_id=rental.id,
        subtotal=subtotal,
        discount_rate=discount_rate,
        total=round(subtotal * (1 - discount_rate), 2),
    )


def freeze(obj: object) -> object:
    """Freeze nested built-in containers and copy each mapping."""
    if isinstance(obj, Mapping):
        return MappingProxyType({key: freeze(value) for key, value in obj.items()})
    if isinstance(obj, (list, tuple)):
        return tuple(freeze(value) for value in obj)
    if isinstance(obj, (set, frozenset)):
        return frozenset(freeze(value) for value in obj)
    return obj
