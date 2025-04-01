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
        return max(
            sorted(
                [n for n in self.nodes if not self.is_root(n)],
                key=lambda n: self.actions.index(n[-1]),
                reverse=True
            ) + [''], key=len)

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
        
        missing_nodes = []
        for d in range(depth):
            missing_children = []
            for n in missing_nodes + [
                n for n in self.nodes
                if self.depth(n)==d and not self.is_solution(n)
            ]:
                missing_children += self.missing_children(n)
            missing_nodes = missing_children
        num_missing_nodes = len(missing_nodes)

        num_nodes = len([
            n for n in self.nodes
            if self.depth(n) == depth
        ])

        return  num_nodes / (num_nodes + num_missing_nodes)

    @property
    def best_nodes(self: Self) -> list[NodeIndex]:
        solutions = sorted(
            sorted(self.solution_nodes),
            key=lambda k: self.nodes[k]
        )

        return [n for n in solutions if self.nodes[n] != float('inf')]
    
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