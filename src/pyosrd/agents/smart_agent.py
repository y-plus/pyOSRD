import time
from typing_extensions import Self


from pyosrd import OSRD
from pyosrd.groot2 import Groot
from pyosrd.agents.base_agent import BaseAgent
from pyosrd.groot_decision_tree.groot_decision_tree import GrootDecisionTree
from pyosrd.groot2.actions.evaluate_action import evaluate_action
from pyosrd.utils import seconds_to_hour


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
            debug=self.debug,
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

        if self.debug:
            print('Calculating interlocking')
        groot = self.disrupted_groot.clone()
        stop = not groot.has_conflicts

        self.interlocking_node = ''
        while not stop:
            evaluate_action(groot, self.ref_groot, 'S')
            self.interlocking_node += 'S'
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
            debug=self.debug,
        )

    def _stop_criteria(self: Self) -> bool:
        if self.debug:
            print(
                f' Best delay: {seconds_to_hour(self.tree.best_solution)} ({self.tree.best_node}): '
                f'{self.tree.depth_completeness_ratio(self.tree.best_node):.1%}'
            )
            if self.tree.nodes[self.tree.best_node] == self.tree.nodes['']:
                print('No more extra delays')
        return (
            self.tree.depth_completeness_ratio(self.tree.best_node) == 1
            or
            self.tree.nodes[self.tree.best_node] == self.tree.nodes['']
        )

    def _calculate_dispatch(self: Self, debug: bool = False) -> Groot:
        
        if self.debug:
            print('Calculating dispatch')
            t0 = time.perf_counter()

        self.tree.best_solution = self.interlocking_score()
        self.tree.best_node = self.interlocking_node
        self.tree.best_groot = self.interlocking_groot


        if not self.disrupted_groot.has_conflicts():
                return self.disrupted_groot
        
        for wave in range(self.num_waves):

            # Exploration phase
            if self.debug:
                print(' Exploration phase')
            if wave == 0:
                nodes = [
                f'{a}{b}'
                for a in self.ACTIONS
                for b in self.ACTIONS
            ]
            else:
                nodes = self.tree.nodes_for_exploration()[:self.tree.num_proc]
            if self.debug:
                print(' ', nodes)
            self.tree.grow(nodes)
            if self._stop_criteria():
                break

            # Improvements phase
            nodes = self.tree.nodes_for_improvements()[:self.tree.num_proc]
            # nodes = self.tree.missing_nodes_at_depth(self.tree.depth(self.tree.best_node))
            if self.debug:
                print(' Improvements phase')
                print(' ', nodes)

            self.tree.grow(nodes)
            if self._stop_criteria():
                break

        if self.debug:
            if wave == self.num_waves-1:
                print('Max number of  waves reached')

            print(f'Time to calculate dispatch: {(time.perf_counter() - t0):.1f}s')
        
        return self.tree.best_groot
  