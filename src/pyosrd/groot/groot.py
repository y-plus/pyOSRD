import copy
import itertools

from dataclasses import dataclass, field
from typing_extensions import Self
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from matplotlib.axes._axes import Axes

from pyosrd.utils import seconds_to_hour

from .build_zones import zones_graph

@dataclass
class Groot(object):
    zones: dict[str, str] = field(default_factory=dict)
    ends_with_a_signal: dict[str, bool] = field(default_factory=dict)
    stations: list[str] = field(default_factory=list)
    times: dict[str, dict[str, tuple[float, float]]] = field(default_factory=dict)
    min_durations: dict[str, dict[str, float]] = field(default_factory=dict)
    lengths: dict[str, float] = field(default_factory=dict)

    @property
    def trains(self) -> list[str]:
        return [train for train in self.times]

    def path(self, train) -> list[str]:
        return sorted(
            self.times[train],
            key=lambda x:  self.times[train][x][0]
        )

    def train_zones(self, train) -> list[str]:
        return [self.zones[tvd] for tvd in self.path(train)]
    
    @property
    def times_zones(self) -> dict[str, dict[str, tuple[float, float]]]:
        if not hasattr(self, '_times_zones') or self._times_zones is None:
            self._times_zones =  {
                train: {self.zones[k]: v for k, v in data.items()}
                for train, data in self.times.items()
            }
        return self._times_zones

    @property
    def zones_graph(self) -> nx.DiGraph:
        if not hasattr(self, '_zones_graph'):
            self._zones_graph = zones_graph(self.zones)
        return self._zones_graph

    def to_df(self) -> pd.DataFrame:
        df = pd.DataFrame(
            columns=pd.MultiIndex.from_product(
                [self.trains, ['s', 'e']]
            ),
            index=self.zones.values()
        )
        for train in self.trains:
            df[train] = pd.DataFrame(self.times_zones[train]).T.rename(columns={0: 's', 1:'e'})
        return df.drop_duplicates()


    def plot(self) -> Axes:

        gr = self.zones_graph

        extremities = [n for n,d in gr.in_degree() if d<=1]
        zones_to_sort = set(gr.nodes)
        sorted_zones = []

        for extr in extremities:
            connected_nodes = [
                n for n in zones_to_sort
                if nx.has_path(gr, n, extr)
            ]
            zones_to_sort -= set(connected_nodes)
            sorted_zones += sorted(connected_nodes, key= lambda n: len(nx.shortest_path(gr, n, extr)))

        sorted_zones = [
            z for z in sorted_zones
            if any(z in self.train_zones(train) for train in self.trains)
        ]

        _, ax = plt.subplots()

        times_zones = self.times_zones

        for train in self.times:
            width = [
                (times_zones[train][n][1] - times_zones[train][n][0])
                if n in times_zones[train]
                else 0
                for n in sorted_zones
            ]
            left = [
                times_zones[train][n][0]
                if n in times_zones[train]
                else 0
                for n in sorted_zones
            ]
            ax.barh(
                width=width,
                left=left,
                y=sorted_zones,
                label=train,
                height=1,
                alpha=.5
            )
        ax.set_xticks(
            [
                label._x
                for label in ax.get_xticklabels()
            ],
            [
                seconds_to_hour(int(float(label.get_text())))
                for label in ax.get_xticklabels()
            ]
        )
        ax.set_xlabel('Time')
        return ax

    def earliest_conflict(self) -> tuple[str, str, str, float]:

        times_zones = self.times_zones
        for train0, train1 in itertools.combinations(self.trains, 2):
            train_zones0 = self.train_zones(train0)
            train_zones1 = self.train_zones(train1)
            t_conflict = float('inf')
            train1_conflict, train2_conflict, zone_conflict = None, None, None
            for zone in train_zones0:
                if zone in train_zones1:
                    min_t_out = min(times_zones[train0][zone][1], times_zones[train1][zone][1])
                    max_t_in = max(times_zones[train0][zone][0], times_zones[train1][zone][0])
                    min_t_in = min(times_zones[train0][zone][0], times_zones[train1][zone][0])
                    if max_t_in <= min_t_out and min_t_in < t_conflict:
                        t_conflict = min_t_in
                        train1_conflict, train2_conflict, zone_conflict =\
                            train0, train1, zone
            if not train1_conflict:
                t_conflict = None
            return train1_conflict, train2_conflict, zone_conflict, t_conflict
        
    def has_conflicts(self) -> bool:
        return self.earliest_conflict()[0] is not None
    
    def trains_order_in_zone(self, train1, train2, zone) -> tuple[str, str]:
        if self.times_zones[train1][zone] <= self.times_zones[train2][zone]:
            return (train1, train2)
        return (train2, train1)
    
    def between(
        self,
        t_min: float = 0,
        t_max: float = float('inf'),
    ) -> Self:
        new = copy.deepcopy(self)
        new._times_zones = None
        new.times = {
            train: {
                zone: (max(t_min, t[0]), min(t_max, t[1])) 
                for zone, t in data.items()
                if t[1] > t_min and t[0] < t_max
            }
            for train, data in new.times.items()
        }
        return new

    def before(self, t: float) -> Self:
        return self.between(t_max=t)

    def after(self, t: float) -> Self:
        return self.between(t_min=t)

    def add_delay(
        self,
        train: str,
        zone: str,
        delay: float
    ) -> Self:
        new = copy.deepcopy(self)
        new._times_zones = None
        path = self.path(train)
        tvd = next(
            tvd for tvd in path
            if self.zones[tvd] == zone
        )
        idx = path.index(tvd)
        for i, zone in enumerate(path[idx:]):
            new.times[train][zone] = (
                self.times[train][zone][0] + delay,
                self.times[train][zone][1] + delay
            ) if i !=0 else (
                self.times[train][zone][0],
                self.times[train][zone][1] + delay
            )    
        return new

    def zones_are_free(
        self,
        zones: list[str],
        t1=0,
        t2=float('inf')
    ) -> bool:
        restricted = self.between(t1, t2)
        return all(
            zone not in restricted.times_zones[train]
            for train in restricted.times_zones
            for zone in zones
        )
    
    def previous_zones(self, train: str, zone: str) -> list[str]:
        zones = self.train_zones(train)
        return zones[::-1][zones[::-1].index(zone)+1:]

    def next_zones(self, train: str, zone: str) -> list[str]:
        zones = self.train_zones(train)
        return zones[zones.index(zone)+1:]

    def previous_station(self, train: str, zone: str) -> str:
        return next((z for z in self.previous_zones(train, zone) if z in self.stations), None)

    def next_station(self, train: str, zone: str) -> str:
        return next((z for z in  self.next_zones(train, zone) if z in self.stations), None)

    def get_tvd(self, train: str, zone: str) -> str:
        return next(
            tvd for tvd in self.path(train)
            if self.zones[tvd] == zone
        )

    def previous_signal(self, train: str, zone: str) -> str:
        return next(
            (
                z for z in self.previous_zones(train, zone)
                if self.ends_with_a_signal[self.get_tvd(train, z)]
            ),
            None
        )

    def next_signal(self, train: str, zone: str) -> str:
        return next(
            (
                z for z in  self.next_zones(train, zone)
                if self.ends_with_a_signal[self.get_tvd(train, z)]
            ),
            None
        )

    def previous_common_convergence(
        self,
        train1: str,
        train2: str,
        zone: str
    ) -> str:

        prev_zones1 = [zone] + self.previous_zones(train1, zone)
        prev_zones2 = [zone] + self.previous_zones(train2, zone)

        for i, z in enumerate(prev_zones1[:-1]):
            if (
                z in prev_zones2
                and prev_zones1[i+1] != prev_zones2[prev_zones2.index(z)+1]
            ):
                return z
        return None

    def is_a_divergence(self, zone: str, train1: str, train2: str) -> bool:
        train_zones1 = self.train_zones(train1)
        train_zones2 = self.train_zones(train2)
        if zone in [train_zones1[-1], train_zones2[-1]]:
            return False
        return train_zones1[train_zones1.index(zone)+1] != train_zones2[train_zones2.index(zone)+1]

    def alternative_zones(self, train: str, zone: str) -> list[list[str]]:

        next_station = self.next_station(train, zone)
        next_next_station = self.next_station(train, next_station) if next_station else None
        prev_station = self.previous_station(train, zone)
        prev_prev_station = self.previous_station(train, prev_station) if prev_station else None

        if prev_station is None and zone != self.train_zones(train)[0]:
            prev_station = self.train_zones(train)[0]
        if next_station is None and zone != self.train_zones(train)[-1]:
            next_station = self.train_zones(train)[-1]

        graph = self.zones_graph
        subg = nx.subgraph(graph, [n for n in graph if n!=zone])
        found = False
        for n1, n2 in [(prev_station, next_station), (prev_prev_station, next_station), (prev_station, next_next_station)]:
            if n1 and n2:
                if found:= nx.has_path(subg, source=n1, target=n2):
                    start, stop = n1, n2
                    continue

        if not found:
            return []
        return list(nx.all_simple_paths(subg, start, stop))

    def make_train_wait_after(
        self: Self,
        waiting_train: str,
        priority_train: str,
        wait_at: str,
        conflict_zone: str
    ) -> Self:

            zone_to_free = self.next_signal(priority_train, conflict_zone)
            delay = (
                    self.times_zones[priority_train][zone_to_free][1]
                    - self.times_zones[waiting_train][zone_to_free][0] 
            )
            return self.add_delay(waiting_train, wait_at, delay)