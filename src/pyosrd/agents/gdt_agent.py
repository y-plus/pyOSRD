import copy
import math

from typing_extensions import Self

import networkx as nx

from pyosrd.utils import seconds_to_hour
from pyosrd.groot import Groot
from pyosrd.agents.groot_agent import GrootAgent
from pyosrd.groot.dispatching import evaluate_action


class GDTAgent(GrootAgent):

    NUM_ACTIONS = 5
    MAX_NODES = float('inf')
    DELAY_TOL = 0 #240

    @property
    def n_interlocking_actions(self: Self) -> int:
        if not hasattr(self, '_n_interlocking_actions'):
            _ = self.interlocking_groot
            self._n_interlocking_actions = len(self.interlocking_actions)
        return self._n_interlocking_actions

    def calculate_dispatch(self: Self, debug: bool = False) -> Groot:
        
        now = 0
        for train in self.ref_groot.trains:
            for tvd, (t1, t2) in self.ref_groot.times[train].items():
                if self.disrupted_groot.times[train][tvd] != (t1, t2):
                    now = t1
                    break
                
        current_state = copy.deepcopy(self.disrupted_groot)
        tree = nx.DiGraph()
        tree.add_node(
            0,
            state=current_state,
            reward=-self._scorer(current_state, self.ref_groot),
            done=False,
            valid=True
        )

        if not current_state.has_conflicts():
            nodes_to_explore = []
            best_node = 0
        else:
            nodes_to_explore = [0]
            best_node = None

        while nodes_to_explore:
            node = nodes_to_explore[-1]

            all_actions_evaluated = \
                len(list(tree.successors(node))) == self.NUM_ACTIONS
            
            unvalid = not tree.nodes[node]['valid']
            
            done_and_valid = tree.nodes[node]['done'] and tree.nodes[node]['valid']

            not_better = (
                tree.nodes[node]['reward'] - tree.nodes[best_node]['reward'] <= self.DELAY_TOL
            ) if best_node else False

            depth = len(nx.shortest_path(tree, 0, node))
            max_depth = self.n_interlocking_actions
            max_depth_reached = (depth > max_depth)

            if best_node is None and done_and_valid:
                best_node = node
            if (
                node > 1 and
                done_and_valid
                and tree.nodes[node]['reward'] > tree.nodes[best_node]['reward']
            ):
                best_node = node

            if all_actions_evaluated or unvalid or done_and_valid or not_better or max_depth_reached:
                nodes_to_explore.pop()
            elif tree.number_of_nodes() > self.MAX_NODES:
                nodes_to_explore = []
            else:
                new_node = tree.number_of_nodes()
                action = len(list(tree.successors(node)))
                groot, info = evaluate_action(
                    tree.nodes[node]['state'],
                    a=action,
                    ref=self.ref_groot,
                    scorer=self._scorer,
                    now=now,
                )
                if debug:
                    done=info['done']
                    valid=info['valid']
                    best_score = (
                        -tree.nodes[best_node]['reward']
                        if best_node else float('inf')
                    )
                    best_delay = seconds_to_hour(
                        best_score
                    )  if math.isfinite(best_score) else ''
                    delay = seconds_to_hour(
                        info["score"]
                    )  if valid else 'not valid'
                    print(
                        f"{node}-({action=})->{new_node}",
                        f"{delay=}",
                        f"{best_delay=}",
                        f"{done=}",
                        f"depth={len(nx.shortest_path(tree, 0, node))+1}",
                        sep = ' | '
                    )
                tree.add_node(
                    new_node,
                    done=info['done'],
                    valid=info['valid'],
                    reward=-info['score'] if info['valid'] else -float('inf'),
                    state=groot if info['valid'] else None,
                )
                tree.add_edge(node, new_node, info=info)
                nodes_to_explore.append(new_node)

        sp = nx.shortest_path(tree, 0, best_node)
        pg = nx.path_graph(sp)  # does not pass edges attributes

        if tree.number_of_nodes() == 1:
            self.actions = []
        else:
            self.actions = [
                tree.edges[edge[0], edge[1]]['info']
                for edge in pg.edges()
            ]

        for i, action in enumerate(self.actions):
            if i > 0:
                added_score = action['score'] - self.actions[i-1]['score']
            else:
                added_score = action['score'] + tree.nodes[0]['reward']
            added_delay = seconds_to_hour(added_score)
            self.actions[i] = {
                **action,
                'added_score': added_score,
                'delay': seconds_to_hour(action['score']),
                'added_delay': added_delay
            }
        
        best_groot = tree.nodes[best_node]['state']
        del(tree)
        return best_groot
