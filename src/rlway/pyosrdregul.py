from dataclasses import dataclass, field
from typing import Dict, Any, List, Protocol, TypedDict

from rlway.pyosrd import OSRD


class Disturbance(TypedDict):
    delays: Dict[str, Any]
    simulation: Dict[str, Any]
    results: List[Dict[str, Any]]


class AgentProtocol(Protocol):
    name: str

    def regulate(self) -> None:
        ...


class Regulation(TypedDict):
    agent: AgentProtocol
    simulation: Dict[str, Any]
    results: List[Dict[str, Any]]


@dataclass
class ORDSRegul(OSRD):

    disturbance: Disturbance = field(default_factory=dict)
    regulations: Dict[str, Regulation] = field(default_factory=dict)
