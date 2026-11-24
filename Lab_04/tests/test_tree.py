from algorithms import (
    Node,
    bfs_level_order,
    dfs_preorder_iter,
    inorder,
    postorder,
    preorder,
)


def test_binary_tree_traversal_order() -> None:
    tree = Node(4, Node(2, Node(1), Node(3)), Node(6, right=Node(7)))

    assert list(preorder(tree)) == [4, 2, 1, 3, 6, 7]
    assert list(inorder(tree)) == [1, 2, 3, 4, 6, 7]
    assert list(postorder(tree)) == [1, 3, 2, 7, 6, 4]
    assert bfs_level_order(tree) == [4, 2, 6, 1, 3, 7]
    assert dfs_preorder_iter(tree) == [4, 2, 1, 3, 6, 7]


def test_empty_binary_tree_has_no_keys() -> None:
    assert list(preorder(None)) == []
    assert list(inorder(None)) == []
    assert list(postorder(None)) == []
    assert bfs_level_order(None) == []
    assert dfs_preorder_iter(None) == []
