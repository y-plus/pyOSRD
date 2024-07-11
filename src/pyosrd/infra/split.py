import copy
import json
import os
import shutil

from typing import Any

from railjson_generator import InfraBuilder
from railjson_generator.utils.routes_generator import generate_routes
from railjson_generator.schema.infra.direction import Direction
from railjson_generator.schema.infra.infra import Infra

from pyosrd import OSRD

SWITCHES_TYPES_DIRECTIONS = {
    'link': ['STATIC'],
    'point_switch': ['A_B1', 'A_B2'],
    'crossing': ['STATIC'],
    'double_slip_switch': ['A1_B1', 'A1_B2', 'A2_B1', 'A2_B2'],
}

SWITCH_EXIT = {
    'link': {'STATIC': {'A': 'B', 'B': 'A'}},
    'point_switch': {
        'A_B1': {'A': 'B1', 'B1': 'A'},
        'A_B2': {'A': 'B2', 'B2': 'A'},
    },
    'crossing': {
        'STATIC': {
            'A1': 'B1', 'B1': 'A1',
            'A2': 'B2', 'B2': 'A2',
        }
    },
    'double_slip_switch': {
        'A1_B1': {'A1': 'B1', 'B1': 'A1'},
        'A1_B2': {'A1': 'B2', 'B2': 'A1'},
        'A2_B1': {'A2': 'B1', 'B1': 'A2'},
        'A2_B2': {'A2': 'B2', 'B2': 'A2'},
    }
}


def generate_updated_routes(
      original_infra: dict,
      splitted_infra: dict,
      switches_to_buffer_stops: dict[str, dict],
      modified_switches: dict[str, dict],
) -> list:

    detectors = [d['id'] for d in splitted_infra['detectors']]
    buffer_stops = [d['id'] for d in splitted_infra['buffer_stops']]
    switches = {s['id']: s['switch_type'] for s in splitted_infra['switches']}
    waypoints = detectors + buffer_stops

    updated_routes = []
    for route in original_infra['routes']:
        entry = route['entry_point']['id']
        exit = route['exit_point']['id']
        if entry in waypoints and exit in waypoints:
            new_route = copy.deepcopy(route)
            release_detectors = [
                d for d in route['release_detectors']
                if d in detectors
            ]
            new_route['release_detectors'] = release_detectors
            switches_directions = {}
            for sw, dir in route['switches_directions'].items():
                if sw in switches:
                    if sw in modified_switches:
                        switches_directions[sw] = modified_switches[sw][dir]
                    else:
                        switches_directions[sw] = dir
            new_route['switches_directions'] = switches_directions
            updated_routes.append(new_route)
        if entry in waypoints and exit not in waypoints:
            replaced = [
                switch_id for switch_id in route['switches_directions']
                if switch_id in switches_to_buffer_stops
            ]
            if replaced:
                new_route = copy.deepcopy(route)
                port =\
                    route['switches_directions'][replaced[0]].replace('A_', '')
                if port in switches_to_buffer_stops[replaced[0]]:
                    bs = switches_to_buffer_stops[replaced[0]][port]
                    exit_point = {'type': 'BufferStop', 'id': bs}
                    new_route['exit_point'] = exit_point
                    new_route['id'] = route['id'].replace(exit, bs)
                    switches_directions = {}
                    for sw, dir in route['switches_directions'].items():
                        if sw in switches:
                            if sw in modified_switches:
                                switches_directions[sw] =\
                                    modified_switches[sw][dir]
                            else:
                                switches_directions[sw] = dir
                    new_route['switches_directions'] = switches_directions
                    release_detectors = [
                        d for d in route['release_detectors']
                        if d in detectors
                    ]
                    new_route['release_detectors'] = release_detectors
                    buffer_stop_exit = next(
                        b for b in splitted_infra['buffer_stops']
                        if b['id'] == bs
                    )
                    if buffer_stop_exit['position'] != 0:
                        new_route['entry_point_direction'] = "START_TO_STOP"
                    else:
                        new_route['entry_point_direction'] = "STOP_TO_START"
                    if not (
                        new_route['entry_point']['type']
                        == new_route['exit_point']['type']
                        == 'BufferStop'
                    ):
                        updated_routes.append(new_route)

        if entry not in waypoints and exit in waypoints:
            replaced = [
                switch_id for switch_id in route['switches_directions']
                if switch_id in switches_to_buffer_stops
            ]
            if replaced:
                new_route = copy.deepcopy(route)
                port = (
                    route['switches_directions'][replaced[-1]]
                    .replace('A_', '')
                )
                if port in switches_to_buffer_stops[replaced[-1]]:
                    bs = switches_to_buffer_stops[replaced[-1]][port]
                    entry_point = {
                        'type': 'BufferStop',
                        'id': bs
                    }
                    new_route['entry_point'] = entry_point
                    new_route['id'] = route['id'].replace(entry, bs)
                    switches_directions = {}
                    for sw, dir in route['switches_directions'].items():
                        if sw in switches:
                            if sw in modified_switches:
                                switches_directions[sw] =\
                                    modified_switches[sw][dir]
                            else:
                                switches_directions[sw] = dir
                    new_route['switches_directions'] = switches_directions
                    release_detectors = [
                        d for d in route['release_detectors']
                        if d in detectors
                    ]
                    buffer_stop_entry = next(
                        b for b in splitted_infra['buffer_stops']
                        if b['id'] == bs
                    )
                    if buffer_stop_entry['position'] == 0:
                        new_route['entry_point_direction'] = "START_TO_STOP"
                    else:
                        new_route['entry_point_direction'] = "STOP_TO_START"
                    new_route['release_detectors'] = release_detectors
                    if not (
                        new_route['entry_point']['type']
                        == new_route['exit_point']['type']
                        == 'BufferStop'
                    ):
                        updated_routes.append(new_route)
    return updated_routes


def build(self: InfraBuilder, progressive_release: bool = True) -> Infra:
    """Build the RailJSON infrastructure. Routes are generated if missing"""
    self._prepare_infra()
    duplicates = self.infra.find_duplicates()
    # Generate routes
    if not self.infra.routes:
        for route in generate_routes(self.infra, progressive_release):
            self.register_route(route)

    if duplicates:
        print("Duplicates were found:")
        for duplicate in duplicates:
            print(duplicate.__class__.__name__, duplicate.label)
        raise ValueError("Duplicates found")

    return self.infra


def filter_by_track_section_ids(
    # infra: dict[str, Any],
    sim,
    track_section_ids: list[str],
    dir: str | None = None,
    route_updates: bool = True
) -> OSRD:

    if dir is None:
        dir = sim.dir + '_sub'

    shutil.rmtree(dir, ignore_errors=True)
    new_sim = OSRD(dir=dir)
    os.makedirs(dir, exist_ok=True)

    # Detect missing tracks to complete the routes

    detector_ids = [
        detector['id']
        for detector in sim.infra['detectors']
        if detector['track'] in track_section_ids
    ]

    buffer_stop_ids = [
        buffer_stop['id']
        for buffer_stop in sim.infra['buffer_stops']
        if buffer_stop['track'] in track_section_ids
    ]

    missing_track_ids = set()

    SWITCHES_TRACKS = {
        s['id']: [e['track'] for e in s['ports'].values()]
        for s in sim.infra['switches']
    }

    for route in sim.infra['routes']:
        if (
            route['entry_point']['id'] in detector_ids+buffer_stop_ids
            and
            route['exit_point']['id'] in detector_ids+buffer_stop_ids
        ):
            not_visited = set(route['switches_directions'].keys())

            curr_track = next(
                p['track']
                for p in sim.infra['detectors'] + sim.infra['buffer_stops']
                if p['id'] == route['entry_point']['id']
            )
            while not_visited:
                sw = next(
                    switch
                    for switch in sim.infra['switches']
                    if curr_track in SWITCHES_TRACKS[switch['id']]
                    and switch['id'] in not_visited
                )
                sw_id = sw['id']
                entry_port = next(
                    p
                    for p, details in sw['ports'].items()
                    if details['track'] == curr_track
                )
                direction = route['switches_directions'][sw_id]
                exit_port =\
                    SWITCH_EXIT[sw['switch_type']][direction][entry_port]
                curr_track = sw['ports'][exit_port]['track']
                not_visited.remove(sw_id)
                if curr_track not in track_section_ids:
                    missing_track_ids.add(curr_track)

    track_section_ids += list(missing_track_ids)

    # Use an InfraBuilder to build a new infra restricted
    # to the track_section_ids

    infra_builder = InfraBuilder()

    # Track sections
    track_sections = dict()
    for track in sim.infra['track_sections']:
        if track['id'] in track_section_ids:
            track_sections[track['id']] = infra_builder.add_track_section(
                label=track['id'],
                length=track['length'],
            )

    # Detectors
    for detector in sim.infra['detectors']:
        if detector['track'] in track_sections:
            track_sections[detector["track"]].add_detector(
                detector['position'],
                label=detector['id'],
            )

    # Buffer stops
    for buffer_stop in sim.infra['buffer_stops']:
        if buffer_stop['track'] in track_sections:
            track_sections[buffer_stop["track"]].add_buffer_stop(
                buffer_stop['position'],
                label=buffer_stop['id'],
            )

    # Signals
    directions = {
        'START_TO_STOP': Direction.START_TO_STOP,
        'STOP_TO_START': Direction.STOP_TO_START,
    }
    for signal in sim.infra['signals']:
        if signal['track'] in track_section_ids:
            direction = signal['direction']

            added_signal = track_sections[signal["track"]].add_signal(
                signal['position'],
                label=signal['id'],
                direction=directions[direction],
                is_route_delimiter=True,
            )
            for logical_signal in signal['logical_signals']:
                added_signal.add_logical_signal(
                    logical_signal['signaling_system'],
                    settings=logical_signal['settings'],
                )

    # Update/modify switches
    switches = []
    for switch in sim.infra['switches']:
        for entry_port, details in switch['ports'].items():
            if details['track'] in track_sections:
                switches.append(switch)
                break

    switches_to_buffer_stops = dict()
    modified_switches = dict()

    buffer_stops_counter = 0
    for switch in switches:
        num_ports = 0
        keep_ports = dict()
        for entry_port, details in switch['ports'].items():
            num_ports += 1
            if details['track'] in track_sections:
                keep_ports[entry_port] = details

        num_tracks = len(keep_ports)
        switches_to_buffer_stops[switch['id']] = dict()

        if num_tracks == 1:
            entry_port, details = next(iter(keep_ports.items()))
            position = (
                0
                if details['endpoint'] == 'BEGIN'
                else track_sections[details['track']].length
            )
            track_sections[details['track']].add_buffer_stop(
                position=position,
                label=f"bs.{buffer_stops_counter}"
            )

            switches_to_buffer_stops[switch['id']][entry_port] = \
                f"bs.{buffer_stops_counter}"
            buffer_stops_counter += 1

        if num_tracks == num_ports:
            add_func = getattr(
                infra_builder,
                'add_' + switch['switch_type']
            )
            args = [
                track_sections[details['track']].begin()
                if details['endpoint'] == 'BEGIN'
                else track_sections[details['track']].end()
                for port, details in switch['ports'].items()
                if details['track'] in track_sections
            ]
            add_func(*args, label=switch['id'])

        if num_tracks == 2:
            stype = switch['switch_type']
            ports = tuple(keep_ports.keys())

            if (
                (stype == 'point_switch' and 'A' not in keep_ports)
                or
                (stype == 'crossing' and ports[0][1] != ports[1][1])
                or
                (stype == 'double_slip_switch' and ports[0][0] == ports[1][0])
            ):

                for entry_port, details in keep_ports.items():
                    position = (
                        0
                        if details['endpoint'] == 'BEGIN'
                        else track_sections[details['track']].length
                    )
                    track_sections[details['track']].add_buffer_stop(
                        position=position,
                        label=f"bs.{buffer_stops_counter}"
                    )

                    switches_to_buffer_stops[switch['id']][entry_port] = \
                        f"bs.{buffer_stops_counter}"
                    buffer_stops_counter += 1
            if (
                (stype == 'point_switch' and 'A' in keep_ports)
                or
                (stype == 'crossing' and ports[0][1] == ports[1][1])
                or
                (stype == 'double_slip_switch' and ports[0][0] != ports[1][0])
            ):
                args = [
                    track_sections[details['track']].begin()
                    if details['endpoint'] == 'BEGIN'
                    else track_sections[details['track']].end()
                    for port, details in switch['ports'].items()
                    if details['track'] in track_sections
                ]
                infra_builder.add_link(*args, label=switch['id'])
                modified_switches[switch['id']] = {
                    p: 'STATIC' for p in SWITCHES_TYPES_DIRECTIONS[stype]
                }
        if num_tracks == 3:
            stype = switch['switch_type']
            ports = tuple(keep_ports.keys())

            def port_to_endpoint(p: str, keep_ports):
                return (
                    track_sections[keep_ports[p]['track']].begin()
                    if keep_ports[p]['endpoint'] == 'BEGIN'
                    else track_sections[keep_ports[p]['track']].end()
                )
            if (
                stype == 'double_slip_switch'
            ):
                if 'A1' not in ports:
                    base = port_to_endpoint('A2', keep_ports)
                    left = port_to_endpoint('B1', keep_ports)
                    right = port_to_endpoint('B2', keep_ports)
                    modified_switches[switch['id']] = {
                        'A2_B1': 'A_B1',
                        'A2_B2': 'A_B2',
                    }
                if 'A2' not in ports:
                    base = port_to_endpoint('A1', keep_ports)
                    left = port_to_endpoint('B1', keep_ports)
                    right = port_to_endpoint('B2', keep_ports)
                    modified_switches[switch['id']] = {
                        'A1_B1': 'A_B1',
                        'A1_B2': 'A_B2',
                    }
                if 'B1' not in ports:
                    base = port_to_endpoint('B2', keep_ports)
                    left = port_to_endpoint('A1', keep_ports)
                    right = port_to_endpoint('A2', keep_ports)
                    modified_switches[switch['id']] = {
                        'A1_B2': 'A_B1',
                        'A2_B2': 'A_B2',
                    }
                if 'B2' not in ports:
                    base = port_to_endpoint('B1', keep_ports)
                    left = port_to_endpoint('A1', keep_ports)
                    right = port_to_endpoint('A2', keep_ports)
                    modified_switches[switch['id']] = {
                        'A1_B1': 'A_B1',
                        'A2_B1': 'A_B2',
                    }
                infra_builder.add_point_switch(
                    base=base,
                    left=left,
                    right=right,
                    label=switch['id'],
                )

            if (
                stype == 'crossing' and 'A1' in ports
            ):
                if 'B1' in ports:
                    a1 = keep_ports['A1']
                    b1 = keep_ports['B1']
                    infra_builder.add_link(
                        track_sections[a1['track']].begin()
                        if a1['endpoint'] == 'BEGIN'
                        else track_sections[a1['track']].end(),
                        track_sections[b1['track']].begin()
                        if b1['endpoint'] == 'BEGIN'
                        else track_sections[b1['track']].end(),
                        label=switch['id']
                    )
                    modified_switches[switch['id']] = {
                        p: 'STATIC' for p in SWITCHES_TYPES_DIRECTIONS[stype]
                    }
                    last_port = next(
                        port for port in keep_ports
                        if port not in ['A1', 'B1']
                    )
                    track = keep_ports[last_port]['track']
                    position = (
                        track_sections[track].length
                        if keep_ports[last_port]['endpoint'] == 'END'
                        else 0
                    )
                    track_sections[track].add_buffer_stop(
                            position=position,
                            label=f"bs.{buffer_stops_counter}"
                        )

                    switches_to_buffer_stops[switch['id']][entry_port] = \
                        f"bs.{buffer_stops_counter}"
                    buffer_stops_counter += 1
            if (
                stype == 'crossing' and 'A2' in ports
            ):
                if 'B2' in ports:
                    a2 = keep_ports['A2']
                    b2 = keep_ports['B2']
                    infra_builder.add_link(
                        track_sections[a2['track']].begin()
                        if a2['endpoint'] == 'BEGIN'
                        else track_sections[a2['track']].end(),
                        track_sections[b2['track']].begin()
                        if b2['endpoint'] == 'BEGIN'
                        else track_sections[b2['track']].end(),
                        label=switch['id']
                    )
                    modified_switches[switch['id']] = {
                        p: 'STATIC' for p in SWITCHES_TYPES_DIRECTIONS[stype]
                    }
                    last_port = next(
                        port for port in keep_ports
                        if port not in ['A2', 'B2']
                    )
                    track = keep_ports[last_port]['track']
                    position = (
                        track_sections[track].length
                        if keep_ports[last_port]['endpoint'] == 'END'
                        else 0
                    )
                    track_sections[track].add_buffer_stop(
                            position=position,
                            label=f"bs.{buffer_stops_counter}"
                        )

                    switches_to_buffer_stops[switch['id']][entry_port] = \
                        f"bs.{buffer_stops_counter}"
                    buffer_stops_counter += 1

    # Build infra
    built_infra = build(infra_builder, progressive_release=True)
    subinfra = built_infra.to_rjs().model_dump()

    # Rebuild routes
    if route_updates:
        subinfra['routes'] = generate_updated_routes(
            sim.infra,
            subinfra,
            switches_to_buffer_stops,
            modified_switches,
        )
    else:  # Clean duplicate route names
        unique_ids = set()
        routes = []

        for route in subinfra['routes']:
            new_route = route
            if route["id"] in unique_ids:
                new_route['id'] += '_1'
            unique_ids.add(new_route['id'])
            routes.append(new_route)

        subinfra = infra_builder.infra.to_rjs().model_dump()
        subinfra['routes'] = routes

    # Update the new infra by transferring track sections details
    subinfra['track_sections'] = [
        track_section
        for track_section in sim.infra['track_sections']
        if track_section['id'] in track_sections
    ]

    # Update the new infra to add detectors/buffer stops/ signals extensions
    detector_ids = [detector['id'] for detector in subinfra['detectors']]
    detectors = [
        detector
        for detector in sim.infra['detectors']
        if detector['id'] in detector_ids
    ]
    subinfra['detectors'] = detectors

    buffer_stop_ids = [bs['id'] for bs in subinfra['buffer_stops']]
    buffer_stop_ids_original = [bs['id'] for bs in sim.infra['buffer_stops']]
    buffer_stops = [
        buffer_stop
        for buffer_stop in sim.infra['buffer_stops']
        if buffer_stop['id'] in buffer_stop_ids
    ] + [
        buffer_stop
        for buffer_stop in subinfra['buffer_stops']
        if buffer_stop['id'] not in buffer_stop_ids_original
    ]  # buffer stops created to replace switches
    subinfra['buffer_stops'] = buffer_stops

    signal_ids = [signal['id'] for signal in subinfra['signals']]
    signals = [
        signal
        for signal in sim.infra['signals']
        if signal['id'] in signal_ids
    ]
    subinfra['signals'] = signals

    # Add operational_points

    op_ids = set()
    for op in sim.infra['operational_points']:
        for track in [part['track'] for part in op['parts']]:
            if track in track_section_ids:
                op_ids.add(op['id'])

    ops = []
    for op in sim.infra['operational_points']:
        if op['id'] in op_ids:
            new_op = copy.deepcopy(op)
            parts = [
                part
                for part in op['parts']
                if part['track'] in track_section_ids
            ]
            new_op['parts'] = parts
            ops.append(new_op)
    subinfra['operational_points'] = ops

    # speed sections
    subinfra['speed_sections'] = []
    for speed_section in sim.infra['speed_sections']:
        track_ranges = [
            track_range
            for track_range in speed_section['track_ranges']
            if track_range['track'] in track_section_ids
        ]
        if track_ranges:
            speed_section['track_ranges'] = track_ranges
            subinfra['speed_sections'].append(speed_section)

    # electrifications
    subinfra['electrifications'] = []
    for electrification in sim.infra['electrifications']:
        track_ranges = [
            track_range
            for track_range in electrification['track_ranges']
            if track_range['track'] in track_section_ids
        ]
        if track_ranges:
            electrification['track_ranges'] = track_ranges
            subinfra['electrifications'].append(electrification)

    # # neutral_sections
    subinfra['neutral_sections'] = []
    for neutral_section in sim.infra['neutral_sections']:
        track_ranges = [
            track_range
            for track_range in neutral_section['track_ranges']
            if track_range['track'] in track_section_ids
        ]
        if track_ranges:
            neutral_section['track_ranges'] = track_ranges
            subinfra['neutral_sections'].append(neutral_section)

    # Save new infra
    new_sim.infra = subinfra
    with open(os.path.join(new_sim.dir, new_sim.infra_json), 'w') as f:
        json.dump(subinfra, f)
    return new_sim


def filter_by_line_codes(
    sim,
    codes: int | list[int],
    dir: str | None = None,
) -> dict[str, Any]:

    if not isinstance(codes, list):
        codes = [codes]

    track_section_ids = [
        track['id']
        for track in sim.infra['track_sections']
        if track['extensions']['sncf']['line_code'] in codes
    ]

    return filter_by_track_section_ids(sim, track_section_ids)


def filter_by_latlng(
    sim,
    min_lat: float,
    max_lat: float,
    min_lng: float,
    max_lng: float,
    dir: str | None = None,
) -> dict[str, Any]:

    box = [min_lat, min_lng, max_lat, max_lng]
    track_section_ids = []
    for track_section in sim.infra['track_sections']:
        lats, longs = [], []
        for coords in track_section['geo']['coordinates']:
            lats.append(coords[0])
            longs.append(coords[1])

        bbox = [min(lats), min(longs), max(lats), max(longs)]
        xA = max(box[0], bbox[0])
        yA = max(box[1], bbox[1])
        xB = min(box[2], bbox[2])
        yB = min(box[3], bbox[3])
        intersection_area = abs(max((xB - xA, 0)) * max((yB - yA), 0))
        if intersection_area > 0:
            track_section_ids.append(track_section['id'])

    return filter_by_track_section_ids(sim, track_section_ids)
