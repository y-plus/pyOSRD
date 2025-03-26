import pytest
from pyosrd.agents.decision_tree import DecisionTree


@pytest.fixture
def tree() -> DecisionTree:
    return DecisionTree(
        actions=['A', 'B', 'C'],
        nodes={
            '': None,
            'A': None,
            'B': 1,
            'C': 1,
            'BA': None,
            'BB': None,
            'CA': None,
        }
    )


def test_num_actions(tree: DecisionTree):
    assert tree.num_actions == 3


def test_len(tree: DecisionTree):
    assert len(tree) == 7


def test_height(tree: DecisionTree):
    assert tree.height() == 2


def test_depth(tree: DecisionTree):
    assert tree.depth('') == 0
    assert tree.depth('A') == 1
    assert tree.depth('BA') == 2


def test_parent(tree: DecisionTree):
    assert tree.parent('') is None
    assert tree.parent('A') == ''
    assert tree.parent('BA') == 'B'


def test_children(tree: DecisionTree):
    assert tree.children('') == {'A', 'B', 'C'}
    assert len(tree.children('A')) == 0
    assert tree.children('B') == {'BA', 'BB'}
    assert tree.children('C') == {'CA'}


def test_num_children(tree: DecisionTree):
    assert tree.num_children('') == 3
    assert tree.num_children('A') == 0
    assert tree.num_children('B') == 2
    assert tree.num_children('C') == 1


def test_missing_children_edges(tree: DecisionTree):
    assert tree.missing_children_edges('') == []
    assert tree.missing_children_edges('A') == ['A', 'B', 'C']
    assert tree.missing_children_edges('B') == ['C']
    assert tree.missing_children_edges('C') == ['B', 'C']


def test_missing_brothers_edges(tree: DecisionTree):
    assert tree.missing_brothers_edges('') is None
    assert tree.missing_brothers_edges('A') == []
    assert tree.missing_brothers_edges('BA') == ['C']
    assert tree.missing_brothers_edges('CA') == ['B', 'C']


def test_missing_children(tree: DecisionTree):
    assert tree.missing_children('') == []
    assert tree.missing_children('A') == ['AA', 'AB', 'AC']
    assert tree.missing_children('B') == ['BC']
    assert tree.missing_children('C') == ['CB', 'CC']


def test_missing_brothers(tree: DecisionTree):
    assert tree.missing_brothers('') is None
    assert tree.missing_brothers('A') == []
    assert tree.missing_brothers('BA') == ['BC']
    assert tree.missing_brothers('CA') == ['CB', 'CC']


def test_max_num_sucessors(tree: DecisionTree):
    assert tree.max_num_sucessors('', 0) == 0
    assert tree.max_num_sucessors('', 1) == 3
    assert tree.max_num_sucessors('', 2) == 12

    assert tree.max_num_sucessors('A', 1) == 0
    assert tree.max_num_sucessors('A', 2) == 3
    assert tree.max_num_sucessors('A', 3) == 12
    assert tree.max_num_sucessors('A', 4) == 39

    assert tree.max_num_sucessors('BA', 2) == 0
    assert tree.max_num_sucessors('BA', 3) == 3
    assert tree.max_num_sucessors('BA', 4) == 12


def test_num_successors_on_missing_children_branches(tree: DecisionTree):
    assert tree.num_successors_on_missing_children_branches('', 0) == 0
    assert tree.num_successors_on_missing_children_branches('', 1) == 0
    assert tree.num_successors_on_missing_children_branches('', 2) == 0

    assert tree.num_successors_on_missing_children_branches('A', 1) == 0
    
    assert tree.num_successors_on_missing_children_branches('A', 2) == 3
    assert tree.num_successors_on_missing_children_branches('B', 2) == 1
    assert tree.num_successors_on_missing_children_branches('C', 2) == 2
    
    assert tree.num_successors_on_missing_children_branches('A', 3) == 12
    assert tree.num_successors_on_missing_children_branches('B', 3) == 4
    assert tree.num_successors_on_missing_children_branches('C', 3) == 8
    
    assert tree.num_successors_on_missing_children_branches('BA', 3) == 3
    assert tree.num_successors_on_missing_children_branches('BB', 3) == 3
    assert tree.num_successors_on_missing_children_branches('CA', 3) == 3


def test_node_states(tree: DecisionTree) -> None:
    assert tree.unfinished_nodes == {'B', 'C'}
    assert tree.finished_nodes == {'A', 'BA', 'BB', 'CA'}
    tree.update_nodes_states()
    assert tree.unfinished_nodes == {'B', 'C'}
    assert tree.finished_nodes == {'A', 'BA', 'BB', 'CA'}


def test_node_states2(tree: DecisionTree) -> None:
    tree.nodes['BC'] = 1
    assert tree.unfinished_nodes == {'B', 'C', 'BC'}
    assert tree.finished_nodes == {'A', 'BA', 'BB', 'CA'}
    tree.update_nodes_states()
    assert tree.unfinished_nodes == {'B', 'C', 'BC'}
    assert tree.finished_nodes == {'A', 'BA', 'BB', 'CA'}


def test_node_states3(tree: DecisionTree) -> None:
    tree.nodes['BC'] = None
    assert tree.unfinished_nodes == {'B', 'C'}
    assert tree.finished_nodes == {'A', 'BA', 'BB', 'CA', 'BC'}
    tree.update_nodes_states()
    assert tree.unfinished_nodes == {'C'}
    assert tree.finished_nodes == {'A', 'BA', 'BB', 'CA', 'BC', 'B'}


def test_add(tree: DecisionTree) -> None:
    paths = [
        DecisionTree(nodes={'': None, 'B': 1, 'BA': None}),
        DecisionTree(nodes={'': None, 'A': None}),
        DecisionTree(nodes={'': None, 'B': 1, 'BB': None}),
        DecisionTree(nodes={'': None, 'C': 1, 'CA': None}),
    ]
    new_tree = DecisionTree()
    for path in paths:
        new_tree.add(path)
    assert new_tree.nodes == tree.nodes


def test_add_not_overwrite(tree: DecisionTree) -> None:

    paths = [
        DecisionTree(nodes={'': None, 'B': 1, 'BA': None}),
        DecisionTree(nodes={'': None, 'A': None}),
        DecisionTree(nodes={'': None, 'B': 1, 'BB': None}),
        DecisionTree(nodes={'': None, 'C': 1, 'CA': None}),
        DecisionTree(actions=tree.actions, nodes={'': None, 'C': 1, 'CA': None}),
    ]
    new_tree = DecisionTree()
    for path in paths:
        new_tree.add(path)
    assert new_tree.nodes == tree.nodes

