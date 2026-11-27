import csv
import json
from functools import singledispatch
from io import StringIO, TextIOBase
from pathlib import Path
from typing import cast

RawBooking = dict[str, object]
_BOOKING_FIELDS = {"guest", "nights", "room_type", "price", "status"}


def _read_csv(text: str) -> list[RawBooking]:
    reader = csv.DictReader(StringIO(text, newline=""))
    if reader.fieldnames is None:
        return []
    if not _BOOKING_FIELDS.issubset(reader.fieldnames):
        raise ValueError("CSV must contain guest, nights, room_type, price and status")
    return list(reader)


def _read_text(text: str) -> list[RawBooking]:
    text = text.lstrip("\ufeff").lstrip()
    if text.startswith(("[", "{")):
        return _load_list(json.loads(text))
    return _read_csv(text)


@singledispatch
def load_bookings(source: object) -> list[RawBooking]:
    raise TypeError(f"Unsupported booking source: {type(source).__name__}")


@load_bookings.register
def _load_string(source: str) -> list[RawBooking]:
    text = source.lstrip("\ufeff").strip()
    first_line = text.splitlines()[0] if text else ""
    header = {column.strip('" ') for column in first_line.split(",")}
    if text.startswith(("[", "{")) or _BOOKING_FIELDS.issubset(header):
        return _read_text(source)
    return load_bookings(Path(source))


@load_bookings.register
def _load_path(source: Path) -> list[RawBooking]:
    with source.open(encoding="utf-8-sig", newline="") as file:
        if source.suffix.lower() == ".json":
            return _load_list(json.load(file))
        if source.suffix.lower() == ".csv":
            return _read_csv(file.read())
        return load_bookings(file)


@load_bookings.register
def _load_file(source: TextIOBase) -> list[RawBooking]:
    return _read_text(source.read())


@load_bookings.register(list)
def _load_list(source: object) -> list[RawBooking]:
    if not isinstance(source, list) or not all(
        isinstance(record, dict) for record in source
    ):
        raise ValueError("Expected a list of booking dictionaries")
    return cast(list[RawBooking], source)
