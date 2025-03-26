import pickle

from abc import ABC, abstractmethod
from typing_extensions import Self

from pyosrd.utils import seconds_to_hour
from pyosrd.groot2 import Groot, from_sim
from pyosrd.agents.update import updated_sim
from pyosrd.groot2.scores import sum_delays_at_end


class BaseAgent(ABC):

    name: str
    _dispatched_groot = None
    _interlocking_groot = None

    def __init__(
        self, name: str,
        sim,
        debug: bool = False,
    ) -> None:
        self._name = name
        self._sim = sim
        self._ref_groot = from_sim(sim)
        self._disrupted_groot = from_sim(sim.delayed())
        self._debug = debug
        self._scorer = sum_delays_at_end
        self.clear_cache()

    def save(self, path_to_file: str) -> None:
        with open(path_to_file, "wb") as f:
            pickle.dump(self, f)

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
    def disrupted_sim(self):
        return updated_sim(self.disrupted_groot, self.ref_groot, f'{self.name}_disrupted')

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
    def dispatched_sim(self):
        return updated_sim(self.dispatched_groot, self.ref_groot, f'{self.name}_dispatched')

    @property
    def interlocking_groot(self) -> Groot:
        if self._debug and self._interlocking_groot:
            print('Interlocking Groot is read in cache.')
        if not self._interlocking_groot:
            self._interlocking_groot = self._calculate_interlocking(self._debug)
        return self._interlocking_groot

    @abstractmethod
    def _calculate_interlocking(self: Self, debug: bool) -> Groot:
        ...
        
    @property
    def interlocking_sim(self):
        return updated_sim(self.interlocking_groot, self.ref_groot, f'{self.name}_interlocking')

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
        self._disrupted_groot = self._ref_groot.clone()
        self.clear_cache()
    

def load_agent(path_to_file: str) -> BaseAgent:
    with open(path_to_file, "rb") as f:
        agent = pickle.load(f)
    return agent
