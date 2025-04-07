import multiprocessing

import pytest

from pyosrd import OSRD
from pyosrd.groot2 import from_sim
from pyosrd.groot_decision_tree.groot_decision_tree import (
    GrootDecisionTree,
    grow_branch_through,
    grow_branch_to
)


@pytest.fixture(scope='session')
def tree() -> GrootDecisionTree:
    sim = OSRD(
        dir='tmp',
        simulation="c1yy3yy1_3trains"
    )
    sim.add_delay(0, 120, 120)
    ref_groot = from_sim(sim)
    disrupted_groot = from_sim(sim.delayed())
    return GrootDecisionTree(
        actions=['R', 'S', 'O'],
        ref_groot=ref_groot,
        disrupted_groot=disrupted_groot,
    )

@pytest.fixture()
def branch(tree) -> GrootDecisionTree:
    return GrootDecisionTree(
        tree.actions,
        tree.ref_groot,
        tree.disrupted_groot
    )


class TestGrootDecisionTree:

    def test_init(self, tree: GrootDecisionTree):
        assert tree.best_solution == float('inf')
        assert tree.best_groot is None
        assert tree.best_node == ''
        assert tree.num_proc == multiprocessing.cpu_count()
        assert tree.current_groot == tree.disrupted_groot

    def test_create_node_in_branch(
        self,
        tree: GrootDecisionTree,
        branch: GrootDecisionTree
    ):

        assert branch.current_groot.has_conflicts()
        
        tree.create_node_in_branch('S', branch)
        assert branch.current_groot.has_conflicts

        tree.create_node_in_branch('SS', branch)
        assert not branch.current_groot.has_conflicts()

    def test_create_node_in_branch_error_no_parent(
        self,
        tree: GrootDecisionTree,
        branch: GrootDecisionTree
    ):
        error_msg = "Can't create SS as node S does not exist in branch"
        with pytest.raises(ValueError, match=error_msg):
            tree.create_node_in_branch('SS', branch)
        
    def test_create_node_in_branch_unknown_action(
        self,
        tree: GrootDecisionTree,
        branch: GrootDecisionTree
    ):
        with pytest.raises(ValueError, match='Unknown action _'):
            tree.create_node_in_branch('_', branch)

    @pytest.mark.parametrize("action", ['O'])
    def test_create_node_in_branch_unvalid_action(
        self,
        tree: GrootDecisionTree,
        branch: GrootDecisionTree,
        action
    ):
        ok = tree.create_node_in_branch(action, branch)
        assert not ok
        assert branch.nodes[action] == float('inf')

    def test_grow_branch_to(self, tree: GrootDecisionTree):
        branch = grow_branch_to(tree, 'S')
        assert set(branch.nodes.keys()) == {'', 'S'}
        
        branch = grow_branch_to(tree, 'SS')
        assert set(branch.nodes.keys()) == {'', 'S', 'SS'}
        
        branch = grow_branch_to(tree, 'SSS')
        assert set(branch.nodes.keys()) == {'', 'S', 'SS'}
        
        branch = grow_branch_to(tree, 'R')
        assert set(branch.nodes.keys()) == {'', 'R'}
        
        branch = grow_branch_to(tree, 'RS')
        assert set(branch.nodes.keys()) == {'', 'R', 'RS'}

    def test_grow_branch_through(self, tree: GrootDecisionTree):
        
        branch = grow_branch_through(tree, 'R')
        assert set(branch.nodes.keys()) == {'', 'R', 'RR', 'RS'}
        
        branch = grow_branch_through(tree, 'RS')
        assert set(branch.nodes.keys()) == {'', 'R', 'RS'}

        branch = grow_branch_through(tree, 'S')
        assert set(branch.nodes.keys()) == {'', 'S', 'SR', 'SS'}
        
        branch = grow_branch_through(tree, 'SS')
        assert set(branch.nodes.keys()) == {'', 'S', 'SS'}
        
        branch = grow_branch_through(tree, 'SSS')
        assert set(branch.nodes.keys()) == {'', 'S', 'SS'}

    def test_grow_branches(self, tree: GrootDecisionTree):
        branches = tree.grow_branches(['S', 'R'])
        assert list(branches[0].nodes.keys()) == ['', 'S', 'SR', 'SS']
        assert list(branches[1].nodes.keys()) == ['', 'R', 'RR', 'RS']

    def test_grow(self, tree: GrootDecisionTree):
        tree.grow(['S', 'R'])
        assert set(tree.nodes.keys()) == {'', 'R', 'RR', 'RS', 'S', 'SR', 'SS'}
        assert tree.solution_nodes == {'RR', 'RS', 'SS', 'SR'}
    
        assert tree.best_nodes == ['RS', 'SS']
        
        assert tree.nodes_for_improvements() == ['RO', 'SO']
        assert set(tree.nodes_for_exploration()) == {'', 'R', 'S'}
        
        assert tree.best_node == 'RS'
        assert tree.depth_completeness_ratio('RS') == 4 / 9