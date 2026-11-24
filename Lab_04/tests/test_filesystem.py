import sys

import pytest

from algorithms import (
    Directory,
    DirectoryStats,
    File,
    directory_bfs,
    directory_dfs,
    directory_stats,
    directory_stats_iter,
)


def test_empty_directories_count_no_files() -> None:
    directory = Directory("root", (Directory("empty"),))

    assert directory_stats(directory) == DirectoryStats(0, 0)
    assert directory_stats_iter(directory) == DirectoryStats(0, 0)
    assert list(directory_dfs(Directory("empty"))) == [Directory("empty")]
    assert list(directory_bfs(Directory("empty"))) == [Directory("empty")]


def test_nested_file_counts_sizes_and_traversal_order() -> None:
    nested = Directory("src", (File("main.py", 800), Directory("empty")))
    root = Directory("root", (nested, File("data", 50), File("zero", 0)))

    assert directory_stats(root) == directory_stats_iter(root) == DirectoryStats(3, 850)
    assert [entry.name for entry in directory_dfs(root)] == [
        "root",
        "src",
        "main.py",
        "empty",
        "data",
        "zero",
    ]
    assert [entry.name for entry in directory_bfs(root)] == [
        "root",
        "src",
        "data",
        "zero",
        "main.py",
        "empty",
    ]
    assert root.children == (nested, File("data", 50), File("zero", 0))


def test_deep_directory_within_recursion_limit() -> None:
    directory = Directory("leaf", (File("last", 16),))
    for depth in range(75):
        directory = Directory(str(depth), (directory,))

    assert directory_stats(directory) == directory_stats_iter(directory) == (1, 16)


def test_iterative_traversals_on_directory_beyond_recursion_limit() -> None:
    directory = Directory("leaf", (File("last", 16),))
    depth = sys.getrecursionlimit() + 25
    for level in range(depth):
        directory = Directory(str(level), (directory,))

    with pytest.raises(RecursionError):
        directory_stats(directory)

    assert directory_stats_iter(directory) == (1, 16)
    assert sum(1 for _ in directory_dfs(directory)) == depth + 2
    assert sum(1 for _ in directory_bfs(directory)) == depth + 2


def test_rejects_negative_file_size() -> None:
    with pytest.raises(ValueError, match="File size"):
        File("invalid", -5)
