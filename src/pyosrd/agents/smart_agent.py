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
        
        for wave in range(self.num_waves):

            # Exploration phase
            if wave == 0:
                nodes = [
                f'{a}{b}'
                for a in self.ACTIONS
                for b in self.ACTIONS
            ]
            else:
                nodes = self.tree.nodes_for_exploration()
            
            self.tree.grow(nodes)
            if self._no_more_improvement():
                break

            # Improvements phase
            nodes = self.tree.nodes_for_improvements()
            self.tree.grow(nodes)
            if self._no_more_improvement():
                break

            
        return self.tree.best_groot
  