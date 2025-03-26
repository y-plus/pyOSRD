from dataclasses import dataclass, field
from typing import Any
from typing_extensions import Self

NodeIndex = str
Action = str


@dataclass
class DecisionTree:

    actions: list[Action] = field(default_factory=list)
    nodes: dict[NodeIndex, Any | None] = field(default_factory=lambda: {"": None})

    @property
    def num_actions(self: Self) -> int:
        return len(self.actions)

    def __len__(self: Self) -> int:
        return len(self.nodes)

    def height(self: Self) -> int:
        return len(max(self.nodes, key=len))
    
    def depth(self: Self, node: NodeIndex) -> int:
        return len(node)
    
    @property
    def last_node(self: Self) -> NodeIndex:
        return max(self.nodes, key=len)

    def parent(self: Self, node:NodeIndex) -> NodeIndex:
        if self.depth(node) > 0:
            return node[:-1]
    
    def children(self: Self, node: NodeIndex) -> set[NodeIndex]:
        return set(
            n for n in self.nodes
            if n and n[:-1] == node
        )
    
    def num_children(self: Self, node: NodeIndex) -> int:
        return len(self.children(node))
    
    def missing_children_edges(self: Self, node: NodeIndex) -> list[Action]:
        return [
            a for a in self.actions
            if f"{node}{a}" not in self.children(node)
        ]
    
    def missing_brothers_edges(self: Self, node: NodeIndex) -> list[Action]:
        if node:
            return self.missing_children_edges(self.parent(node))

    def missing_children(self: Self, node: NodeIndex) -> list[Action]:
        return [
            f"{node}{a}" for a in self.actions
            if f"{node}{a}" not in self.children(node)
        ]
    
    def missing_brothers(self: Self, node: NodeIndex) -> list[Action]:
        if node:
            return self.missing_children(self.parent(node))
    
    def max_num_sucessors(self: Self, node: NodeIndex, depth: int) -> int:
        N = self.num_actions
        return int(
            ( 1 - N ** (depth - self.depth(node) + 1))
            / (1-len(self.actions)) - 1
        )
    
    def num_successors_on_missing_children_branches(
        self: Self,
        node: NodeIndex,
        depth: int
    ) -> int:
        return ( 
            self.max_num_sucessors(node, depth) 
            * len(self.missing_children_edges(node))
            / self.num_actions
        )
    
    @property
    def unfinished_nodes(self: Self) -> set[NodeIndex]:
        return set(
            node for node, value in self.nodes.items()
            if value
        )
    
    @property
    def finished_nodes(self: Self) -> set[NodeIndex]:
        return set(
            node for node, value in self.nodes.items()
            if node and not value
        )
    
    def update_nodes_states(self: Self) -> None:
        for node in sorted(self.unfinished_nodes, key=len, reverse=True):
            if (
                self.num_children(node) == self.num_actions
                and
                all(self.nodes[ch] is None for ch in self.children(node))
            ):
                self.nodes[node] = None

    def add(self: Self, other: Self) -> None:
        self.nodes.update(other.nodes)


    