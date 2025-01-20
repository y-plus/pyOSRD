import copy

import networkx as nx
import numpy as np

from pyosrd.infra.distances import distance_between_points
from pyosrd.groot import Groot

def reroute_train_to_avoid_zone(
    self: Groot,
    train: str,
    zone: str
) -> Groot | None:

    tvd_conflict = self.get_tvd(train, zone)
    next_station = self.next_station(train, zone)
    next_next_station = self.next_station(train, next_station) if next_station else None
    prev_station = self.previous_station(train, zone)
    prev_prev_station = self.previous_station(train, prev_station) if prev_station else None

    if prev_station is None and zone != self.train_zones(train)[0]:
        prev_station = self.train_zones(train)[0]
    if next_station is None and zone != self.train_zones(train)[-1]:
        next_station = self.train_zones(train)[-1]

    tvd_prev_station = self.get_tvd(train, prev_station)
    tvd_next_station = self.get_tvd(train, next_station)

    tvd_prev_prev_station = (
        self.get_tvd(train, prev_prev_station)
        if prev_prev_station
        else None
    )
    tvd_next_next_station = (
        self.get_tvd(train, next_next_station)
        if next_next_station
        else None
    )

    graph = self.tvds_graph
    subg = nx.subgraph(graph, [n for n in graph if n!=tvd_conflict])
    found = False
    for n1, n2 in [
        (tvd_prev_station, tvd_next_station),
        (tvd_prev_prev_station, tvd_next_station),
        (tvd_prev_station, tvd_next_next_station)
    ]:
        if n1 and n2:
            if found:= nx.has_path(subg, source=n1, target=n2):
                source, target = n1, n2
                break
    if not found:
        return None

    train_path = self.path(train)
    points = self._sim.points_encountered_by_train(train)
    hp = self._sim._head_position(train, 'eco')

    while nx.has_path(subg, source=source, target=target):
        
        tvds = nx.shortest_path(subg, source, target)

        new_tvds = [tvd for tvd in tvds if tvd not in train_path]
        rerouted_path = tvds[tvds.index(new_tvds[0])-1:tvds.index(new_tvds[-1])+2]
        original_path = train_path[
            train_path.index(rerouted_path[0])
            :
            train_path.index(rerouted_path[-1])+1
        ]

        # new_length = sum(distance_between_points(
        #         self._sim,
        #         tvd.split('->')[0],
        #         tvd.split('->')[1],
        #         self._track_section_lengths,
        #         self._track_section_network
        #     ) for tvd in rerouted_path[1:-1])

        start = next(p for p in points if p['id']==rerouted_path[0].split('->')[1])
        end = next(p for p in points if p['id']==rerouted_path[-1].split('->')[0])

        new_positions = [
            start['offset'] + distance_between_points(
                self._sim,
                start['id'],
                tvd.split('->')[0],
                self._track_section_lengths,
                self._track_section_network
            )
            for tvd in new_tvds
        ]
        new_entry_times = np.interp(
            new_positions,
            [r['path_offset'] for r in hp],
            [r['time'] for r in hp]
        )
        train_length = self._sim.train_lengths[self._sim.trains.index(train)]
        new_exit_times = np.interp(
            [new_positions[i+1]+train_length for i, _ in enumerate(new_positions[:-1])],
            [r['path_offset'] for r in hp],
            [r['time'] for r in hp]
        )
        new_exit_times = np.append(new_exit_times,
            np.interp(
                [end['offset'] + train_length],
                [r['path_offset'] for r in hp],
                [r['time'] for r in hp]
            ).item()
        )

        new_groot = copy.deepcopy(self)
        new_groot._times_zones = None

        new_groot.times[train] = {
            k: v
            for k, v in new_groot.times[train].items()
            if k not in original_path[1:-1]
        }
        for tvd, entry_time, exit_time in zip(new_tvds, new_entry_times, new_exit_times):
            new_groot.times[train][tvd] = (
                entry_time,
                exit_time
            )
        _, _, conflict_zone, _ = new_groot.earliest_conflict()
        conflict_tvd = new_groot.get_tvd(train, conflict_zone)

        if conflict_tvd in rerouted_path:
            subg = nx.subgraph(subg, [n for n in subg if n!=conflict_tvd])
        else:
            return new_groot
    return None
