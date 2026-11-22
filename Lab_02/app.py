import argparse
import json
from math import isfinite
from pathlib import Path

from core import Record, build_pipeline, reduce_stats


def _read_record(value: object, index: int) -> Record:
    if not isinstance(value, dict):
        raise ValueError(f"Record {index}: expected a JSON object")

    product_id = value.get("id")
    name = value.get("name")
    category = value.get("category")
    price = value.get("price")
    stock = value.get("stock")
    if (
        type(product_id) is not int
        or not isinstance(name, str)
        or not isinstance(category, str)
        or not isinstance(price, (int, float))
        or isinstance(price, bool)
        or not isfinite(price)
        or price < 0
        or type(stock) is not int
        or stock < 0
    ):
        raise ValueError(
            f"Record {index}: expected id (int), name (str), category (str), "
            "price (finite non-negative number) and stock (non-negative int)"
        )
    return {
        "id": product_id,
        "name": name,
        "category": category,
        "price": float(price),
        "stock": stock,
    }


def _read_records(path: Path) -> list[Record]:
    data: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("The input must be a JSON array of warehouse products")
    return [_read_record(value, i) for i, value in enumerate(data, start=1)]


def _non_negative_int(text: str) -> int:
    value = int(text)
    if value < 0:
        raise argparse.ArgumentTypeError("expected a non-negative integer")
    return value


def _non_negative_factor(text: str) -> float:
    value = float(text)
    if not isfinite(value) or value < 0:
        raise argparse.ArgumentTypeError("expected a finite non-negative number")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Аналіз товарів складу")
    sample_file = Path(__file__).resolve().with_name("sample_data.json")
    parser.add_argument("--data", type=Path, default=sample_file)
    parser.add_argument("--top", type=_non_negative_int, default=2)
    parser.add_argument("--boost-category", "--category", default="Електроніка")
    parser.add_argument("--factor", type=_non_negative_factor, default=1.1)
    parser.add_argument("--min-stock", type=_non_negative_int, default=1)
    args = parser.parse_args(argv)

    try:
        records = _read_records(args.data)
        pipeline = build_pipeline(
            top_n=args.top,
            category=args.boost_category,
            factor=args.factor,
            min_stock=args.min_stock,
        )
        selected = pipeline(records)
        stats = reduce_stats(selected)
    except (OSError, ValueError, OverflowError) as exc:
        parser.error(str(exc))

    print(
        json.dumps({"records": selected, "stats": stats}, ensure_ascii=False, indent=2)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
