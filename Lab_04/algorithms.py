from __future__ import annotations

from collections import deque
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from functools import lru_cache
from random import Random
from typing import NamedTuple


def quicksort(xs: Sequence[int], *, seed: int = 42) -> list[int]:
    """Return a sorted copy using a local, reproducible random pivot."""
    random = Random(seed)

    def sort(values: Sequence[int]) -> list[int]:
        if len(values) <= 1:
            return list(values)

        pivot = random.choice(values)
        left = [value for value in values if value < pivot]
        equal = [value for value in values if value == pivot]
        right = [value for value in values if value > pivot]
        return sort(left) + equal + sort(right)

    return sort(xs)


@dataclass(frozen=True, slots=True)
class Node:
    key: int
    left: Node | None = None
    right: Node | None = None


def preorder(tree: Node | None) -> Iterator[int]:
    if tree is None:
        return
    yield tree.key
    yield from preorder(tree.left)
    yield from preorder(tree.right)


def inorder(tree: Node | None) -> Iterator[int]:
    if tree is None:
        return
    yield from inorder(tree.left)
    yield tree.key
    yield from inorder(tree.right)


def postorder(tree: Node | None) -> Iterator[int]:
    if tree is None:
        return
    yield from postorder(tree.left)
    yield from postorder(tree.right)
    yield tree.key


def bfs_level_order(tree: Node | None) -> list[int]:
    if tree is None:
        return []
    queue = deque([tree])
    keys = []
    while queue:
        node = queue.popleft()
        keys.append(node.key)
        if node.left is not None:
            queue.append(node.left)
        if node.right is not None:
            queue.append(node.right)
    return keys


def dfs_preorder_iter(tree: Node | None) -> list[int]:
    if tree is None:
        return []
    stack = [tree]
    keys = []
    while stack:
        node = stack.pop()
        keys.append(node.key)
        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)
    return keys


def _check_index(n: int) -> None:
    if type(n) is not int:
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")


@lru_cache(maxsize=None, typed=True)
def fib(n: int) -> int:
    _check_index(n)
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def fib_iter(n: int) -> int:
    _check_index(n)
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


@dataclass(frozen=True, slots=True)
class File:
    name: str
    size: int

    def __post_init__(self) -> None:
        if type(self.size) is not int or self.size < 0:
            raise ValueError("File size must be a non-negative integer in bytes")


@dataclass(frozen=True, slots=True)
class Directory:
    name: str
    children: tuple[File | Directory, ...] = ()


class DirectoryStats(NamedTuple):
    file_count: int
    total_size: int


def directory_stats(directory: Directory) -> DirectoryStats:
    """Sum direct files and recursively combine the statistics of subdirectories."""
    count = total = 0
    for child in directory.children:
        if isinstance(child, File):
            count += 1
            total += child.size
        else:
            child_count, child_size = directory_stats(child)
            count += child_count
            total += child_size
    return DirectoryStats(count, total)


def directory_dfs(directory: Directory) -> Iterator[File | Directory]:
    """Yield all nodes in depth-first order, starting with the root."""
    stack: list[File | Directory] = [directory]
    while stack:
        entry = stack.pop()
        yield entry
        if isinstance(entry, Directory):
            stack.extend(reversed(entry.children))


def directory_bfs(directory: Directory) -> Iterator[File | Directory]:
    """Yield all nodes by levels, starting with the root."""
    queue: deque[File | Directory] = deque([directory])
    while queue:
        entry = queue.popleft()
        yield entry
        if isinstance(entry, Directory):
            queue.extend(entry.children)


def directory_stats_iter(directory: Directory) -> DirectoryStats:
    count = total = 0
    for entry in directory_dfs(directory):
        if isinstance(entry, File):
            count += 1
            total += entry.size
    return DirectoryStats(count, total)
