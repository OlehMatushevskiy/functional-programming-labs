from dataclasses import dataclass
from functools import total_ordering


@total_ordering
@dataclass(frozen=True)
class Booking:
    guest: str
    nights: int
    room_type: str
    price: float
    status: str
    rate: float = 1.0

    @property
    def total_price(self) -> float:
        return self.nights * self.price * self.rate

    def _order_key(self) -> tuple[float, str, str, int, float, str, float]:
        return (
            self.total_price,
            self.guest,
            self.room_type,
            self.nights,
            self.price,
            self.status,
            self.rate,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Booking):
            return NotImplemented
        return self._order_key() == other._order_key()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Booking):
            return NotImplemented
        return self._order_key() < other._order_key()
