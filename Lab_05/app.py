from itertools import repeat

from streams import (
    drop,
    fib_stream,
    moving_average,
    naturals,
    prefix_products,
    prefix_sums,
    sensor_batches,
    sensor_stream,
    sliding_window,
    take,
)


def main() -> None:
    packets = sensor_batches(
        sensor_stream(), noise_threshold=20, emergency_threshold=75, batch_size=3
    )
    print("Пакети датчика:", take(10, packets))
    print("Фібоначчі, перші 10:", take(10, fib_stream()))
    print("Фібоначчі після пропуску 5:", take(4, drop(5, fib_stream())))
    print("Натуральні після пропуску 3:", take(4, drop(3, naturals())))
    print(
        "Ковзні суми:",
        take(4, (sum(window) for window in sliding_window(naturals(), 3))),
    )
    print("Ковзні середні:", take(4, moving_average(naturals(), 3)))
    print("Префіксні суми:", list(prefix_sums([1, 2, 3, 4])))
    print("Префіксні добутки:", list(prefix_products([1, 2, 3, 4])))
    print("Перші три повтори:", take(3, repeat(10)))


if __name__ == "__main__":
    main()
