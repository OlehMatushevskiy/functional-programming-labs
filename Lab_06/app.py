from closures import make_counter, make_logger
from decorators import retries
from search import Product, make_search


def main() -> None:
    products = (
        Product(1, "Миша Logitech", "Периферія"),
        Product(2, "Клавіатура", "Периферія"),
        Product(3, "Ігрова миша", "Ігри"),
    )
    now = 0.0
    search = make_search(
        products, ttl=30, time_fn=lambda: now, logger=make_logger("ПОШУК")
    )
    print("Перший пошук:", [product.id for product in search("  МИША ")])
    print("Повтор із кешу:", [product.id for product in search("миша")])
    print("Пошук із limit=1:", [product.id for product in search("миша", limit=1)])
    removed = search.cache_invalidate(
        lambda args, kwargs: args == ("миша",) and kwargs.get("limit") == 1
    )
    print("Видалено за предикатом:", removed)
    print(
        "Повтор після інвалідації:", [product.id for product in search("миша", limit=1)]
    )
    search.cache_clear()
    print("Після повного очищення:", [product.id for product in search("миша")])
    now += 30
    print("Після спливу TTL:", [product.id for product in search("миша")])

    next_attempt = make_counter()

    @retries(attempts=3, exceptions=(TimeoutError,), sleep=lambda _: None)
    def simulated_call() -> int:
        attempt = next_attempt()
        if attempt < 3:
            raise TimeoutError("temporary demo failure")
        return attempt

    print("Імітація повторів: успіх зі спроби", simulated_call())


if __name__ == "__main__":
    main()
