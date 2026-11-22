from collections.abc import MutableMapping
from dataclasses import FrozenInstanceError
from types import MappingProxyType
from typing import cast

import pytest

from core import (
    add_option,
    apply_discount,
    calculate_subtotal,
    change_status,
    extend_rental,
    freeze,
)
from model import Car, Invoice, Rental, RentalOption, RentalStatus


@pytest.fixture
def rental() -> Rental:
    return Rental(1, Car(7, "Toyota Corolla", 1000.0, frozenset({"automatic"})), 2)


def test_add_option_returns_new_rental_and_preserves_order(rental: Rental) -> None:
    gps = RentalOption("GPS", 100.0)
    seat = RentalOption("Child seat", 80.0)
    with_gps = add_option(rental, gps)
    with_both = add_option(with_gps, seat)

    assert rental.options == ()
    assert with_gps.options == (gps,)
    assert with_both.options == (gps, seat)
    assert with_gps is not rental
    assert with_both is not with_gps


def test_extend_rental_returns_new_copy(rental: Rental) -> None:
    extended = extend_rental(rental, 3)

    assert extended is not rental
    assert extended.days == 5 and rental.days == 2
    assert extended.car == rental.car and extended.status == rental.status


def test_change_status_returns_new_copy(rental: Rental) -> None:
    active = change_status(rental, "active")

    assert active is not rental
    assert active.status == "active" and rental.status == "booked"
    assert active.days == rental.days and active.options == rental.options


@pytest.mark.parametrize("extra_days", [0, -1, True, 1.5])
def test_extend_rejects_invalid_duration(rental: Rental, extra_days: int) -> None:
    with pytest.raises(ValueError, match="Extra days"):
        extend_rental(rental, extra_days)


def test_constructor_rejects_invalid_duration(rental: Rental) -> None:
    with pytest.raises(ValueError, match="Rental duration"):
        Rental(2, rental.car, 0)


def test_rejects_unknown_status(rental: Rental) -> None:
    with pytest.raises(ValueError, match="Unknown rental status"):
        change_status(rental, cast(RentalStatus, "invalid"))


def test_rental_and_car_are_frozen(rental: Rental) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(rental, "days", 99)
    with pytest.raises(FrozenInstanceError):
        setattr(rental.car, "model", "Changed")
    assert isinstance(rental.options, tuple)
    assert isinstance(rental.car.features, frozenset)


def test_metadata_is_a_copied_read_only_mapping(rental: Rental) -> None:
    source = {"pickup": "Lviv"}
    saved = Rental(2, rental.car, 2, meta=source)
    source["pickup"] = "Kyiv"

    assert isinstance(saved.meta, MappingProxyType)
    assert saved.meta["pickup"] == "Lviv"
    assert extend_rental(saved, 1).meta == saved.meta
    with pytest.raises(TypeError):
        cast(MutableMapping[str, str], saved.meta)["pickup"] = "Odesa"


def test_versions_remain_hashable(rental: Rental) -> None:
    longer = extend_rental(rental, 1)

    assert len({rental, longer}) == 2
    indexed = {rental: "original", longer: "updated"}
    assert indexed[rental] == "original"
    equal_rental = Rental(rental.id, rental.car, rental.days, meta=dict(rental.meta))
    assert equal_rental == rental and hash(equal_rental) == hash(rental)


def test_discount_returns_new_invoice_without_changing_rental(rental: Rental) -> None:
    updated = extend_rental(add_option(rental, RentalOption("GPS", 100)), 2)

    first = apply_discount(updated, 0.1)
    second = apply_discount(updated, 0.1)

    assert calculate_subtotal(updated) == 4400.0
    assert first == second == Invoice(1, 4400.0, 0.1, 3960.0)
    assert first is not second
    assert updated.days == 4 and updated.options == (RentalOption("GPS", 100),)
    assert rental.days == 2 and rental.options == ()


@pytest.mark.parametrize("discount_rate", [-0.01, 1.01, float("nan")])
def test_discount_rejects_invalid_rate(rental: Rental, discount_rate: float) -> None:
    with pytest.raises(ValueError, match="Discount rate"):
        apply_discount(rental, discount_rate)


def test_freeze_recursively_copies_nested_collections() -> None:
    stops = ["Lviv"]
    extras = {"GPS"}
    source = {"route": {"stops": stops, "extras": extras}}

    frozen = freeze(source)
    stops.append("Kyiv")
    extras.add("Child seat")

    assert isinstance(frozen, MappingProxyType)
    route = frozen["route"]
    assert isinstance(route, MappingProxyType)
    assert route["stops"] == ("Lviv",)
    assert route["extras"] == frozenset({"GPS"})
    with pytest.raises(TypeError):
        cast(MutableMapping[str, object], route)["stops"] = ()
