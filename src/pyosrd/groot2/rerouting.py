import copy

import networkx as nx

from pyosrd.infra.distances import distance_between_points
from .groot import Groot, GrootTimes

def reroute_train_to_avoid_zone(
    self: Groot,
    train: str,
    zone: str,
) -> GrootTimes | None:

    original_times = {train: copy.deepcopy(self.times[train])}

    tvd_conflict = self.get_tvd(train, zone)
    next_station = self.next_station(train, zone)
    next_next_station = self.next_station(train, next_station) if next_station else None
    prev_station = self.previous_station(train, zone)
    prev_prev_station = self.previous_station(train, prev_station) if prev_station else None

    if prev_station is None and zone != self.path_zones(train)[0]:
        prev_station = self.path_zones(train)[0]
    if next_station is None and zone != self.path_zones(train)[-1]:
        next_station = self.path_zones(train)[-1]

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
    path_found = False
    for n1, n2 in [
        (tvd_prev_station, tvd_next_station),
        (tvd_prev_prev_station, tvd_next_station),
        (tvd_prev_station, tvd_next_next_station)
    ]:
        if n1 and n2:
            if path_found:= nx.has_path(subg, source=n1, target=n2):
                source, target = n1, n2
                break
    if not path_found:
        return

    train_path = self.path(train)
    
    while nx.has_path(subg, source=source, target=target):

        tvds = nx.shortest_path(subg, source, target)

        new = [tvd for tvd in tvds if tvd not in train_path]

        new_path = tvds[tvds.index(new[0])-1:tvds.index(new[-1])+2]
        original_path = train_path[
            train_path.index(new_path[0])
            :
            train_path.index(new_path[-1])+1
        ]

        
        rerouted_groot = copy.deepcopy(self)
        rerouted_groot.times[train] = {
            k: v
            for k, v in rerouted_groot.times[train].items()
            if k not in original_path[1:-1]
        }


        original_zones = [self.zones[tvd] for tvd in original_path[1:-1]]
        original_station = next((
            z for z in original_zones if '/' in z
        ), None)
        new_zones = [self.zones[tvd] for tvd in new_path[1:-1]]
        new_station = next((
            z for z in new_zones if '/' in z
        ), None)

        if original_station and new_station:
            new_entry_times, new_exit_times = [], []
            tvd_original_station = self.get_tvd(train, original_station)
            tvd_new_station = next(tvd for tvd in new_path if self.zones[tvd]==new_station)

            tvds_before_original_station = original_path[
                1:
                original_path.index(tvd_original_station)
            ]
            tvds_after_original_station = original_path[
                original_path.index(tvd_original_station)+1:
                -1
            ]
            tvds_before_new_station = new_path[
                1:
                new_path.index(tvd_new_station)
            ]
            tvds_after_new_station = new_path[
                new_path.index(tvd_new_station)+1:
                -1
            ]

            t_in_0 = self.times_zones[train][self.zones[tvds_before_original_station[0]]][0]
            t_out_0 = self.times_zones[train][self.zones[original_path[0]]][1]

            ts_in_0 = self.times[train][tvd_original_station][0]
            ts_out_0 = self.times[train][tvds_before_original_station[-1]][1]

            ts_in_1 = self.times[train][tvds_after_original_station[0]][0]
            ts_out_1 = self.times[train][tvd_original_station][1]

            t_in_1 = self.times_zones[train][self.zones[original_path[-1]]][0]
            t_out_1 = self.times_zones[train][self.zones[original_path[-2]]][1]

            new_length_before_station = sum(
                distance_between_points(
                    self._sim,
                    tvd.split('->')[0],
                    tvd.split('->')[1],
                    self._track_section_lengths,
                    self._track_section_network
                )
                for tvd in tvds_before_new_station
            )

            length = 0
            for tvd in tvds_before_new_station:
                t_in = (
                    t_in_0
                    + (ts_in_0-t_in_0) * length/new_length_before_station
                )
                length += distance_between_points(
                    self._sim,
                    tvd.split('->')[0],
                    tvd.split('->')[1],
                    self._track_section_lengths,
                    self._track_section_network
                )
                t_out = (
                    t_out_0
                    + (ts_out_0-t_out_0) * length/new_length_before_station
                )
                rerouted_groot.times[train][tvd] = (t_in, t_out)
            rerouted_groot.times[train][tvd_new_station] = self.times[train][tvd_original_station]
            new_length_after_station = sum(
                distance_between_points(
                    self._sim,
                    tvd.split('->')[0],
                    tvd.split('->')[1],
                    self._track_section_lengths,
                    self._track_section_network
                )
                for tvd in tvds_after_new_station
            )
            length = 0
            for tvd in tvds_after_new_station:
                t_in = (
                    ts_in_1
                    + (t_in_1-ts_in_1) * length/new_length_after_station
                )
                length += distance_between_points(
                    self._sim,
                    tvd.split('->')[0],
                    tvd.split('->')[1],
                    self._track_section_lengths,
                    self._track_section_network
                )
                t_out = (
                    ts_out_1
                    + (t_out_1-ts_out_1) * length/new_length_after_station
                )
                rerouted_groot.times[train][tvd] = (t_in, t_out)

            zones_that_must_be_free = [
                self.zones[tvd] for tvd in tvds_after_new_station
            ] + [new_station]

        else:
            new_length = sum(
                distance_between_points(
                    self._sim,
                    tvd.split('->')[0],
                    tvd.split('->')[1],
                    self._track_section_lengths,
                    self._track_section_network
                )
                for tvd in new_path[1:-1]
            )

            t_in_0 = self.times_zones[train][self.zones[original_path[1]]][0]
            t_out_0 = self.times_zones[train][self.zones[original_path[0]]][1]

            t_in_1 = self.times_zones[train][self.zones[original_path[-1]]][0]
            t_out_1 = self.times_zones[train][self.zones[original_path[-2]]][1]

            length=0
            new_entry_times, new_exit_times = [], []
            for tvd in new_path[1:-1]:
                new_entry_times.append(
                    t_in_0 + (t_in_1-t_in_0) * length/new_length
                )
                length += distance_between_points(
                    self._sim,
                    tvd.split('->')[0],
                    tvd.split('->')[1],
                    self._track_section_lengths,
                    self._track_section_network
                )
                new_exit_times.append(
                    t_out_0 + (t_out_1-t_out_0) * length/new_length
                )

            for tvd, entry_time, exit_time in zip(
                new_path[1:-1],
                new_entry_times,
                new_exit_times
            ):
                rerouted_groot.times[train][tvd] = (entry_time, exit_time)
            zones_that_must_be_free = new_zones
    
        tr1, tr2, conflict_zone, _ = rerouted_groot.earliest_conflict()
        conflict_tvd = rerouted_groot.get_tvd(train, conflict_zone)

        if conflict_zone in zones_that_must_be_free and train in (tr1, tr2):
            subg = nx.subgraph(subg, [n for n in subg if n!=conflict_tvd])
        else:
            self.times = rerouted_groot.times
            return original_times

