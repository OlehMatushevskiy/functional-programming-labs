from dataclasses import dataclass

from core import add_option, change_status, extend_rental
from model import Car, Rental, RentalOption, RentalStatus

REPETITIONS = 50_000


@dataclass(slots=True)
class MutableRental:
    id: int
    car: Car
    days: int
    options: list[RentalOption]
    status: RentalStatus
    meta: dict[str, str]


def test_before_mutable_updates() -> None:
    car = Car(7, "Toyota Corolla", 1000.0)
    gps = RentalOption("GPS", 100.0)
    meta = {"pickup": "Lviv"}

    for _ in range(REPETITIONS):
        rental = MutableRental(1, car, 2, [], "booked", dict(meta))
        rental.options.append(gps)
        rental.days += 2
        rental.status = "active"

    assert (rental.days, tuple(rental.options), rental.status) == (4, (gps,), "active")


def test_after_immutable_updates() -> None:
    car = Car(7, "Toyota Corolla", 1000.0)
    gps = RentalOption("GPS", 100.0)
    meta = {"pickup": "Lviv"}

    for _ in range(REPETITIONS):
        original = Rental(1, car, 2, meta=meta)
        rental = add_option(original, gps)
        rental = extend_rental(rental, 2)
        rental = change_status(rental, "active")

    assert (rental.days, rental.options, rental.status) == (4, (gps,), "active")
    assert (original.days, original.options, original.status) == (2, (), "booked")
