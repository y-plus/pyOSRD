from typing_extensions import Self

from pyosrd import OSRD
from pyosrd.groot2 import Groot
from pyosrd.agents.base_agent import BaseAgent
from pyosrd.groot_decision_tree.groot_decision_tree import GrootDecisionTree
from pyosrd.groot2.actions.evaluate_action import evaluate_action

class SmartAgent(BaseAgent):

    ACTIONS: list[str] = ['R', 'S', 'O']

    def __init__(
        self,
        name: str,
        sim: OSRD,
        debug: bool = False,
        num_waves: int = 5,
    ) -> None:
        super().__init__(name, sim, debug)
        self.num_waves = num_waves

        self.leave_station_asap = leave_station_asap

        self.tree = DecisionTree(
        self.tree = GrootDecisionTree(
            actions=self.ACTIONS,
            ref_groot=self.ref_groot,
            disrupted_groot=self.disrupted_groot,
            not_before=self.now,
            scorer=self._scorer,
        )
        

    @property
    def now(self: Self) -> float:
        now = 0
        for train in self.ref_groot.trains:
            for tvd, (t1, t2) in self.ref_groot.times[train].items():
                if self.disrupted_groot.times[train][tvd] != (t1, t2):
                    now = t1
                    break
        return now

    def _calculate_interlocking(self: Self, debug: bool) -> Groot:

        groot = self.disrupted_groot.clone()
        stop = not groot.has_conflicts

        while not stop:
            evaluate_action(groot, self.ref_groot, 'S')
            stop = not groot.has_conflicts()

        return groot

    def clear_cache(self):
        super().clear_cache()
        self.tree = GrootDecisionTree(
            actions=self.ACTIONS,
            ref_groot=self.ref_groot,
            disrupted_groot=self.disrupted_groot,
            not_before=self.now,
            scorer=self._scorer,
        )

    def _no_more_improvement(self: Self) -> bool:
        return self.tree.depth_completeness_ratio(self.tree.best_node)

    def _calculate_dispatch(self: Self, debug: bool = False) -> Groot:
            
        if not self.disrupted_groot.has_conflicts():
                return self.disrupted_groot

    def create_node_in_path(
        self: Self,
        node: str,
        path: DecisionTree,
        groot: Groot,
    ) -> bool:
        
        if node in self.tree.nodes and  self.tree.nodes[node] is None:
            return False
        
        if node in self.tree.nodes:
            path.nodes[node] = groot.set_times(self.tree.nodes[node])
            return True
        
        action = node[-1]
        original_times = self.evaluate_action(groot, action)
        path.nodes[node] = original_times

        if original_times is None:
            return False
 
        score = self._scorer(groot, self.ref_groot)

        if score > self.best_solution:
            path.nodes[node] = None
            groot.set_times(original_times)
            return False

        return True


# Those functions are not methods so that we can use them
# with multiprocessing

def path_to(
    agent: SmartAgent,
    node_to_reach: str
) -> tuple[DecisionTree, Groot]:
    
    path = DecisionTree()
    groot = agent.disrupted_groot.clone()

    for i, _ in enumerate(node_to_reach):
        ok = agent.create_node_in_path(node_to_reach[:i+1], path, groot)
        if not ok or not groot.has_conflicts():
            break
    return path, groot


def path_through(
    self: SmartAgent,
    node_to_include: str,
)-> tuple[DecisionTree, Groot]:

    path, groot = self.path_to(node_to_include)

    node = path.last_node
    stop = path.nodes[node] is None
    
    while not stop:
        if missing_actions := self.tree.missing_children_edges(node):
            action = missing_actions[0]
            new_node = f"{node}{action}"
            ok = self.create_node_in_path(new_node, path, groot)
            stop = not groot.has_conflicts()
            if ok:
                node = new_node
        else:
            node = path.parent(node)

    return path, groot
