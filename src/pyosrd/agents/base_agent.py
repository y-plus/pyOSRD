import pickle

from abc import ABC, abstractmethod
from typing import Callable
from typing_extensions import Self

import plotly.graph_objects as go

from pyosrd import OSRD
from pyosrd.utils import seconds_to_hour
from pyosrd.groot2 import Groot, from_sim
from pyosrd.agents.update import updated_sim
from pyosrd.groot2.scores import sum_delays_at_end
from pyosrd.groot2.delays_chart import plot_groot_delays

class BaseAgent(ABC):

    def __init__(
        self, name: str,
        sim: OSRD,
        debug: bool = False,
        scorer: Callable[[Groot, Groot], float] = sum_delays_at_end
    ) -> None:
        self.name = name
        self.sim = sim
        self.debug = debug
        self._scorer = scorer 

        self.ref_groot = from_sim(sim)
        self.disrupted_groot = from_sim(sim.delayed())
        self.disrupted_score = self._scorer(self.disrupted_groot, self.ref_groot)
    
        self._interlocking_groot = None
        self._dispatched_groot = None

    def save(self, path_to_file: str) -> None:
        with open(path_to_file, "wb") as f:
            pickle.dump(self, f)

    @property
    def disrupted_sim(self):
        return updated_sim(self.disrupted_groot, self.ref_groot, f'{self.name}_disrupted')

    @property
    def dispatched_groot(self) -> Groot:
        if self.debug and self._dispatched_groot:
            print('Dispatched Groot is read in cache.')
        if not self._dispatched_groot:
            self._dispatched_groot = self._calculate_dispatch(self.debug)
        return self._dispatched_groot
    
    @abstractmethod
    def _calculate_dispatch(self: Self, debug: bool) -> Groot:
        ...
    
    @property
    def dispatched_sim(self):
        return updated_sim(self.dispatched_groot, self.ref_groot, f'{self.name}_dispatched')

    @property
    def interlocking_groot(self) -> Groot:
        if self.debug and self._interlocking_groot:
            print('Interlocking Groot is read in cache.')
        if not self._interlocking_groot:
            self._interlocking_groot = self._calculate_interlocking(self.debug)
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


    def score(self: Self, formatted: bool = False) -> float:
        s = self._scorer(self.dispatched_groot, self.ref_groot)
        if formatted:
            return(seconds_to_hour(s).split('.')[0])
        return s

    def interlocking_score(self: Self, formatted: bool = False) -> float:
        s = self._scorer(self.interlocking_groot, self.ref_groot)
        if formatted:
            return(seconds_to_hour(s).split('.')[0])
        return s
    
    def add_delay(self: Self, train: str, zone: str, delay: float) -> None:
        self.disrupted_groot.add_delay(train, zone, delay)
        self.clear_cache()
    
    def reset_disruptions(self: Self) -> None:
        self.disrupted_groot = self.ref_groot.clone()
        self.clear_cache()
      
    def plot_delays(
        self: Self,
        all_trains: bool = False,
        tmin: float | str | None = None,
        tmax: float | str | None = None,
        dmax: float | str | None = None,
    ) -> go.Figure:

        return plot_groot_delays(
            self.dispatched_groot,
            self.ref_groot,
            all_trains=all_trains,
            tmin=tmin,
            tmax=tmax,
            dmax=dmax
        )

    def plot_interlocking_delays(
        self: Self,
        all_trains: bool = False,
        tmin: float | str | None = None,
        tmax: float | str | None = None,
        dmax: float | str | None = None,
    ) -> go.Figure:

        return plot_groot_delays(
            self.interlocking_groot,
            self.ref_groot,
            all_trains=all_trains,
            tmin=tmin,
            tmax=tmax,
            dmax=dmax
        )

    def plot_space_time(
        self: Self,
        train: str,
        reverse: bool = False,
    ) -> go.Figure:
        return self.dispatched_sim.space_time_chart_plotly(
            train,
            ref= self.sim,
            reverse=reverse
        )

    def plot_disrupted_space_time(
        self: Self,
        train: str,
        reverse: bool = False,
    ) -> go.Figure:
        return self.disrupted_sim.space_time_chart_plotly(
            train,
            ref= self.sim,
            reverse=reverse
        )

    def plot_interlocking_space_time(
        self: Self,
        train: str,
        reverse: bool = False,
    ) -> go.Figure:
        return self.interlocking_sim.space_time_chart_plotly(
            train,
            ref= self.sim,
            reverse=reverse
        )

def load_agent(path_to_file: str) -> BaseAgent:
    with open(path_to_file, "rb") as f:
        agent = pickle.load(f)
    return agent
