import multiprocessing
from typing_extensions import Self

from pyosrd import OSRD
from pyosrd.groot2 import Groot, GrootTimes
from pyosrd.groot2.actions import reroute_train_to_avoid_zone, solve_conflict

from pyosrd.agents.base_agent import BaseAgent
from pyosrd.groot_decision_tree.decision_tree import DecisionTree

class SmartAgent(BaseAgent):

    ACTIONS: list[str] = ['R', 'S', 'O']
    NUM_ACTIONS: int = len(ACTIONS)
    NUM_PROC: int = multiprocessing.cpu_count()

    def __init__(
        self,
        name: str,
        sim: OSRD,
        debug: bool = False,
        num_waves: int = 5,
        leave_station_asap: bool = True
    ) -> None:
        super().__init__(name, sim, debug)
        self.num_waves = num_waves

        self.leave_station_asap = leave_station_asap

        self.tree = DecisionTree(
            actions=self.ACTIONS,
            nodes={'': dict()},
        )
        self.solutions: dict[str, float] = dict()
        self.ultimate_solution = self._scorer(self.disrupted_groot, self.ref_groot)
        self.best_solution = float('inf')
        self.best_groot = None
        self.best_node = ''
        self.scores = dict()


    @property
    def now(self: Self) -> float:
        now = 0
        for train in self.ref_groot.trains:
            for tvd, (t1, t2) in self.ref_groot.times[train].items():
                if self.disrupted_groot.times[train][tvd] != (t1, t2):
                    now = t1
                    break
        return now

    def evaluate_action(
        self: Self,
        groot: Groot,
        action: str,
    ) -> GrootTimes | None:
        match action:
            case 'R':
                tr1, tr2, zone, _ = groot.earliest_conflict()
                try:
                    train_to_reroute = self.ref_groot.trains_order_in_zone(tr1, tr2, zone)[1]
                except KeyError:
                    train_to_reroute = groot.trains_order_in_zone(tr1, tr2, zone)[1]

                original_times = reroute_train_to_avoid_zone(
                    groot,
                    train_to_reroute,
                    zone,
                )
            case 'S':
                original_times = solve_conflict(
                    groot,
                    ref=self.ref_groot,
                    reorder=False,
                    not_before=self.now
                )
            case 'O':
                original_times = solve_conflict(
                    groot,
                    ref=self.ref_groot,
                    reorder=True,
                    in_place=True,
                    not_before=self.now
                )
        return original_times

    def _calculate_interlocking(self: Self, debug: bool) -> Groot:

        groot = self.disrupted_groot.clone()
        stop = not groot.has_conflicts

        while not stop:
            self.evaluate_action(groot, 'S')

        return groot

    def calculate_dispatch(self: Self, debug: bool = False) -> Groot:

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
