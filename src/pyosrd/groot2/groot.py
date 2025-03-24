import copy
import itertools

from dataclasses import dataclass, field
from typing_extensions import Self

import matplotlib.pyplot as plt
import networkx as nx

from matplotlib.axes._axes import Axes


from pyosrd.utils import seconds_to_hour
from pyosrd.viz.colors import train_colors

from .constructor.build_zones import zones_graph, tvds_graph


GrootTimes = dict[str, dict[str, tuple[float, float]]]
GrootDurations = dict[str, dict[str, float]] 


@dataclass
class Groot(object):
    zones: dict[str, str] = field(default_factory=dict)
    stations: list[str] = field(default_factory=list)
    ends_with_a_signal: dict[str, bool] = field(default_factory=dict)
    times: GrootTimes = field(default_factory=dict)
    min_durations: GrootDurations = field(default_factory=dict)

    def clone(self:Self) -> Self:
        return copy.deepcopy(self)

    @property
    def trains(self: Self) -> list[str]:
        return [train for train in self.times]

    def path(self: Self, train) -> list[str]:
        return sorted(
            self.times[train],
            key=lambda x:  self.times[train][x][0]
        )

    def path_zones(self: Self, train) -> list[str]:
        return [self.zones[tvd] for tvd in self.path(train)]

    @property
    def times_zones(self: Self) -> GrootTimes:
        return{
            train: {self.zones[k]: v for k, v in data.items()}
            for train, data in self.times.items()
        }


    @property
    def zones_graph(self: Self) -> nx.DiGraph:
        if not hasattr(self, '_zones_graph'):
            self._zones_graph = zones_graph(self.zones)
        return self._zones_graph

    @property
    def tvds_graph(self: Self) -> nx.DiGraph:
        if not hasattr(self, '_tvds_graph'):
            self._tvds_graph = tvds_graph(self.zones, self.ends_with_a_signal)
        return self._tvds_graph

    def plot(
        self: Self,
        train: str | None = None,
        legend: bool = True,
        display_zone_names: bool = False,
        reverse: bool = False
    ) -> Axes:


        if not train:
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
                if any(z in self.path_zones(train) for train in self.trains)
            ]
        else:
            sorted_zones = self.path_zones(train)


        if train:
            t_min = self.times_zones[train][self.path_zones(train)[0]][0]
            t_max = self.times_zones[train][self.path_zones(train)[-1]][1]
            times_zones = {
            train: {
                zone: (max(t_min, t[0]), min(t_max, t[1]))
                for zone, t in data.items()
                if t[1] > t_min and t[0] < t_max
            }
            for train, data in self.times_zones.items()
        }
        else:
            times_zones = self.times_zones

        colors = train_colors(self)
        _, ax = plt.subplots()
        for tr in self.times:
            width = [
                (times_zones[tr][n][1] - times_zones[tr][n][0])
                if n in times_zones[tr]
                else 0
                for n in sorted_zones
            ]
            left = [
                times_zones[tr][n][0]
                if n in times_zones[tr]
                else 0
                for n in sorted_zones
            ]
            if sum(width) > 0:
                ax.barh(
                    width=width,
                    left=left,
                    y=sorted_zones,
                    label=tr,
                    height=1,
                    alpha=.5,
                    color=colors[tr]
                )
        if train:
             ax.set_xlim(t_min, t_max)
        else:
            ax.set_xlim(
                min(self.departure_times.values()),
                max(self.last_arrival_times.values())
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
        plt.locator_params(axis='x', nbins=6)
        ax.set_xlabel('Time')
        if not display_zone_names:
            ax.set_yticks(
                [
                    label._y
                    for label in ax.get_yticklabels()
                ],
                [
                    label.get_text() if label.get_text() in self.stations else ''
                    for label in ax.get_yticklabels()
                ]
            )
        else:
            if train:
                ax.set_yticks(
                    [
                        label._y
                        for label in ax.get_yticklabels()
                    ],
                    [
                        self.get_tvd(train, zone) + f" ({zone})"
                        for zone in sorted_zones
                    ]
                )
        if train:
            ax.set_title(train)
        if legend:
            ax.legend()
        if reverse:
            ax.yaxis.set_inverted(True)
        return ax

    def earliest_conflict(
        self: Self,
        train1: str | None = None,
        train2: str | None = None,
    ) -> tuple[str, str, str, float]:

        times_zones = self.times_zones
        train1_conflict, train2_conflict, zone_conflict = None, None, None
        t_conflict = float('inf')

        if train1 is None:
            trains =  itertools.combinations(self.trains, 2)
        else:
            trains = [(train1, train2)]

        for tr1, train1 in trains:

            train_zones0 = self.path_zones(tr1)
            train_zones1 = self.path_zones(train1)

            for zone in set(train_zones0).intersection(set(train_zones1)):
                min_t_out = min(times_zones[tr1][zone][1], times_zones[train1][zone][1])
                max_t_in = max(times_zones[tr1][zone][0], times_zones[train1][zone][0])
                min_t_in = min(times_zones[tr1][zone][0], times_zones[train1][zone][0])
                if max_t_in < min_t_out and min_t_in < t_conflict:
                    t_conflict = min_t_in
                    train1_conflict, train2_conflict, zone_conflict =\
                        tr1, train1, zone
        if not train1_conflict:
            t_conflict = None
        return train1_conflict, train2_conflict, zone_conflict, t_conflict

    def all_conflicts(self) -> list[tuple[str, str, str, float]]:
        """Generate the list of all conflicts between all trains.
        Only generate the earliest conflict between two trains.

        Returns
        -------
        list[tuple[str, str, str, float]]
            The list of all conflicts using a tuple with:
            - train0
            - train1
            - tvd
            - time in seconds of the conflict
        """

        conflicts = []
        times_zones = self.times_zones
        for train0, train1 in itertools.combinations(self.trains, 2):
            t_conflict = float('inf')
            tup = None

            train_zones0 = self.path_zones(train0)
            train_zones1 = self.path_zones(train1)

            for zone in set(train_zones0).intersection(set(train_zones1)):
                min_t_out = min(times_zones[train0][zone][1], times_zones[train1][zone][1])
                max_t_in = max(times_zones[train0][zone][0], times_zones[train1][zone][0])
                min_t_in = min(times_zones[train0][zone][0], times_zones[train1][zone][0])
                if max_t_in < min_t_out and min_t_in < t_conflict:
                    t_conflict = min_t_in
                    tup = (train0, train1, zone, min_t_in)
            if tup is not None:
                conflicts.append(tup)
        return conflicts

    def has_conflicts(self: Self) -> bool:
        return self.earliest_conflict()[0] is not None

    def trains_order_in_zone(self: Self, train1, train2, zone) -> tuple[str, str]:
        if self.times_zones[train1][zone] <= self.times_zones[train2][zone]:
            return (train1, train2)
        return (train2, train1)

    def previous_zones(self: Self, train: str, zone: str) -> list[str]:
        zones = self.path_zones(train)
        return zones[::-1][zones[::-1].index(zone)+1:]

    def next_zones(self: Self, train: str, zone: str) -> list[str]:
        zones = self.path_zones(train)
        return zones[zones.index(zone)+1:]

    def previous_station(self: Self, train: str, zone: str) -> str | None:
        return next((z for z in self.previous_zones(train, zone) if z in self.stations), None)

    def next_station(self: Self, train: str, zone: str) -> str | None:
        return next((z for z in  self.next_zones(train, zone) if z in self.stations), None)

    def get_tvd(self: Self, train: str, zone: str) -> str | None:
        return next(
            (
                tvd for tvd in self.path(train)
                if self.zones[tvd] == zone
            ),
            None
        )

    def previous_signal(self: Self, train: str, zone: str) -> str | None:
        return next(
            (
                z for z in self.previous_zones(train, zone)
                if self.ends_with_a_signal[self.get_tvd(train, z)]
            ),
            None
        )

    def next_signal(self: Self, train: str, zone: str) -> str | None:
        return next(
            (
                z for z in  self.next_zones(train, zone)
                if self.ends_with_a_signal[self.get_tvd(train, z)]
            ),
            None
        )

    def previous_common_convergence(
        self: Self,
        train1: str,
        train2: str,
        zone: str
    ) -> str | None:

        if (
            zone==self.path_zones(train1)[0]
            or zone==self.path_zones(train2)[0]
        ):
            return None

        prev_zones1 = [zone] + self.previous_zones(train1, zone)
        prev_zones2 = [zone] + self.previous_zones(train2, zone)

        for i, z in enumerate(prev_zones1[:-1]):
            if (
                z in prev_zones2
                and prev_zones1[i+1] != prev_zones2[prev_zones2.index(z)+1]
            ):
                return z
        return None

 
    @property
    def departure_times(self: Self) -> dict[str, float]:
        return {
            train: self.times[train][self.path(train)[0]][0]
            for train in self.times
        }

    @property
    def last_arrival_times(self: Self) -> dict[str, float]:
        return {
            train: self.times[train][self.path(train)[-1]][1]
            for train in self.times
        }

    def trains_in_zone(self: Self, zone: str) -> list[str]:
        trains_entries = dict()
        for train in self.trains:
            if zone in self.times_zones[train]:
                trains_entries[train] = self.times_zones[train][zone][0]
        return [e[0]for e in sorted(trains_entries.items(), key= lambda x: x[1])]

    def previous_train(self: Self, train: str, zone: str) -> str | None:
        trains = self.trains_in_zone(zone)
        if train not in trains:
            return
        idx = trains.index(train)
        if idx == 0:
            return
        return trains[idx-1]

    def next_train(self: Self, train: str, zone: str) -> str | None:
        trains = self.trains_in_zone(zone)
        if train not in trains:
            return
        idx = trains.index(train)
        if idx == len(trains)-1:
            return
        return trains[idx+1]

    def set_times(
        self: Self,
        times: GrootTimes,
    ) -> GrootTimes:
        
        modified_times = copy.deepcopy(self.times)
        self.times.update(times)
        return modified_times
