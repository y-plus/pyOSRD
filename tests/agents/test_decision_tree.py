import pytest
from pyosrd.agents.decision_tree import DecisionTree


@pytest.fixture
def tree() -> DecisionTree:
    return DecisionTree(
        actions=['A', 'B', 'C'],
        nodes={
            '': 1,
            'A': 5,
            'B': dict(),
            'C': dict(),
            'BA': 5,
            'BB': 5,
            'CA': 3,
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


def test_is_root(tree: DecisionTree):
    assert tree.is_root('')
    assert not tree.is_root('A')
    assert not tree.is_root('BB')


def test_parent(tree: DecisionTree):
    assert tree.parent('') is None
    assert tree.parent('A') == ''
    assert tree.parent('BA') == 'B'
    assert tree.parent('BAC') == 'BA'


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


def test_nodes_finished_unfinished_or_solution_(tree: DecisionTree):
    assert tree.solution_nodes == {'A', 'BA', 'BB', 'CA'}
    assert tree.unfinished_nodes == {'B', 'C'}
    assert tree.finished_nodes == {'A', 'BA', 'BB', 'CA'}


def test_nodes_finished_unfinished_or_solution_2(tree: DecisionTree):
    tree.nodes['BC'] = dict()
    assert tree.finished_nodes == {'A', 'B', 'BA', 'BB', 'CA'}
    assert tree.unfinished_nodes == {'C', 'BC'}
    assert tree.solution_nodes == {'A', 'BA', 'BB', 'CA'}


def test_nodes_finished_unfinished_or_solution_3(tree: DecisionTree):
    tree.nodes['BC'] = 5
    assert tree.finished_nodes == {'A', 'B', 'BA', 'BB', 'CA', 'BC'}
    assert tree.unfinished_nodes == {'C'}
    assert tree.solution_nodes == {'A', 'BA', 'BB', 'BC', 'CA'}


def test_combine(tree: DecisionTree):
    paths = [
        DecisionTree(nodes={'': 1, 'B': dict(), 'BA': 5}),
        DecisionTree(nodes={'': 1, 'A': 5}),
        DecisionTree(nodes={'': 1, 'B': dict(), 'BB': 5}),
        DecisionTree(nodes={'': 1, 'C': dict(), 'CA': 3}),
    ]
    new_tree = DecisionTree()
    for path in paths:
        new_tree.combine(path)
    assert new_tree.nodes == tree.nodes


def test_add_not_overwrite(tree: DecisionTree):

    paths = [
        DecisionTree(nodes={'': 1, 'B': dict(), 'BA': 5}),
        DecisionTree(nodes={'': 1, 'A': 5}),
        DecisionTree(nodes={'': 1, 'B': dict(), 'BB': 5}),
        DecisionTree(nodes={'': 1, 'C': dict(), 'CA': 3}),
        DecisionTree(nodes={'': 1, 'C': dict(), 'CA': 3}),
    ]
    new_tree = DecisionTree()
    for path in paths:
        new_tree.combine(path)
    assert new_tree.nodes == tree.nodes


def test_best_solution_confidence(tree: DecisionTree):
    assert tree.depth_completeness_ratio('A') == 1
    assert tree.depth_completeness_ratio('BA') == 1/2

    tree.nodes['BC'] =  5
    assert tree.depth_completeness_ratio('BA') == 4/6

    tree.nodes['BC'] =  dict()
    tree.nodes['BCA'] =  5
    assert tree.depth_completeness_ratio('BA') == 4/6
    assert tree.depth_completeness_ratio('BCA') == 1/11
    assert tree.unfinished_nodes == {'BC', 'C'}


def test_best_nodes(tree: DecisionTree):
    assert tree.best_nodes == ['CA', 'A', 'BA', 'BB']


def test_to_explore_from_top(tree: DecisionTree):
    tree.nodes['BC'] = dict(),
    tree.nodes['BCA'] = 5
    assert tree.to_explore_from_top() == ['C', 'BC']
    assert tree.to_explore_from_best_solutions() == ['CB', 'CC', 'BCB', 'BCC']

    tree.nodes['BCA'] = 1
    assert tree.to_explore_from_top() == ['C', 'BC']
    assert tree.to_explore_from_best_solutions() == ['BCB', 'BCC', 'CB', 'CC', ]

    tree.nodes['BCA'] = 5
    tree.nodes['BA'] = 1
    assert tree.to_explore_from_top() == ['C', 'BC']
    assert tree.to_explore_from_best_solutions() == ['CB', 'CC', 'BCB', 'BCC']

    tree.nodes['BCA'] = 5
    tree.nodes['A'] = 1
    assert tree.to_explore_from_top() == ['C', 'BC']
    assert tree.to_explore_from_best_solutions() == []