import copy
from typing_extensions import Self

from pyosrd.groot import Groot
from pyosrd.agents.groot_agent import GrootAgent
from pyosrd.groot.dispatching import evaluate_action


class LazyAgent(GrootAgent):

    def calculate_dispatch(self: Self, debug: bool = False) -> Groot:
        dispatched_groot =  copy.deepcopy(self.disrupted_groot)
        done = False
        self.actions = []
        while not done:
            dispatched_groot, info = evaluate_action(
                dispatched_groot,
                a=0,
                ref=self.ref_groot,
                scorer=self._scorer
            )
            done = info['done']
            self.actions.append(info)
        return dispatched_groot
    

