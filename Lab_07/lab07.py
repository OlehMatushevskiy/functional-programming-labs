from collections.abc import Callable, Mapping
from functools import partial, reduce
from math import isfinite
from operator import itemgetter, methodcaller
from typing import Any, TypedDict

from loaders import RawBooking, load_bookings
from models import Booking


class BookingResult(TypedDict):
    guest: str
    nights: int
    room_type: str
    price: float
    status: str
    total_price: float


def pipeline(value: Any, *funcs: Callable[[Any], Any]) -> Any:
    return reduce(lambda result, step: step(result), funcs, value)


_get_fields = itemgetter("guest", "nights", "room_type", "price", "status")
_strip = methodcaller("strip")
_lower = methodcaller("lower")
_title = methodcaller("title")


def _normalize_booking(row: RawBooking, *, tariffs: Mapping[str, float]) -> Booking:
    guest, nights, room_type, price, status = _get_fields(row)
    room = _lower(_strip(room_type))
    booking = Booking(
        guest=_title(_strip(guest)),
        nights=int(str(nights)),
        room_type=room,
        price=float(str(price)),
        status=_lower(_strip(status)),
        rate=tariffs.get(room, 1.0),
    )
    if not isfinite(booking.total_price):
        raise ValueError("Booking total must be finite")
    return booking


def _is_confirmed(booking: Booking) -> bool:
    return booking.status == "confirmed"


def _rank_key(booking: Booking) -> tuple[float, str]:
    return -booking.total_price, booking.guest


def clean_and_rank(
    path_or_str: object, top: int = 3, *, tariffs: Mapping[str, float] | None = None
) -> list[BookingResult]:
    rates = {_lower(_strip(room)): rate for room, rate in (tariffs or {}).items()}
    normalize = partial(_normalize_booking, tariffs=rates)
    selected: list[Booking] = pipeline(
        path_or_str,
        load_bookings,
        partial(map, normalize),
        partial(filter, _is_confirmed),
        partial(sorted, key=_rank_key),
        lambda bookings: bookings[: max(top, 0)],
    )
    return [
        BookingResult(
            guest=booking.guest,
            nights=booking.nights,
            room_type=booking.room_type,
            price=booking.price,
            status=booking.status,
            total_price=booking.total_price,
        )
        for booking in selected
    ]
