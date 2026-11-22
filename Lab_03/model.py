from collections.abc import Mapping
from dataclasses import dataclass, field
from math import isfinite
from types import MappingProxyType
from typing import Literal

RentalStatus = Literal["booked", "active", "completed", "cancelled"]


@dataclass(frozen=True, slots=True)
class Car:
    id: int
    model: str
    daily_rate: float
    features: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not isfinite(self.daily_rate) or self.daily_rate < 0:
            raise ValueError("Car daily rate must be finite and non-negative")
        object.__setattr__(self, "features", frozenset(self.features))


@dataclass(frozen=True, slots=True)
class RentalOption:
    name: str
    daily_rate: float = 0.0

    def __post_init__(self) -> None:
        if not isfinite(self.daily_rate) or self.daily_rate < 0:
            raise ValueError("Option daily rate must be finite and non-negative")


@dataclass(frozen=True, slots=True)
class Rental:
    id: int
    car: Car
    days: int
    options: tuple[RentalOption, ...] = ()
    status: RentalStatus = "booked"
    # Metadata affects equality, but a mappingproxy is not hashable.
    meta: Mapping[str, str] = field(default_factory=dict, hash=False)

    def __post_init__(self) -> None:
        if type(self.days) is not int or self.days < 1:
            raise ValueError("Rental duration must be a positive integer")
        if self.status not in ("booked", "active", "completed", "cancelled"):
            raise ValueError("Unknown rental status")
        object.__setattr__(self, "options", tuple(self.options))
        object.__setattr__(self, "meta", MappingProxyType(dict(self.meta)))


@dataclass(frozen=True, slots=True)
class Invoice:
    rental_id: int
    subtotal: float
    discount_rate: float
    total: float
