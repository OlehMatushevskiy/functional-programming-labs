import argparse
import sys
from statistics import median
from timeit import repeat

from algorithms import (
    Directory,
    File,
    Node,
    directory_bfs,
    directory_dfs,
    directory_stats,
    directory_stats_iter,
    fib,
    fib_iter,
    inorder,
    quicksort,
)


def sample_directory() -> Directory:
    return Directory(
        "project",
        (
            File("README.md", 120),
            Directory("src", (File("main.py", 800), File("utils.py", 440))),
            Directory("assets", (File("logo.png", 1600),)),
            Directory("empty"),
        ),
    )


def print_benchmark(directory: Directory) -> None:
    runs, iterations = 3, 10_000
    recursive = median(
        repeat(lambda: directory_stats(directory), repeat=runs, number=iterations)
    )
    iterative = median(
        repeat(lambda: directory_stats_iter(directory), repeat=runs, number=iterations)
    )
    print(f"Медіана {runs} замірів, кожен по {iterations} підрахунків:")
    print(f"  Рекурсивний підрахунок: {recursive:.4f} с")
    print(f"  Ітеративний DFS: {iterative:.4f} с")


def main() -> None:
    parser = argparse.ArgumentParser(description="Рекурсія та файлова ієрархія")
    parser.add_argument(
        "--benchmark", action="store_true", help="порівняти час підрахунків"
    )
    args = parser.parse_args()

    directory = sample_directory()
    recursive = directory_stats(directory)
    iterative = directory_stats_iter(directory)
    print(f"Рекурсивно: {recursive.file_count} файли, {recursive.total_size} байтів.")
    print(f"Ітеративно: {iterative.file_count} файли, {iterative.total_size} байтів.")
    print("DFS:", ", ".join(entry.name for entry in directory_dfs(directory)))
    print("BFS:", ", ".join(entry.name for entry in directory_bfs(directory)))
    print("QuickSort:", quicksort([5, 1, 3, 1, 2]))
    print("Inorder:", list(inorder(Node(2, Node(1), Node(3)))))

    fib.cache_clear()
    print(f"fib(25): {fib(25)}; fib_iter(25): {fib_iter(25)}.")
    fib(25)
    print(f"Кеш Фібоначчі: {fib.cache_info()}")
    fib.cache_clear()
    print(f"Після cache_clear: {fib.cache_info().currsize}.")
    print(f"Ліміт рекурсії: {sys.getrecursionlimit()}.")

    if args.benchmark:
        print_benchmark(directory)


if __name__ == "__main__":
    main()
