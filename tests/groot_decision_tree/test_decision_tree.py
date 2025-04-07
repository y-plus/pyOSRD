import pytest
from pyosrd.groot_decision_tree.decision_tree import DecisionTree


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
            'BB': float('inf'),
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


def test_missing_siblings_edges(tree: DecisionTree):
    assert tree.missing_siblings_edges('') is None
    assert tree.missing_siblings_edges('A') == []
    assert tree.missing_siblings_edges('BA') == ['C']
    assert tree.missing_siblings_edges('CA') == ['B', 'C']


def test_missing_children(tree: DecisionTree):
    assert tree.missing_children('') == []
    assert tree.missing_children('A') == ['AA', 'AB', 'AC']
    assert tree.missing_children('B') == ['BC']
    assert tree.missing_children('C') == ['CB', 'CC']


def test_missing_siblings(tree: DecisionTree):
    assert tree.missing_siblings('') is None
    assert tree.missing_siblings('A') == []
    assert tree.missing_siblings('BA') == ['BC']
    assert tree.missing_siblings('CA') == ['CB', 'CC']


def test_nodes_explored_unexplored_or_solution_(tree: DecisionTree):
    assert tree.solution_nodes == {'A', 'BA', 'BB', 'CA'}
    assert tree.unexplored_nodes == {'B', 'C'}
    assert tree.explored_nodes == {'A', 'BA', 'BB', 'CA'}


def test_nodes_explored_unexplored_or_solution_2(tree: DecisionTree):
    tree.nodes['BC'] = dict()
    assert tree.explored_nodes == {'A', 'B', 'BA', 'BB', 'CA'}
    assert tree.unexplored_nodes == {'C', 'BC'}
    assert tree.solution_nodes == {'A', 'BA', 'BB', 'CA'}


def test_nodes_explored_unexplored_or_solution_3(tree: DecisionTree):
    tree.nodes['BC'] = 5
    assert tree.explored_nodes == {'A', 'B', 'BA', 'BB', 'CA', 'BC'}
    assert tree.unexplored_nodes == {'C'}
    assert tree.solution_nodes == {'A', 'BA', 'BB', 'BC', 'CA'}


def test_combine(tree: DecisionTree):
    paths = [
        DecisionTree(nodes={'': 1, 'B': dict(), 'BA': 5}),
        DecisionTree(nodes={'': 1, 'A': 5}),
        DecisionTree(nodes={'': 1, 'B': dict(), 'BB': float('inf')}),
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
        DecisionTree(nodes={'': 1, 'B': dict(), 'BB': float('inf')}),
        DecisionTree(nodes={'': 1, 'C': dict(), 'CA': 3}),
        DecisionTree(nodes={'': 1, 'C': dict(), 'CA': 3}),
    ]
    new_tree = DecisionTree()
    for path in paths:
        new_tree.combine(path)
    assert new_tree.nodes == tree.nodes


def test_best_solution_confidence(tree: DecisionTree):
    assert tree.depth_completeness_ratio('A') == 1
    assert tree.depth_completeness_ratio('BA') == 3/6

    tree.nodes['BC'] =  5
    assert tree.depth_completeness_ratio('BA') == 4/6

    tree.nodes['BC'] =  dict()
    tree.nodes['BCA'] =  5
    assert tree.depth_completeness_ratio('BA') == 4/6
    assert tree.depth_completeness_ratio('BCA') == 1/9
    assert tree.unexplored_nodes == {'BC', 'C'}

    tree.nodes.pop('CA')
    tree.nodes.pop('C')
    assert tree.depth_completeness_ratio('A') == 2/(2 + 1)
    assert tree.depth_completeness_ratio('BA') == 3/(3 + 3)
    assert tree.depth_completeness_ratio('BCA') == 1/(1 + 11)

def test_best_nodes(tree: DecisionTree):
    assert tree.best_nodes == ['CA', 'A', 'BA']


def test_nodes_for_exploration(tree: DecisionTree):
    tree.nodes['BC'] = dict(),
    tree.nodes['BCA'] = 5
    assert tree.nodes_for_exploration() == ['C', 'BC']
    
    tree.nodes['BCA'] = 1
    assert tree.nodes_for_exploration() == ['C', 'BC']
    
    tree.nodes['BCA'] = 5
    tree.nodes['BA'] = 1
    assert tree.nodes_for_exploration() == ['C', 'BC']
    
    tree.nodes['BCA'] = 5
    tree.nodes['A'] = 1
    assert tree.nodes_for_exploration() == ['C', 'BC']
    
def test_nodes_for_improvements(tree: DecisionTree):
    tree.nodes['BC'] = dict(),
    tree.nodes['BCA'] = 5
    assert tree.nodes_for_improvements() == ['CB', 'CC', 'BCB', 'BCC']

    tree.nodes['BCA'] = 1
    assert tree.nodes_for_improvements() == ['BCB', 'BCC', 'CB', 'CC', ]

    tree.nodes['BCA'] = 5
    tree.nodes['BA'] = 1
    assert tree.nodes_for_improvements() == ['CB', 'CC', 'BCB', 'BCC']

    tree.nodes['BCA'] = 5
    tree.nodes['A'] = 1
    assert tree.nodes_for_improvements() == []
