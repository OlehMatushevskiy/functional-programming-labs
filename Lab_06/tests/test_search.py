import pytest

from closures import make_counter, make_logger, make_query_normalizer
from search import Product, make_search


def test_closures_keep_independent_counters_and_configurations() -> None:
    first = make_counter(10)
    second = make_counter()
    assert (first(), first(), second(), first()) == (11, 12, 1, 13)
    assert make_query_normalizer()("  ІГРОВА\t МИША ") == "ігрова миша"
    assert (
        make_query_normalizer(case_sensitive=True)("  ІГРОВА   Миша ") == "ІГРОВА Миша"
    )
    logs: list[str] = []
    make_logger("TEST", sink=logs.append)("ready")
    assert logs == ["[TEST] ready"]


def test_normalized_search_reuses_cache_and_can_invalidate_one_query() -> None:
    mouse = Product(1, "Ігрова миша", "Ігри")
    products = [mouse, Product(2, "Клавіатура", "Периферія")]
    logs: list[str] = []
    search = make_search(products, logger=logs.append, clock=lambda: 0.0)

    assert search(" ІГРОВА   МИША ", category=" ІГРИ") == (mouse,)
    assert search("ігрова миша", category="ігри") == (mouse,)
    assert len(logs) == 1
    assert search("ігрова миша", category="ігри", limit=0) == ()
    assert len(logs) == 2
    assert (
        search.cache_invalidate(
            lambda args, kwargs: args == ("ігрова миша",) and kwargs["limit"] is None
        )
        == 1
    )
    assert search("ігрова миша", category="ігри", limit=0) == ()
    assert len(logs) == 2
    assert search("ігрова миша", category="ігри") == (mouse,)
    assert len(logs) == 3

    search.cache_clear()
    assert search("ігрова миша", category="ігри") == (mouse,)
    assert len(logs) == 4


def test_search_uses_a_snapshot_and_rejects_invalid_limit() -> None:
    mouse = Product(1, "Миша Logitech", "Периферія")
    products = [mouse]
    search = make_search(products, logger=lambda _: None, clock=lambda: 0.0)
    products.clear()

    assert search("миша") == (mouse,)
    assert search("миша", category="Ігри") == ()
    with pytest.raises(ValueError, match="limit"):
        search("миша", limit=-1)
