import numbers

from dataclasses import dataclass, field

from typing import Any
from typing_extensions import Self

NodeIndex = str
Action = str


@dataclass
class DecisionTree:

    actions: list[Action] = field(default_factory=list)
    nodes: dict[NodeIndex, Any | None] = field(default_factory=lambda: {'': None})

    @property
    def num_actions(self: Self) -> int:
        return len(self.actions)

    def __len__(self: Self) -> int:
        return len(self.nodes)

    def __eq__(self, other: Self):
        return (
            self.actions == other.actions
            and
            self.nodes == other.nodes
        )

    def height(self: Self) -> int:
        return len(max(self.nodes, key=len))

    def depth(self: Self, node: NodeIndex) -> int:
        return len(node)

    @property
    def last_node(self: Self) -> NodeIndex:
        return max(self.nodes, key=len)

    def is_root(self: Self, node: NodeIndex) -> bool:
        return self.depth(node) == 0

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
        return int(
            self.max_num_sucessors(node, depth)
            * len(self.missing_children_edges(node))
            / self.num_actions
        )

    def is_solution(self: Self, node: NodeIndex) -> bool:
        return not self.is_root(node) and isinstance(self.nodes[node], numbers.Number)

    def is_explored(self: Self, node: NodeIndex) -> bool:
        return self.is_solution(node) or self.num_children(node)==self.num_actions

    @property
    def solution_nodes(self: Self) -> set[NodeIndex]:
        return set(
            node for node in self.nodes
            if self.is_solution(node)
        )

    @property
    def explored_nodes(self: Self) -> set[NodeIndex]:
        return set(
            node for node in self.nodes
            if not self.is_root(node)
            and self.is_explored(node)
        )

    @property
    def unexplored_nodes(self: Self) -> set[NodeIndex]:
        return set(
            node for node in self.nodes
            if not self.is_explored(node)
        )

    def combine(self: Self, other: Self):
        self.nodes.update(other.nodes)

    def depth_completeness_ratio(self: Self, node: NodeIndex) -> float:
        depth = self.depth(node)

        missing_nodes_at_this_depth = sum(
            self.num_successors_on_missing_children_branches(n, depth)
            for n in self.unexplored_nodes
            if self.depth(n) <= depth
        )

        nodes_at_this_depth = len([
            n for n in self.nodes
            if self.depth(n) == depth
        ])

        return  nodes_at_this_depth / (
            nodes_at_this_depth + missing_nodes_at_this_depth
        )

    @property
    def best_nodes(self: Self) -> list[NodeIndex]:
        return sorted(
            sorted(self.solution_nodes),
            key=lambda k: self.nodes[k]
        )
    
    def nodes_for_exploration(self: Self) -> list[NodeIndex]:
        return sorted(self.unexplored_nodes, key=self.depth)

    def nodes_for_improvements(self: Self) -> list[NodeIndex]:
        best_nodes = self.best_nodes
        best_node = best_nodes[0]

        if self.depth_completeness_ratio(best_node) == 1:
            return []

        return sum(
            [
                self.missing_brothers(n)
                for n in self.best_nodes
            ],
            []
        )