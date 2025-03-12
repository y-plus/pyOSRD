import copy
import multiprocessing

from typing_extensions import Self

import networkx as nx
import numpy as np

from pyosrd.utils import seconds_to_hour
from pyosrd.groot import Groot
from pyosrd.agents.groot_agent import GrootAgent
from pyosrd.groot.dispatching import evaluate_action


def random_path(self: Self) -> nx.DiGraph:

    path = nx.DiGraph()
    node = 0
    path.add_node(node)
    groot = self.disrupted_groot
    stop_ant = False

    while not stop_ant:
        pheromons = np.ones(self.NUM_ACTIONS)
        if node in self.tree:
            for n in self.tree.successors(node):
                idx = self.tree.get_edge_data(node,n)['action']
                pheromons[idx] = self.tree.get_edge_data(node,n)['pheromone']
        if sum(pheromons) != 0:
            p = pheromons / sum(pheromons)
        else:
            return path
        while sum(p) > 0:
            action = np.random.choice(self.NUM_ACTIONS, 1, p=p).item()
            groot, info = evaluate_action(
                groot,
                a = action,
                ref=self.ref_groot,
                now=self.now
            )
            stop_ant = (
                info['done']
                or
                info['score'] > self.best_solution
            )
            new_node = f"{node}{action}"
            path.add_node(
                new_node,
                delay=info['score'],
                info=info,
            )
            path.add_edge(
                node,
                new_node,
                action = action,
                pheromone = 0 if stop_ant else 1,
            )

            if self.debug:
                print(node,'->', new_node)

            if info['valid']:
                break
            p[action] = 0
            
            if sum(p) == 0:
                stop_ant = True
            else:
                p /= sum(p)

        node = new_node

    return path

class ACAgent(GrootAgent):

    NUM_ACTIONS = 5
    NUM_ANTS = multiprocessing.cpu_count()   
    NUM_WAVES = 10

    def calculate_dispatch(self: Self, debug: bool = False) -> Groot:
        
        if not self.disrupted_groot.has_conflicts():
            return self.disrupted_groot
    
        self.now = 0
        for train in self.ref_groot.trains:
            for tvd, (t1, t2) in self.ref_groot.times[train].items():
                if self.disrupted_groot.times[train][tvd] != (t1, t2):
                    self.now = t1
                    break
         
        groot =  copy.deepcopy(self.disrupted_groot)


        self.tree = nx.DiGraph()
        self.tree.add_node(0, info={'done': False, 'valid': True})
        node = 0
        done = False
        while not done:
            
            action = 2
            new_groot, info = evaluate_action(
                groot,
                a=action,
                ref=self.ref_groot,
                scorer=self._scorer
            )
            new_node = f"{node}{action}"
            self.tree.add_node(
                new_node,
                delay=info['score'],
                info=info,
            )
            self.tree.add_edge(
                node,
                new_node,
                action = action,
                pheromone = 0 if (not info['valid']) or info['done'] else 1
            )
            if self.debug:
                print(node,'->', new_node)
            
            if not info['valid']:
                action = 0
                new_groot, info = evaluate_action(
                    groot,
                    a=action,
                    ref=self.ref_groot,
                    scorer=self._scorer
                )
                new_node = f"{node}{action}"
                self.tree.add_node(
                    new_node,
                    delay=info['score'],
                    info=info,
                )
                self.tree.add_edge(
                    node,
                    new_node,
                    action = action,
                    pheromone =0 if (not info['valid']) or info['done'] else 1
                )
                if self.debug:
                    print(node,'->', new_node)
                
            if not info['valid']:
                action = 1
                new_groot, info = evaluate_action(
                    groot,
                    a=action,
                    ref=self.ref_groot,
                    scorer=self._scorer
                )
                new_node = f"{node}{action}"
                self.tree.add_node(
                    new_node,
                    delay=info['score'],
                    info=info,
                )
                self.tree.add_edge(
                    node,
                    new_node,
                    action = action,
                    pheromone = 0 if (not info['valid']) or info['done'] else 1,
                )
                # 
                if self.debug:
                    print(node,'->', new_node)
            if not info['valid']:
                raise ValueError('No interlocking solution found')
            done = info['done']       
            groot = new_groot
            node = new_node
        self.best_solution = info['score']
        self.best_node = node

        # update pheromones for best node
        sp = nx.shortest_path(self.tree, 0, self.best_node)
        for edge in nx.path_graph(sp).edges():
            if self.tree.edges[edge[0], edge[1]]['pheromone'] > 0:
                self.tree.edges[edge[0], edge[1]]['pheromone'] += 1

        print(
            '*',
            len(self.tree),
            self.best_node,
            seconds_to_hour(self.best_solution),
        )
        
        for _ in range(self.NUM_WAVES):
            with multiprocessing.Pool(initializer=np.random.seed) as pool:
                paths = pool.map(random_path, [self for _ in range(self.NUM_ANTS)])

            best_node = self.best_node
            for path in paths:
                self.tree = nx.compose(path, self.tree)
                last_node = list(path.nodes)[-1]
                done = nx.get_node_attributes(path, 'info')[last_node]['done'] 
                valid = nx.get_node_attributes(path, 'info')[last_node]['valid']
                if done and valid:
                    if (delay := nx.get_node_attributes(path, 'delay')[last_node]) < self.best_solution:
                        best_solution = delay
                        best_node = last_node
                else: # retro-pruning
                    for e in list(path.edges)[::-1]:
                        # print(e, end='')
                        successors_ph = [
                            self.tree.edges[e[1], n]['pheromone']for n in self.tree.successors(e[1])
                        ]
                        if successors_ph == [0] * self.NUM_ACTIONS:
                            self.tree.edges[edge[0], edge[1]]['pheromone'] = 0
                            print(e)
                        # if (
                        #     len(self.tree.successors(e[1])==self.NUM_ACTIONS)
                        #     and all()
                        # ):                    
            del(paths)

            for n in self.tree.nodes:
                successors_ph = [
                        self.tree.edges[e[1], n]['pheromone']for n in self.tree.successors(e[1])
                    ]
                
            # update pheromones ?? (evaporation)

            # update pheromones for best node
            if best_node != self.best_node:
                self.best_solution, self.best_node = best_solution, best_node
                sp = nx.shortest_path(self.tree, 0, self.best_node)
                for edge in nx.path_graph(sp).edges():
                    if self.tree.edges[edge[0], edge[1]]['pheromone'] > 0:
                        self.tree.edges[edge[0], edge[1]]['pheromone'] += 1

            print(
                '*',
                len(self.tree),
                self.best_node,
                seconds_to_hour(self.best_solution),
            )
        
        # if self.debug:
            # self._draw_tree()
        
        return groot

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
        sp = nx.shortest_path(self.tree, 0, self.best_node)
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
