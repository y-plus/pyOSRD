import copy

from typing_extensions import Self

import networkx as nx

from pyosrd.utils import seconds_to_hour
from pyosrd.groot import Groot
from pyosrd.agents.groot_agent import GrootAgent
from pyosrd.groot.dispatching import evaluate_action


class GDTAgent(GrootAgent):

    NUM_ACTIONS = 5

    def calculate_dispatch(self: Self) -> Groot:
        
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
            best_node = 1

        while nodes_to_explore:
            node = nodes_to_explore[-1]
            all_actions_evaluated = \
                len(list(tree.successors(node))) == self.NUM_ACTIONS
            not_valid = not tree.nodes[node]['valid']
            done_and_valid = tree.nodes[node]['done'] and tree.nodes[node]['valid']

            not_better = (
                tree.nodes[node]['reward'] <= tree.nodes[best_node]['reward']
            ) if node > 1 else False

            if (
                node > 1 and
                done_and_valid
                and tree.nodes[node]['reward'] > tree.nodes[best_node]['reward']
            ):
                best_node = node

            if node > 1 and len(list(tree.successors(1))) == 1:
                best_node = node

            if all_actions_evaluated or not_valid or done_and_valid or not_better:
                nodes_to_explore.pop()
            else:
                new_node = tree.number_of_nodes()
                action = len(list(tree.successors(node)))

                groot, info = evaluate_action(
                    tree.nodes[node]['state'],
                    a=action,
                    ref=self.ref_groot,
                    scorer=self._scorer
                )
                tree.add_node(
                    new_node,
                    done=info['done'],
                    valid=info['valid'],
                    reward=-info['score'],
                    state=groot,
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
            

        return tree.nodes[best_node]['state']

