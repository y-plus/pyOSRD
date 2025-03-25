from dataclasses import dataclass, field
from typing import Any
from typing_extensions import Self


@dataclass
class DecisionTree:

    actions: list[str]
    nodes: dict[str, Any | None] = field(default_factory=dict)

    @property
    def num_actions(self: Self) -> int:
        return len(self.actions)

    def __len__(self: Self) -> int:
        return len(self.nodes)

    def height(self: Self) -> int:
        return len(max(self.nodes, key=lambda k: len(k)))
    
    def depth(self: Self, node: str) -> int:
        return len(node)
    
    def parent(self: Self, node:str) -> str:
        if self.depth(node) > 0:
            return node[:-1]
    
    def children(self: Self, node: str) -> set[str]:
        return set(
            n for n in self.nodes
            if n and n[:-1] == node
        )
    
    def num_children(self: Self, node: str) -> int:
        return len(self.children(node))
    
    def missing_children(self: Self, node: str) -> list[str]:
        return [
            a for a in self.actions
            if f"{node}{a}" not in self.children(node)
        ]
    
    def is_leaf(self: Self, node: str) -> bool:
        return len(self.children(node)) == 0
    
    def max_num_sucessors(self: Self, node: str, depth: int) -> int:
        N = self.num_actions
        return int(
            ( 1 - N ** (depth - self.depth(node) + 1))
            / (1-len(self.actions)) - 1
        )
    
    def num_successors_on_missing_children_branches(
        self: Self,
        node: str,
        depth: int
    ) -> int:
        return ( 
            self.max_num_sucessors(node, depth) 
            * len(self.missing_children(node))
            / self.num_actions
        )
    
