import copy
import itertools
import json
import os

from pyosrd.infra.distances import distance_between_points
from pyosrd.delays import add_delay_between_points

def _updated_routes(sim, train: int | str, tvd_limits: list[str]) -> list[str]:

    if isinstance(train, int):
        train = sim.trains[train]

    route_ios = {
        route['id']: (route['entry_point']['id'], route['exit_point']['id'])
        for route in sim.infra['routes']
    }
    route_release_detectors = {
        route['id']: set(route['release_detectors'])
        for route in sim.infra['routes']
    }

    new_routes = []

    entry = tvd_limits[0]

    rd=set()
    for detector in tvd_limits[1:]:
        exit = detector
        
        if (entry, exit) in route_ios.values():
            candidate_routes = [route for route, v in route_ios.items() if (entry, exit)==v]
            if len(candidate_routes) > 1:
                new_routes.append(

                    next(
                        r for r in candidate_routes
                        if rd.issubset(set(route_release_detectors[r]))
                    )
                )
            else:
                new_routes.append(candidate_routes[0])
            entry = exit
            rd = set()
        elif route := next(
            (
                r for r,v in route_ios.items()
                if exit == v[1] and entry in route_release_detectors[r]
            ),
            None
        ):
            new_routes.append(route)
            entry = exit
            rd = set()
        else:
            rd.add(exit)
        
    return new_routes


def _get_train_track_section_distances(
    sim,
    train: int | str,
    track_section_lengths,
) -> list[dict[str, str | float]]:

    if isinstance(train, str):
            train = sim.trains.index(train)

    group_id, _ = sim._train_schedule_group[
        sim.trains[train]
    ]
    group = next(
        gr
        for gr in sim.simulation['train_schedule_groups']
        if gr['id'] == group_id
    )
    first_track_id = group['waypoints'][0][0]['track_section']
    last_track_id = group['waypoints'][-1][-1]['track_section']
    first_position = group['waypoints'][0][0]['offset']
    last_position = group['waypoints'][-1][-1]['offset']

    train_track_section_distances = copy.copy(sim.train_track_sections(train))
    for track in train_track_section_distances:
        if track['id'] == first_track_id:
            start = 0
            end = (
                track_section_lengths[track['id']] - first_position
                if track['direction'] == 'START_TO_STOP'
                else first_position
            )
            length = end
        elif track['id'] != last_track_id:
            start = length
            end = start + track_section_lengths[track['id']]
            length = end
        else:
            start = length
            end = (
                last_position + length
                if track['direction'] == 'START_TO_STOP'
                else length + track_section_lengths[track['id']] - last_position
            )
        track['start'] = start
        track['end'] = end
        track['length'] = track_section_lengths[track['id']]

    return train_track_section_distances



def _get_track_and_position(
    train_track_section_distances,
    path_offset
) -> tuple[str, float]:
     for i, track in enumerate(train_track_section_distances):
            if path_offset >= track['start'] and path_offset <= track['end']:
                if i == 0:
                     offset = (
                        path_offset + track['length'] - track['end']
                        if track['direction'] == 'START_TO_STOP'
                        else track['end'] - path_offset
                    )
                else:
                    offset = (
                        path_offset - track['start']
                        if track['direction'] == 'START_TO_STOP'
                        else track['length'] - (path_offset - track['start'])
                    )
                return track['id'], offset



def updated_sim(
    new_groot,
    ref_groot,
    updated_sim_name: str,
):

    sim = ref_groot._sim
    track_section_lengths = sim.track_section_lengths
    track_section_network = sim._track_section_network

    updated = copy.deepcopy(sim)
    updated._train_track_sections = None

    times = new_groot.times

    for train in sim.trains:

        times[train] = dict(
            sorted(
                times[train].items(),
                key=lambda x: x[1][0]
            )
        )
        updated_tvd_limits =(
            [tvd.split('->')[0] for tvd in new_groot.path(train)]
            + [new_groot.path(train)[-1].split('->')[1]]
        )

        train_id = sim.trains.index(train)
        group, idx_in_group = sim._train_schedule_group[
                sim.trains[train_id]
                ]

        detectors_encountered_by_train =\
            sim.points_encountered_by_train(train, types=['detector'])

        # update routes
        for eco_or_base in ['eco', 'base']:
            if f'{eco_or_base}_simulations' not in updated.results[group]:
                continue
            updated_route_ids = _updated_routes(sim, train, updated_tvd_limits)
            updated.results[group][f'{eco_or_base}_simulations'][idx_in_group]['routing_requirements'] =\
                [{'route': route} for route in updated_route_ids]

        # get differences in detectors
        orig_detectors =\
            [d['id'] for d in detectors_encountered_by_train]
    

        new_detectors = [
            d if d not in orig_detectors else None
            for d in updated_tvd_limits[1:-1]
        ]

        new_segments = [
            list(v)
            for k, v in itertools.groupby(new_detectors, key=lambda x: x is None)
            if not k
        ]

        if new_segments:
            train_track_section_distances =\
                _get_train_track_section_distances(
                    updated,
                    train=train,
                    track_section_lengths=track_section_lengths
                )

        for segment in new_segments:
            last = segment[-1]
            segment.insert(0, updated_tvd_limits[updated_tvd_limits.index(segment[0])-1])
            segment.append(updated_tvd_limits[updated_tvd_limits.index(last)+1])

        for segment in new_segments:
            new_length = sum(
                distance_between_points(
                    sim,
                    d,
                    segment[i+1],
                    track_section_lengths,
                    track_section_network
                )
                for i, d in enumerate(segment[:-1])
            )
            p1 = updated.offset_in_path_of_train(updated.get_point(segment[0]), train)
            p2 = updated.offset_in_path_of_train(updated.get_point(segment[-1]), train)
            length = p2 - p1

            # update track sections and offsets
            for eco_or_base in ['eco', 'base']:
                if f'{eco_or_base}_simulations' not in updated.results[group]:
                    continue
                hp = updated._head_position(train, eco_or_base)
                new_hp = []
                for r in hp:

                    if r['path_offset'] < p1:
                        new_hp.append(r)

                    elif r['path_offset'] > p2:
                        new_hp.append(
                            {
                                **r,
                                'path_offset': r['path_offset'] + new_length - length
                            }
                        )
                    else:
                        new_path_offset = p1 + (r['path_offset'] - p1)/length*new_length
                        track_section, offset = _get_track_and_position(
                            train_track_section_distances,
                            new_path_offset
                        )
                        new_hp.append(
                            {
                                'time': r['time'],
                                'path_offset': new_path_offset,
                                'track_section': track_section,
                                'offset': offset,
                            }
                        )
                
                new_hp.sort(key=lambda r: r['time'])
                updated.results[group][f'{eco_or_base}_simulations'][idx_in_group]['head_positions'] =\
                    new_hp


        # UPDATE TIMES

        delay, total_delay = 0, 0
        for tvd in new_groot.path(train):
            if tvd in ref_groot.path(train):
                delay = round(
                    new_groot.times[train][tvd][-1] - total_delay
                    - ref_groot.times[train][tvd][-1],
                    2
                )
                if delay != 0:
                    if tvd == new_groot.path(train)[0]:
                        for eco_or_base in ['eco', 'base']:
                            if f'{eco_or_base}_simulations' not in updated.results[group]:
                                continue
                            hp = updated._head_position(train, eco_or_base)
                            for r in hp:
                                r['time'] += delay
                    else:
                        add_delay_between_points(
                        updated,
                        train,
                        tvd.split('->')[0],
                        tvd.split('->')[1],
                        delay
                    )
                    total_delay += delay
                    
    # save updated simulation
    os.makedirs(
        os.path.join(sim.dir, updated_sim_name),
        exist_ok=True
    )

    updated.results_json = os.path.join(
        updated_sim_name,
        sim.results_json
    )
    updated.delays_json = os.path.join(
        sim.delays_json
    )
    with open(os.path.join(updated.dir, updated.results_json), 'w') as outfile:
        json.dump(updated.results, outfile)

    return updated