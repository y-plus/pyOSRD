import copy

from abc import ABC, abstractmethod
from typing_extensions import Self

from pyosrd import OSRD
from pyosrd.groot import Groot, from_sim
from pyosrd.agents.update import sim_with_updated_results
from pyosrd.groot.objectives import sum_delays_at_end
from pyosrd.utils import seconds_to_hour


class GrootAgent(ABC):

    name: str
    ref_groot: Groot | None = None
    _dispatched_groot: None

    def __init__(self, name: str, sim: OSRD, debug: bool = False) -> None:
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
    def sim(self) -> OSRD:      
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

    def regulated(
        self: Self,
    ) -> OSRD:
        return sim_with_updated_results(self.sim, self.dispatched_groot.times, self.name)
    
    @abstractmethod
    def calculate_dispatch(self: Self, debug: bool) -> Groot:
        pass

    def clear_cache(self: Self) -> None:
        self._dispatched_groot = None

    def score(self: Self, formatted: bool = False) -> float:
        s = self._scorer(self.dispatched_groot, self._ref_groot)
        if formatted:
            return(seconds_to_hour(s).split('.')[0])
        return s
    
    def add_delay(self: Self, train: str, zone: str, delay: float) -> None:
        self._disrupted_groot = self.disrupted_groot.add_delay(train, zone, delay)

    def reset_disruptions(self: Self) -> None:
        self._disrupted_groot = copy.deepcopy(self._ref_groot)
        self.clear_cache()
    