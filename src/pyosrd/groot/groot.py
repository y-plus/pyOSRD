import itertools

from dataclasses import dataclass, field

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from matplotlib.axes._axes import Axes

from pyosrd.utils import seconds_to_hour

from .build_zones import zones_graph

@dataclass
class Groot(object):
    zones: dict[str, str] = field(default_factory=dict)
    next_zone_with_signal: dict[str, str] = field(default_factory=dict)
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
        return {
            train: {self.zones[k]: v for k, v in data.items()}
            for train, data in self.times.items()
        }

    @property
    def zones_graph(self) -> nx.DiGraph:
        if not hasattr(self, '_zones_graph'):
            self._zones_graph = zones_graph(self.zones)
        return self._zones_graph

    def to_df(self: "Groot") -> pd.DataFrame:
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
            path0 = self.train_zones(train0)
            path1 = self.train_zones(train1)
            t_conflict = float('inf')
            train1_conflict, train2_conflict, zone_conflict = None, None, None
            for zone in path0:
                if zone in path1:
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