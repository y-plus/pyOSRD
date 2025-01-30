import copy

from abc import ABC, abstractmethod
from typing_extensions import Self

from pyosrd.utils import seconds_to_hour
from pyosrd.groot import Groot, from_sim
# from pyosrd.agents.update import sim_with_updated_results
from pyosrd.groot.objectives import sum_delays_at_end
from pyosrd.groot.dispatching import evaluate_action


class GrootAgent(ABC):

    name: str
    _dispatched_groot = None
    _interlocking_groot = None

    def __init__(self, name: str, sim, debug: bool = False) -> None:
        self._name = name
        self._sim = sim
        self._ref_groot = from_sim(sim)
        self._disrupted_groot = from_sim(sim.delayed())
        self._debug = debug
        self._scorer = sum_delays_at_end
        self.clear_cache()

    @property
    def name(self) -> str:
        return self._name
        
    @property
    def sim(self):
        return self._sim

    @property
    def debug(self: Self) -> bool:
        return self._debug
    
    @debug.setter
    def debug(self: Self, value: bool) -> None:
        self._debug = value

    @property
    def ref_groot(self) -> Groot:      
        return self._ref_groot
        
    @property
    def disrupted_groot(self) -> Groot:   
        return self._disrupted_groot

    @property
    def dispatched_groot(self) -> Groot:
        if self._debug and self._dispatched_groot:
            print('Dispatched Groot is read in cache.')
        if not self._dispatched_groot:
            self._dispatched_groot = self.calculate_dispatch(self._debug)
        return self._dispatched_groot
    
    @abstractmethod
    def calculate_dispatch(self: Self, debug: bool) -> Groot:
        pass
    
    @property
    def interlocking_groot(self) -> Groot:
        if self._debug and self._interlocking_groot:
            print('Interlocking Groot is read in cache.')
        if not self._interlocking_groot:
            self._interlocking_groot = self.calculate_interlocking(self._debug)
        return self._interlocking_groot

    def calculate_interlocking(self: Self, debug: bool) -> Groot:
        interlocking_groot =  copy.deepcopy(self.disrupted_groot)
        done = False
        self.interlocking_actions = []
        while not done:
            interlocking_groot, info = evaluate_action(
                interlocking_groot,
                a=0,
                ref=self.ref_groot,
                scorer=self._scorer
            )
            done = info['done']
            self.interlocking_actions.append(info)
        for i, action in enumerate(self.interlocking_actions):
                if i > 0:
                    added_score = action['score'] - self.interlocking_actions[i-1]['score']
                else:
                    added_score = action['score'] -self._scorer(self.disrupted_groot, self.ref_groot)    
                added_delay = seconds_to_hour(added_score)
                self.interlocking_actions[i] = {
                    **action,
                    'added_score': added_score,
                    'delay': seconds_to_hour(action['score']),
                    'added_delay': added_delay
                }
        return interlocking_groot

    # def regulated(
    #     self: Self,
    # ):
    #     return sim_with_updated_results(self.sim, self.dispatched_groot.times, self.name)

    def clear_cache(self: Self) -> None:
        self._interlocking_groot = None
        self.interlocking_actions = None
        self._dispatched_groot = None
        self.actions = None

    def score(self: Self, formatted: bool = False) -> float:
        s = self._scorer(self.dispatched_groot, self._ref_groot)
        if formatted:
            return(seconds_to_hour(s).split('.')[0])
        return s

    def interlocking_score(self: Self, formatted: bool = False) -> float:
        s = self._scorer(self.interlocking_groot, self._ref_groot)
        if formatted:
            return(seconds_to_hour(s).split('.')[0])
        return s
    
    def add_delay(self: Self, train: str, zone: str, delay: float) -> None:
        self._disrupted_groot = self.disrupted_groot.add_delay(train, zone, delay)

    def reset_disruptions(self: Self) -> None:
        self._disrupted_groot = copy.deepcopy(self._ref_groot)
        self.clear_cache()
    