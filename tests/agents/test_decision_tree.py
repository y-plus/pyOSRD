import pytest
from pyosrd.agents.decision_tree import DecisionTree


@pytest.fixture
def tree() -> DecisionTree:
    return DecisionTree(
        actions=['A', 'B', 'C'],
        nodes={
            '': None,
            'A': None,
            'B': None,
            'C': None,
            'BA': None,
            'BB': None,
            'CB': None,
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
    assert tree.children('C') == {'CB'}


def test_num_children(tree: DecisionTree):
    assert tree.num_children('') == 3
    assert tree.num_children('A') == 0
    assert tree.num_children('B') == 2
    assert tree.num_children('C') == 1


def test_missing_children(tree: DecisionTree):
    assert tree.missing_children('') == []
    assert tree.missing_children('A') == ['A', 'B', 'C']
    assert tree.missing_children('B') == ['C']
    assert tree.missing_children('C') == ['A', 'C']


def test_is_leaf(tree: DecisionTree):
    assert not tree.is_leaf('')
    assert tree.is_leaf('A')
    assert not tree.is_leaf('B')
    assert not tree.is_leaf('C')
    assert tree.is_leaf('BA')
    assert tree.is_leaf('CB')


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
    assert tree.num_successors_on_missing_children_branches('CB', 3) == 3
