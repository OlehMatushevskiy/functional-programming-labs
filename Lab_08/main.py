from evaluator import divide, map_result, unwrap_or
from pretty import render


def format_ratio(value: float) -> str:
    return f"{value:.2f}"


def main() -> None:
    for divisor in (2, 0):
        result = divide(9, divisor)
        formatted = map_result(result, format_ratio)
        print(f"9 / {divisor} → {render(result)}")
        print(f"  map_result: {render(formatted)}")
        print(f"  unwrap_or: {unwrap_or(formatted, 'недоступно')}")


if __name__ == "__main__":
    main()
