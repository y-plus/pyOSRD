import copy
import multiprocessing

from typing_extensions import Self

import networkx as nx
import numpy as np

from pyosrd.utils import seconds_to_hour
from pyosrd.groot import Groot
from pyosrd.agents.groot_agent import GrootAgent
from pyosrd.groot.solve_conflict import solve_conflict
from pyosrd.groot.rerouting import reroute_train_to_avoid_zone


def evaluate_action(
    groot: Groot,
    ref_groot: Groot,
    action: int,
    not_before: float = 0,
    saved_times: list[dict[str, str | float]] | None = None
):
    match action:
        case 0:
            solve_conflict(
                groot,
                ref=ref_groot,
                switch_order=False,
                in_place=True,
                saved_times=saved_times,
                not_before=not_before
            )
        case 1:
            tr1, tr2, zone, _ = groot.earliest_conflict()
            try:
                train_to_reroute = ref_groot.trains_order_in_zone(tr1, tr2, zone)[1]
            except KeyError:
                train_to_reroute = groot.trains_order_in_zone(tr1, tr2, zone)[1]
            reroute_train_to_avoid_zone(
                groot,
                train_to_reroute,
                zone,
                in_place=True,
                saved_times=saved_times,
            )
        case 2:
            solve_conflict(
                groot,
                ref=ref_groot,
                switch_order=True, 
                in_place=True,
                saved_times=saved_times,
                not_before=not_before
            )
        case _:
            raise ValueError('Action is not valid')
    groot._times_zones = None


def path_to(self: Self, node_to_reach: str) -> tuple[nx.DiGraph, Groot]:

    groot = copy.deepcopy(self.disrupted_groot)
    groot._times_zones = None

    path = nx.DiGraph()
    path.add_node('_')

    actions = [int(a) for a in node_to_reach[1:]]
    node = '_'

    for _, action in enumerate(actions):
        
        evaluate_action(groot, self.ref_groot, action, not_before=self.now)
        new_node = f'{node}{action}'
        if self.debug:
            print(new_node)
        path.add_node(
            new_node,
            pheromone=(
                0 if not groot.times or not groot.has_conflicts()
                else 1
            )
        )
        path.add_edge(node, new_node)
        if not groot.times:
            break
        node = new_node
        if not groot.has_conflicts():
            break

    return path, groot


def quick_path(
    self: Self,
    node_to_include: str = '_',
) -> tuple[nx.DiGraph, Groot]:

    path, groot = path_to(self, node_to_include)

    if not groot.times or not groot.has_conflicts():
        return path, groot
    
    node = node_to_include
    
    done = not groot.has_conflicts()

    while not done:
        action = 1
        saved_times = []
        evaluate_action(groot, self.ref_groot, action=1, not_before=self.now, saved_times=saved_times)
        new_node = f'{node}{action}'
        if self.debug:
            print(new_node)
        path.add_node(
            new_node,
            pheromone=(
                0 if not groot.times or not groot.has_conflicts()
                else 1
            )
        )
        path.add_edge(node, new_node)
        if not groot.times:
            groot.set_times(saved_times[-1], in_place=True)
            action = 0
            evaluate_action(groot, self.ref_groot, action=0, not_before=self.now, saved_times=saved_times)
            new_node = f'{node}{action}'
            if self.debug:
                print(new_node)
            path.add_node(
                new_node,
                pheromone=(
                    0 if not groot.times or not groot.has_conflicts()
                    else 1
                )
            )
            path.add_edge(node, new_node)
        node = new_node
        done = not groot.has_conflicts()

    return path, groot


def interlocking_path(
    self: Self,
    node_to_include: str = '_',
) -> tuple[nx.DiGraph, Groot]:

    path, groot = path_to(self, node_to_include)

    if not groot.times or not groot.has_conflicts():
        return path, groot
    
    node = node_to_include
    
    done = not groot.has_conflicts()

    while not done:
        action = 0
        saved_times = []
        evaluate_action(groot, self.ref_groot, action=action, not_before=self.now, saved_times=saved_times)
        new_node = f'{node}{action}'
        if self.debug:
            print(new_node)
        path.add_node(
            new_node,
            pheromone=(
                0 if not groot.times or not groot.has_conflicts()
                else 1
            )
        )
        path.add_edge(node, new_node)
        node = new_node
        done = not groot.has_conflicts()

    return path, groot


def ant_path(
    self: Self,
    node_to_include: str = '_',
) -> tuple[nx.DiGraph, Groot]:

    path, groot = path_to(self, node_to_include)

    if not groot.times or not groot.has_conflicts():
        return path, groot
    
    node = node_to_include
    
    done = not groot.has_conflicts()
    saved_times = []
    while not done:

        children_pheromones = np.ones(self.NUM_ACTIONS)
        if node in self.tree:
            for n in self.tree.successors(node):
                idx = n[:-1]
                children_pheromones[idx] = self.tree.nodes[n]['pheromone']
        
        if sum(children_pheromones) == 0:
            node = node[:-1]
            if node == '_':
                return path, groot
            continue

        p = children_pheromones / sum(children_pheromones)
        action = np.random.choice(self.NUM_ACTIONS, 1, p=p).item()

        evaluate_action(
            groot,
            self.ref_groot,
            action=action,
            not_before=self.now,
            saved_times=saved_times,
        )
        new_node = f'{node}{action}'
        if self.debug:
            print(new_node)
        path.add_node(
            new_node,
            pheromone=(
                0 if not groot.times or not groot.has_conflicts()
                else 1
            )
        )
        path.add_edge(node, new_node)
        if not groot.times:
            times = saved_times.pop()
            groot.set_times(times, in_place=True)
        else:
            node = new_node
        done = not groot.has_conflicts()

    return path, groot


class ACOAgent(GrootAgent):

    NUM_ACTIONS = 3
    NUM_ANTS = multiprocessing.cpu_count()   
    NUM_ANT_WAVES = 10

    def _calculate_interlocking(self: Self, debug: bool) -> Groot:

        _, groot = interlocking_path(self, '_')
        return groot

    @property
    def now(self: Self) -> float:
        now = 0
        for train in self.ref_groot.trains:
            for tvd, (t1, t2) in self.ref_groot.times[train].items():
                if self.disrupted_groot.times[train][tvd] != (t1, t2):
                    now = t1
                    break
        return now

    def calculate_dispatch(self: Self, debug: bool = False) -> Groot:
        
        if not self.disrupted_groot.has_conflicts():
            return self.disrupted_groot
    


        self.tree = nx.DiGraph()
        self.tree.add_node('_', info={'done': False, 'valid': True}, pheromone=1)


        ultimate_solution = self._scorer(self.disrupted_groot, self.ref_groot)
        self.best_solution = float('inf')
        self.best_groot = None
        self.best_node = '_'

    # for wave in range(self.NUM_ANT_WAVES+1)

        # LAUNCH WAVE ON MULTIPROC

        # if wave == 0
        nodes = [
            f'_{a}{b}'
            for a in range(3)
            for b in range(3)
        ]

        with multiprocessing.Pool(initializer=np.random.seed) as pool:
            results = pool.starmap(quick_path, [(self, n) for n in nodes])
        
        # else
        # with multiprocessing.Pool(initializer=np.random.seed) as pool:
        #     results = pool.map(ant_path, [self] * self.NUM_ANTS)

        # DBG
        # results=[]
        # for n in nodes:
        #     results.append(
        #         ant_path(self)
        #     )
        # END BDG

        # COMPOSE TREE AND UPDATE BEST SOLUTION

        former_best_node = self.best_node
        for path, groot in results:
            self.tree = nx.compose(path, self.tree)
            if groot.times:
                print(
                    list(path.nodes)[-1],
                    seconds_to_hour(
                        self._scorer(groot, self.ref_groot)
                    )
                )
            if groot.times and self._scorer(groot, self.ref_groot) < self.best_solution:
                self.best_node = list(path.nodes)[-1]
                self.best_solution = self._scorer(groot, self.ref_groot)
                self.best_groot = groot
                self.best_path = path

        if self.best_solution==ultimate_solution:
            return self.best_groot
        
        # CALCULATE CONFIDENCE INDEX
        # = PROBABILITY TO NEVER FIND BETTER WITH LESS ACTIONS

        max_depth = len(self.best_node) - 1
        explored_nodes = [
            n for n in self.tree.nodes
            if len(n) -1 <= max_depth
        ]
        num_explored_nodes = len(explored_nodes)

        num_unexplored_nodes = 0
        for n in explored_nodes:
            depth = len(n) -1
            missing_children = (
                self.NUM_ACTIONS - len(list(self.tree.successors(n)))
                if self.tree.nodes[n]['pheromone'] > 0
                else 0
            )
            num_unexplored_nodes += missing_children * (
                (1 - self.NUM_ACTIONS**(max_depth - depth + 1))
                / (1 - self.NUM_ACTIONS)
                - 1
            )

        confidence = num_explored_nodes / (num_unexplored_nodes + num_explored_nodes)

        if self.debug:
            print(f"Best solution so far: {seconds_to_hour(self.best_solution)} with a confidence of {confidence: .1%}")

        # TODO: STOP CRITERION ON CONFIDENCE ???
        ...

        # UPDATE PHEROMONES FOR BEST SOLUTION

        if self.debug:
            print('Update pheromones for best solution (if changed)')
        if former_best_node != self.best_node:
            for n in self.best_path.nodes:
                self.tree.nodes[n]['pheromone'] += 1

        # PRUNE ALREADY EXPLORED BRANCHES

        if self.debug:
            print('Prune branches by setting pheromone to 0 when all children are dead ends')
        for n in sorted(self.tree.nodes, key=len):
            if [self.tree.nodes[ch] for ch in self.tree.successors(n)] == [0] * self.NUM_ACTIONS:
                self.tree.nodes[n[:-1]]['pheromone'] == 0

    # end wave

        if self.debug:
            self._draw_tree()

        return self.best_groot


    def _draw_tree(self: Self):
        pos = nx.spring_layout(self.tree)
        for layer, nodes in enumerate(nx.topological_generations(self.tree)):
            # `multipartite_layout` expects the layer as a node attribute, so add the
            # numeric layer value as a node attribute
            for node in nodes:
                self.tree.nodes[node]["layer"] = layer

        # Compute the multipartite_layout using the "layer" node attribute
        pos = nx.multipartite_layout(self.tree, subset_key="layer")
        # nx.draw(self.tree, pos)
        nx.draw_networkx_nodes(
            self.tree,
            pos,
            node_size=200,
            node_color='lightgrey'
        )
        nx.draw_networkx_edges(
            self.tree,
            pos,
            edge_color='lightgrey'
        )
        valids = nx.subgraph(self.tree, [n for n in self.tree.nodes if 'info' in self.tree.nodes[n] and self.tree.nodes[n]['info']['valid']])
        nx.draw_networkx(
            valids,
            pos,
            font_size=6,
            node_size=200,
            node_color='lightgreen',
            with_labels=False,
            edge_color="lightgreen"

        )
        nx.draw_networkx_labels(
            self.tree,
            pos,
            font_size=6,
            labels={n: str(n)[-1] for n in self.tree.nodes},
            font_color='grey'
        )
        sp = nx.shortest_path(self.tree, '_', self.best_node)
        nx.draw_networkx(
            nx.path_graph(sp),
            pos,
            font_size=6,
            node_size=200,
            node_color='green',
            with_labels=False,
            edge_color="green",
        )
        nx.draw_networkx_labels(
            nx.path_graph(sp),
            pos,
            font_size=6,
            labels={n: str(n)[-1] for n in nx.path_graph(sp).nodes},
            font_color='white'
        )
