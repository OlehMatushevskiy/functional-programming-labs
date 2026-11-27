from dataclasses import dataclass
from typing import Generic, Literal, Protocol, TypeAlias, TypeVar

ValueT = TypeVar("ValueT", covariant=True)
InputT = TypeVar("InputT", contravariant=True)

ErrorCode: TypeAlias = Literal["operation_failed", "division_by_zero", "overflow"]


@dataclass(frozen=True)
class Success(Generic[ValueT]):
    value: ValueT


@dataclass(frozen=True)
class Failure:
    message: str
    code: ErrorCode = "operation_failed"


Result: TypeAlias = Success[ValueT] | Failure


class Transform(Protocol[InputT, ValueT]):
    def __call__(self, value: InputT, /) -> ValueT: ...
