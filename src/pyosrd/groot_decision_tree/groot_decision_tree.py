
import multiprocessing

from typing import Callable
from typing_extensions import Self

import numpy as np

from pyosrd.groot2 import Groot
from pyosrd.groot2.actions.evaluate_action import evaluate_action

from .decision_tree import DecisionTree, Action, NodeIndex
from pyosrd.groot.objectives import sum_delays_at_end


class GrootDecisionTree(DecisionTree):
    
    def __init__(
        self,
        actions: list[Action],
        ref_groot: Groot,
        disrupted_groot: Groot,
        not_before: float = 0,
        scorer: Callable[[Groot, Groot], float] = sum_delays_at_end
    ):
        super().__init__(actions)
        self.ref_groot = ref_groot
        self.disrupted_groot = disrupted_groot
        self.not_before = not_before
        self._scorer = scorer
        self.best_solution = float('inf')
        self.best_groot = None
        self.best_node = ''
        self.num_proc = multiprocessing.cpu_count()

        self.nodes[''] = self._scorer(self.disrupted_groot, self.ref_groot)
        self.current_groot = self.disrupted_groot.clone()


    def create_node_in_branch(
        self: Self,
        node: str,
        branch: Self,
    ) -> bool:
        
        if node in self.nodes and self.is_explored(node):
            return False
        
        if node in self.nodes:
            branch.nodes[node] = branch.current_groot.set_times(self.nodes[node])
            return True
        
        if node[:-1] not in branch.nodes:
            raise ValueError(f"Can't create {node} as node {node[:-1]} does not exist in branch")

        action = node[-1]

        if action not in self.actions:
            raise ValueError(f"Unknown action {action}")
    
        original_times = evaluate_action(
            branch.current_groot,
            self.ref_groot,
            action,
            self.not_before
        )
        branch.nodes[node] = original_times

        if original_times is None:
            branch.nodes[node] = float('inf')
            return False
 
        score = self._scorer(branch.current_groot, self.ref_groot)
        
        if not branch.current_groot.has_conflicts():
            branch.nodes[node] = score

        if score > self.best_solution:    
            branch.current_groot.set_times(original_times)
            return False

        return True

    def grow_branches(self: Self, nodes: list[NodeIndex]) -> list[tuple[DecisionTree, Groot]]:
        with multiprocessing.Pool(initializer=np.random.seed) as pool:
            results = pool.starmap(
                grow_branch_through,
                [(self, node) for node in nodes]
            )
        return results

    def grow(self: Self, nodes: list[NodeIndex]) -> Groot:
        new_branches: list[Self] = self.grow_branches(nodes)
        for branch in new_branches:
            self.combine(branch)
            last_node = branch.last_node
            if self.is_solution(last_node) and self.nodes[last_node] < self.best_solution:
                self.best_groot = branch.current_groot
                self.best_node = last_node
                self.best_solution = branch.nodes[last_node]
    

# Those functions are not methods so that we can use them
# with multiprocessing

def grow_branch_to(
    tree: GrootDecisionTree,
    node_to_reach: str
) -> GrootDecisionTree:
    
    branch = GrootDecisionTree(
        tree.actions,
        tree.ref_groot,
        tree.disrupted_groot
    )

    for i, _ in enumerate(node_to_reach):
        ok = tree.create_node_in_branch(node_to_reach[:i+1], branch)
        if not ok or not branch.current_groot.has_conflicts():
            break
    return branch


def grow_branch_through(
    tree: GrootDecisionTree,
    node_to_include: str,
)-> GrootDecisionTree:

    branch = grow_branch_to(tree, node_to_include)

    if branch.nodes[branch.last_node] == float('inf'):
        return branch
    
    node = branch.last_node
    stop = not branch.current_groot.has_conflicts()
    missing_actions = tree.missing_children_edges(node)

    while not stop:
        if missing_actions:
            new_node = f"{node}{missing_actions[0]}"
            ok = tree.create_node_in_branch(new_node, branch)
            stop = not branch.current_groot.has_conflicts()
            if ok:
                node = new_node
            else:
                missing_actions = missing_actions[1:]
        elif branch.is_root(node):
            break
        else:
            node = branch.parent(node)
            missing_actions = tree.missing_children_edges(node)
            stop = not branch.current_groot.has_conflicts()
            if tree.is_root(node):
                stop = True

    return branch