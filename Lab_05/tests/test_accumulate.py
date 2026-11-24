from streams import naturals, prefix_products, prefix_sums, take


def test_prefix_sums_and_products() -> None:
    assert list(prefix_sums([1, 2, 3, 4])) == [1, 3, 6, 10]
    assert list(prefix_products([1, 2, 3, 4])) == [1, 2, 6, 24]


def test_prefix_operations_support_empty_and_infinite_sources() -> None:
    assert list(prefix_sums(())) == []
    assert list(prefix_products(())) == []
    assert take(4, prefix_sums(naturals())) == [1, 3, 6, 10]
