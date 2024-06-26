from itertools import combinations


import networkx as nx
import pandas as pd


from pyosrd import OSRD
from pyosrd.schedules import Schedule


def build_zones(sim: OSRD) -> tuple[nx.DiGraph, dict[str, str]]:
    """Build a directed graph and a dict of zones"""

    _tvds = []
    for route in sim.infra['routes']:
        limit_tvds = []
        if not (
            route['entry_point']['type']
            == route['exit_point']['type']
            == "BufferStop"
        ):
            limit_tvds.append(route['entry_point']['id'])
            for d in route['release_detectors']:
                limit_tvds.append(d)
            limit_tvds.append(route['exit_point']['id'])
            for tvd in [
                [limit_tvds[i], limit_tvds[i+1]]
                for i, _ in enumerate(limit_tvds[:-1])
            ]:
                _tvds.append(tvd)

    dict_tvd_zones = {
        "<->".join(sorted(d)): "<->".join(sorted(d))
        for d in _tvds
    }

    points = sim.points_on_track_sections()

    for switch in sim.switches:
        detectors = []
        for port in switch['ports'].values():
            idx = 0 if port['endpoint'] == 'BEGIN' else -1
            detectors_on_track = [
                p.id
                for p in points[port['track']]
                if p.type == 'detector'
            ]
            detectors.append(detectors_on_track[idx])

        for a in combinations(detectors, 2):
            if set(a) in [set(tvd) for tvd in _tvds]:
                dict_tvd_zones["<->".join(sorted(a))] = switch['id']

    graph_zones = nx.DiGraph()
    for tvd in _tvds:
        for other_tvd in _tvds:
            zone = dict_tvd_zones["<->".join(sorted(tvd))]
            other_zone = dict_tvd_zones["<->".join(sorted(other_tvd))]
            if (tvd[1] == other_tvd[0] and zone != other_zone):
                graph_zones.add_edge(zone, other_zone)

    switch_ids = [switch['id'] for switch in sim.switches]

    nodes = (
        zone
        for zone in graph_zones
        if zone in switch_ids
    )
    subgraph = graph_zones.subgraph(nodes)
    switch_groups = [
            list(s)
            for s in nx.connected_components(subgraph.to_undirected())
            if len(s) > 1
        ]

    for switches in switch_groups:
        merged_zone_name = "+".join(sorted(switches))
        for tvd, zone in sim.tvd_zones.items():
            if zone in switches:
                dict_tvd_zones[tvd] = merged_zone_name
        for i, switch in enumerate(switches[:-1]):
            nx.contracted_nodes(
                graph_zones,
                switches[0],
                switches[i+1],
                self_loops=False,
                copy=False
            )
        nx.relabel_nodes(
            graph_zones,
            {switches[0]: '+'.join([str(n) for n in switches])},
            copy=False
        )

    graph_points = nx.Graph()
    points_all_tracks = sim.points_on_track_sections(op_part_tracks=True)
    for _, points in points_all_tracks.items():
        points_track = [p for p in points if p.type != 'signal']
        # points_track = points
        for i, _ in enumerate(points_track[:-1]):
            graph_points.add_node(
                points_track[i].id,
                type=points_track[i].type
            )
            graph_points.add_node(
                points_track[i+1].id,
                type=points_track[i+1].type
            )
            graph_points.add_edge(
                points_track[i].id,
                points_track[i+1].id
            )

    switch_ids = [switch['id'] for switch in sim.infra['switches']]
    op_ids = [op['id'] for op in sim.infra['operational_points']]

    zone_type = dict()

    for tvd in dict_tvd_zones:
        limits = tvd.split('<->')
        point_between =\
            nx.shortest_path(graph_points, limits[0], limits[1])[1:-1]
        zone = dict_tvd_zones[tvd]
        if not point_between:
            zone_type[zone] = 'signal'
        elif point_between[0] in switch_ids:
            zone_type[zone] = 'switch'
        elif (op_id := point_between[0].split('-')[0]) in op_ids:
            zone_type[zone] = op_id

    nx.set_node_attributes(graph_zones, zone_type, 'type')

    return graph_zones, dict_tvd_zones


def build_schedule(
    sim: OSRD
) -> Schedule:

    g, dict_tvd_zones = build_zones(sim)

    df = pd.DataFrame(
        columns=pd.MultiIndex.from_product(
                [sim.trains, ['s', 'e']]
            ),
        index=g.nodes
    )
    times_dict = {train: {'s': {}, 'e': {}} for train in sim.trains}

    points_encountered_by_trains = {
            train: sim.points_encountered_by_train(train)
            for train in sim.trains
        }

    # points_on_track_sections = sim.points_on_track_sections()

    for train in sim.trains:
        times = {
            p['id']: (p['t_base'], p['t_tail_base'])
            for p in points_encountered_by_trains[train]
        }
        print(points_encountered_by_trains[train])
        for tvd, zone in dict_tvd_zones.items():
            p1, p2 = tvd.split('<->')
            if p1 in times:
                t1 = times[p1][0]
            if p2 in times:
                t2 = times[p2][0]
            if p1 in times and p2 in times:
                if t1 < t2:
                    times_dict[train]['s'][zone] = t1
                    times_dict[train]['e'][zone] = times[p2][1]
                else:
                    times_dict[train]['s'][zone] = t2
                    times_dict[train]['e'][zone] = times[p1][1]
    for train in sim.trains:
        df[[(train, 's'), (train, 'e')]] =\
            pd.DataFrame(times_dict[train])

    s = Schedule(len(g.nodes), sim.num_trains)
    s._df = df

    return s
