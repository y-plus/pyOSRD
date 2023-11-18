import base64
import importlib
import json
import os
import pkgutil
import shutil
import subprocess
from dataclasses import dataclass
from importlib.resources import files
from itertools import combinations
from typing import Any, Dict, List, Union

import networkx as nx
import numpy as np
import PIL
import requests
from dotenv import load_dotenv
from typing_extensions import Self

import rlway.pyosrd.use_cases as use_cases


def _read_json(json_file: str) -> Union[Dict, List]:
    with open(json_file, 'r') as f:
        try:
            dict_ = json.load(f)
        except ValueError:  # JSONDecodeError inherits from ValueError
            dict_ = {}
    return dict_


@dataclass
class Point:
    track_section: str
    position: float
    id: str = ''
    type: str = ''


@dataclass
class OSRD():
    """Class with methods to run OSRD simulations and read infra and results

    Parameters
    ----------
    dir: str, optional
        Directory path, by default current directory
    use_case: str or None, optional
        If set, build a use_case
        among all availables given by `OSRD.use_cases`, by default None
    infra_json: str, optional
        Name of the file containing the infrastructure in rail_json format.
        If the file does not exist, attribute infra will be empty,
        by default 'infra.json'
    simulation_json: str, optional
        Name of the file containing the simulation parameters.
        If the file does not exist, attribute simulation will be empty,
        by default 'simulation.json'
    results_json: str, optional
        Name of the file containing the simulation results.
        If the file does not exist, attribute results will be empty,
        by default 'results.json'
    delays_json: str, optional
        Name of the file containing the delays applied to the perturbed
        simulation obtained with .delayed() method.
        If the file does not exist, attribute delays will be empty,
        by default 'delays.json'
    """
    dir: str = '.'
    use_case: Union[str, None] = None
    infra_json: str = 'infra.json'
    simulation_json: str = 'simulation.json'
    results_json: str = 'results.json'
    delays_json: str = 'delays.json'

    from .agents import Agent
    from .delays import add_delay, add_delays_in_results, delayed, reset_delays
    from .regulation import add_stop, add_stops
    from .viz.map import folium_map
    from .viz.space_time_charts import (
        space_time_chart,
        space_time_chart_plotly,
    )

    def __post_init__(self):

        if self.use_case:

            if self.use_case not in self.use_cases:
                raise ValueError(
                    f"{self.use_case} is not a valid use case name."
                )

            module = importlib.import_module(
                f".{self.use_case}",
                "rlway.pyosrd.use_cases"
            )
            function = getattr(module, self.use_case)
            function(
                self.dir,
                self.infra_json,
                self.simulation_json
            )

        self.infra = (
            _read_json(os.path.join(self.dir, self.infra_json))
            if os.path.exists(os.path.join(self.dir, self.infra_json))
            else {}
        )

        self.simulation = (
            _read_json(os.path.join(self.dir, self.simulation_json))
            if os.path.exists(os.path.join(self.dir, self.simulation_json))
            else {}
        )

        if self.use_case:
            self.run()

        self.results = (
            _read_json(os.path.join(self.dir, self.results_json))
            if os.path.exists(os.path.join(self.dir, self.results_json))
            else []
        )

    def run(self) -> None:
        """run the simulation and store the results in attribute results.

        Raises
        ------
        ValueError
            If missing infra or simulation json file.
        """
        if self.infra == {} or self.simulation == {}:
            raise ValueError("Missing json file to run OSRD")

        if os.path.exists(os.path.join(self.dir, self.results_json)):
            os.remove(os.path.join(self.dir, self.results_json))

        load_dotenv()
        JAVA = os.getenv('JAVA') or 'java'

        jar_file = files('rlway.pyosrd').joinpath('osrd-all.jar')

        output = subprocess.run(
            f"{JAVA} -jar {jar_file} standalone-simulation "
            f"--infra_path {os.path.join(self.dir, self.infra_json)} "
            f"--sim_path {os.path.join(self.dir, self.simulation_json)} "
            f"--res_path {os.path.join(self.dir, self.results_json)}",
            shell=True,
            stderr=subprocess.PIPE,
        )

        try:
            self.results = _read_json(
                os.path.join(self.dir, self.results_json)
            )
        except FileNotFoundError:
            raise RuntimeError(output.stderr.decode())

    @property
    def has_results(self) -> bool:
        """True if the object has simulation results"""
        return self.results != []

    @classmethod
    @property
    def use_cases(self) -> List[str]:
        """List of available use cases"""
        return [
            name
            for _, name, _ in pkgutil.iter_modules(use_cases.__path__)
        ]

    @property
    def routes(self) -> List[str]:
        """List of routes ids"""
        return [route['id'] for route in self.infra['routes']]

    @property
    def track_section_lengths(self) -> Dict[str, float]:
        """Dict of track sections and their lengths"""
        return {t['id']: t['length'] for t in self.infra['track_sections']}

    @property
    def num_switches(self) -> int:
        """Number of switches"""
        return len(self.infra['switches'])

    @property
    def station_capacities(self) -> Dict[str, int]:
        """Dict of stations ids (operational points) and their capacities"""
        return {
            station['id']: len(station['parts'])
            for station in self.infra['operational_points']
        }

    @property
    def num_stations(self) -> int:
        """Number of stations (defined as operational points)"""
        return len(self.station_capacities)

    def _points(self, op_part_tracks: bool = False) -> List[Point]:

        points = []

        for detector in self.infra['detectors']:
            points.append(Point(
                id=detector['id'],
                track_section=detector['track'],
                position=detector['position'],
                type='detector'
            ))

        for signal in self.infra['signals']:
            points.append(Point(
                id=signal['id'],
                track_section=signal['track'],
                position=signal['position'],
                type='signal'
            ))

        for buffer_stop in self.infra['buffer_stops']:
            points.append(Point(
                id=buffer_stop['id'],
                track_section=buffer_stop['track'],
                position=buffer_stop['position'],
                type='buffer_stop'
            ))

        for op in self.infra['operational_points']:
            for part in op['parts']:
                points.append(Point(
                    id=op['id'] + (
                        f"-{part['track']}" if op_part_tracks
                        else ''
                    ),
                    track_section=part['track'],
                    position=part['position'],
                    type='station'
                ))

        for link in self.infra['track_section_links']:
            for side in ['src', 'dst']:
                points.append(Point(
                    id=link['id'],
                    track_section=link[side]['track'],
                    position=(
                        0 if link[side]['endpoint'] == 'BEGIN'
                        else self.track_section_lengths[link[side]['track']]
                    ),
                    type='link',
                ))

        for switch in self.infra['switches']:
            for port in switch['ports'].values():
                points.append(Point(
                    id=switch['id'],
                    track_section=port['track'],
                    position=(
                        0 if port['endpoint'] == "BEGIN"
                        else self.track_section_lengths[port['track']]
                    ),
                    type='switch'

                ))
        return points

    def train_departure(self, train: int) -> Point:
        """Train departure point"""

        departure = self._head_position(train)[0]
        return Point(
            id=f'departure_{self.trains[train]}',
            track_section=departure['track_section'],
            position=departure['offset'],
            type='departure'
        )

    def train_arrival(self, train: int) -> Point:
        """Train arrival point"""

        arrival = self._head_position(train)[-1]
        return Point(
            id=f'arrival_{self.trains[train]}',
            track_section=arrival['track_section'],
            position=arrival['offset'],
            type='arrival'
        )

    def _head_position(self, train, eco_or_base: str = 'base'):

        group, idx = self._train_schedule_group[
            self.trains[train]
        ]

        sim = f'{eco_or_base}_simulations'
        return self.results[group][sim][idx]['head_positions']

    def points_on_track_sections(self, op_part_tracks: bool = False) -> Dict:
        """Dict with for each track, points of interests and their positions"""

        points_on_track_sections = {}

        for t in self.track_section_lengths:
            points = [
                p for p in self._points(op_part_tracks=op_part_tracks)
                if p.track_section == t
            ]
            points.sort(key=lambda p: p.position)
            points_on_track_sections[t] = points

        return points_on_track_sections

    def offset_in_path_of_train(
        self,
        point: Point,
        train: int
    ) -> float | None:

        tracks = self.train_track_sections(train)
        track_ids = [t['id'] for t in tracks]

        if point.track_section not in track_ids:
            return None

        idx_pt_tr = track_ids.index(point.track_section)

        if idx_pt_tr == 0:
            if tracks[0]['direction'] == 'START_TO_STOP':
                offset = point.position - self.train_departure(train).position
            else:
                offset = self.train_departure(train).position - point.position
            if offset < 0:
                return None
            return offset

        if tracks[0]['direction'] == 'START_TO_STOP':
            offset = (
                self.track_section_lengths[track_ids[0]]
                - self.train_departure(train).position
            )
        else:
            offset = self.train_departure(train).position

        for id in track_ids[1:idx_pt_tr]:
            offset += self.track_section_lengths[id]

        if tracks[0:idx_pt_tr][-1]['direction'] == 'START_TO_STOP':
            offset += point.position
        else:
            offset += (
                self.track_section_lengths[tracks[0:idx_pt_tr+1][-1]['id']]
                - point.position
            )
        return offset

    def draw_infra_points(
        self,
        save: str | None = None,
    ) -> PIL.PngImagePlugin.PngImageFile:
        """Use mermaid.js to display the infra as a graph of specificpoints

        Parameters
        ----------
        save : str | None, optional
            File name to save image, by default None

        Returns
        -------
        PIL.Image
            Inmage of the infra as a graph of points
        """

        g = 'graph LR;'

        points_all_tracks = self.points_on_track_sections(op_part_tracks=True)
        for _, points in points_all_tracks.items():
            for i, _ in enumerate(points[:-1]):
                g += (f"{points[i].id}<-->{points[i+1].id};")

        graphbytes = g.encode("ascii")
        base64_bytes = base64.b64encode(graphbytes)
        base64_string = base64_bytes.decode("ascii")
        url = "https://mermaid.ink/img/" + base64_string

        response = requests.get(url, stream=True)

        with open('tmp.png', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        image = PIL.Image.open('tmp.png')

        if save:
            os.rename('tmp.png', save)
        else:
            os.remove('tmp.png')

        return image

    @property
    def num_trains(self) -> int:
        """Number of trains in the simulation"""
        return sum(
            len(group['schedules'])
            for group in self.simulation['train_schedule_groups']
        )

    @property
    def trains(self) -> List[str]:
        """List of train ids in the simulation"""
        return [
            train['id']
            for group in self.simulation['train_schedule_groups']
            for train in group['schedules']
        ]

    @property
    def departure_times(self) -> List[float]:
        """List of trains departure times"""
        return [
            train['departure_time']
            for group in self.simulation['train_schedule_groups']
            for train in group['schedules']
        ]

    @property
    def _train_schedule_group(self) -> Dict[str, int]:
        return {
            train['id']: (group['id'], pos)
            for group in self.simulation['train_schedule_groups']
            for pos, train in enumerate(group['schedules'])
        }

    @property
    def _track_section_network(self) -> nx.DiGraph:

        ts = nx.DiGraph()

        if len(self.infra['track_sections']) == 1:
            ts.add_node(self.infra['track_sections'][0]['id'])
            return ts

        for t in self.infra['track_section_links']:
            ts.add_edge(
                t['src']['track'],
                t['dst']['track'],
                in_by=t['dst']['endpoint'],
                out_by=t['src']['endpoint'],
            )
            ts.add_edge(
                t['dst']['track'],
                t['src']['track'],
                in_by=t['src']['endpoint'],
                out_by=t['dst']['endpoint'],
                )
        for switch in self.infra['switches']:
            tracks = [track for _, track in switch['ports'].items()]
            for track1, track2 in combinations(tracks, 2):
                ts.add_edge(
                    track1['track'],
                    track2['track'],
                    out_by=track1['endpoint'],
                    in_by=track2['endpoint'],
                )
                ts.add_edge(
                    track2['track'],
                    track1['track'],
                    out_by=track2['endpoint'],
                    in_by=track1['endpoint'],
                )
        return ts

    def train_track_sections(self, train: int) -> List[Dict[str, str]]:
        """List of tracks for a given train trajectory"""

        head_positions = self._head_position(train=train)

        track_sections = list(
            dict.fromkeys([
                time["track_section"]
                for time in head_positions
            ]))

        # bug fix: if there is no record at a given track,
        # it won't appear in the list
        # => insert them by inspecting the links between the tracks

        ts = self._track_section_network

        tracks = track_sections[:1]

        for i, _ in enumerate(track_sections[:-1]):
            tracks += nx.shortest_path(
                ts,
                track_sections[i],
                track_sections[i+1]
            )[1:]

        DIRECTION_GIVEN_ENTRY = {
            'BEGIN': 'START_TO_STOP',
            'END': 'STOP_TO_START',
        }

        tracks_directions = []

        if len(tracks) > 1:
            for i, t in enumerate(tracks):
                if i == 0:
                    entry = nx.get_edge_attributes(ts, 'in_by')[
                        (tracks[i], tracks[i+1])
                    ]
                else:
                    entry = nx.get_edge_attributes(ts, 'in_by')[
                        (tracks[i-1], tracks[i])
                    ]
                tracks_directions.append({
                    'id': t,
                    'direction': DIRECTION_GIVEN_ENTRY[entry],
                })
        else:
            direction = 'START_TO_STOP' if (
                self.train_departure(train).position
                <= self.train_arrival(train).position
            ) else 'STOP_TO_START'
            tracks_directions = [{
                'id': tracks[0],
                'direction': direction,
            }]
        return tracks_directions

    def points_encountered_by_train(
        self,
        train: int,
        types: List[str] = [
            'departure',
            'signal',
            'detector',
            'station',
            'switch',
            'arrival',
        ],
    ) -> List[Dict[str, Any]]:
        """Points encountered by a train during its trajectory

        Parameters
        ----------
        types : List[str], optional
            Types of points, all types by default

        Returns
        -------
        List[TDict[str, Any]]
            Points encountered (id, type, offset)
        """

        ids = [track['id'] for track in self.train_track_sections(train)]

        points = {
            point.id: point
            for point in (
                [self.train_departure(train)]
                + self._points()
                + [self.train_arrival(train)]
            )
            if point.track_section in ids and point.type in types
        }

        def point_direction(point: Point) -> str:
            if point.type not in ['signal', 'detector']:
                return 'BOTH'
            if point.type == 'signal':
                for signal in self.infra['signals']:
                    if signal['id'] == point.id:
                        return signal['direction']
            if point.type == 'detector':
                for detector in self.infra['detectors']:
                    if detector['id'] == point.id:
                        return detector['applicable_directions']

        def train_direction(point: Point, train: int) -> str:
            for track in self.train_track_sections(train):
                if track['id'] == point.track_section:
                    return track['direction']

        list_ = [
            {
                'id': point.id,
                'offset': self.offset_in_path_of_train(point, train),
                'type': point.type,
            }
            for point in list(points.values())
            if (
                (
                    point_direction(point) == train_direction(point, train)
                    or point_direction(point) == 'BOTH'
                )
                and self.offset_in_path_of_train(point, train) is not None
            )
        ]

        list_.sort(key=lambda point: point['offset'])

        simulations = ['base']
        try:
            self._head_position(train, 'eco')
            simulations += ['eco']
        except TypeError:
            pass

        for eco_or_base in simulations:
            t = [
                record['time']
                for record in self._head_position(train, eco_or_base)
            ]
            path_offset = [
                record['path_offset']
                for record in self._head_position(train, eco_or_base)
            ]
            for point in list_:
                point['t_'+eco_or_base] = np.interp(
                    [point['offset']],
                    path_offset,
                    t
                ).item()
                point['t_tail_'+eco_or_base] = np.interp(
                    [point['offset'] + self.train_lengths[train]],
                    path_offset,
                    t
                ).item()

        return list_

    @property
    def train_lengths(self) -> list[float]:
        lengths = {
            rs['name']: rs['length']
            for rs in self.simulation['rolling_stocks']
        }
        return [
            lengths[train['rolling_stock']]
            for group in self.simulation['train_schedule_groups']
            for train in group['schedules']
        ]

    @property
    def _tvds(self) -> list[set[str]]:

        tvds = []
        for route in self.infra['routes']:
            limit_tvds = []
            limit_tvds.append(route['entry_point']['id'])
            for d in route['release_detectors']:
                limit_tvds.append(d)
            limit_tvds.append(route['exit_point']['id'])
            tvds += [
                set([limit_tvds[i], limit_tvds[i+1]])
                for i, _ in enumerate(limit_tvds[:-1])
            ]

        unique_tvds = []
        for tvd in tvds:
            if tvd not in unique_tvds:
                unique_tvds.append((tvd))

        return unique_tvds

    @property
    def tvd_blocks(self) -> dict[str, str]:

        tvd_blocks = {
            "<->".join(sorted(d)): "<->".join(sorted(d))
            for d in self._tvds
        }

        for switch in self.infra['switches']:
            detectors = []
            for port in switch['ports'].values():
                idx = 0 if port['endpoint'] == 'BEGIN' else -1
                detectors_on_track = [
                    p.id
                    for p in self.points_on_track_sections()[port['track']]
                    if p.type == 'detector'
                ]
                detectors.append(detectors_on_track[idx])

            for a in combinations(detectors, 2):
                if set(a) in self._tvds:
                    tvd_blocks["<->".join(sorted(a))] = switch['id']

        return tvd_blocks

    # @property
    # def entry_signals(
    #     self: "OSRD",
    # ) -> list[dict[str, str | None]]:

    #     entry_signals = []

    #     for train, _ in enumerate(self.trains):

    #         tvds_limits = []
    #         for track in self.train_track_sections(train):
    #             elements = [
    #                 p.id
    #                 for p in self.points_on_track_sections()[track['id']]
    #                 if p.type in ['buffer_stop', 'detector']
    #             ]
    #             tvds_limits += (
    #                 elements[::-1]
    #                 if track['direction'] == 'STOP_TO_START'
    #                 else elements
    #             )

    #         detectors = \
    #             self.points_encountered_by_train(train, types='detector')
    #         first_detector = detectors[0]['id']
    #         last_detector = detectors[-1]['id']
    #         idx_first = tvds_limits.index(first_detector)
    #         idx_last = tvds_limits.index(last_detector)

    #         limits = tvds_limits[idx_first-1:idx_last+2]

    #         signals = {}
    #         for i, _ in enumerate(limits[:-1]):

    #             start = limits[i]
    #             end = limits[i+1]
    #             s_id = None
    #             for p in self.points_encountered_by_train(
    #                 train=train,
    #                 types=['detector', 'signal']
    #             ):
    #                 if p['id'] == start or 'buffer' in start:
    #                     break
    #                 if p['type'] == 'signal':
    #                     s_id = p['id']

    #             signals[self.tvd_blocks["<->".join(sorted([start, end]))]] =\
    #                 s_id

    #         entry_signals.append(signals)

    #     return entry_signals

    def regulate(self, agent: Agent) -> Self:
        """Create and run a regulated simulation

        Parameters
        ----------
        agent : agents.Agent
            Regulation Agent

        Returns
        -------
        OSRD
            Regulated simulation.
            Results are saved in the directory 'delayed/<agent.name>'
        """
        return agent.regulated(self)

    @property
    def stop_positions(self) -> list[dict[str, Any]]:
        """Where can the trains stop in each zone ?

        If a zone is a switch, there is no stop point

        If a zone contains a station, the stop point is the station, defined
        by a part of an operational point

        If the zone has no station, the stop point is the last signal before
        the detector defining the end of the zone.

        The positions are offset in the path of each train (key 'offset').
        If the stop is at a signal or station, its corresponding id
        is also given.

        To retrieve a position, a typical usage would be,
        for example for the first train (index 0) and a zone name 'D1<->D2':
=
        >>> sim = OSRD(...)
        >>> sim.stop_positions[0]['D1<->D2']['position']

        Returns
        -------
        list[dict[str, Any]]
            List of dicts, one by train,where keys are the zones
            during the train's trajectory and the values are dicts with
            the stop points, their types and positions.
        """
        stop_positions = []

        for train_id, _ in enumerate(self.trains):
            positions = {}

            tvds_limits = []
            for track in self.train_track_sections(train_id):
                elements = [
                    p.id
                    for p in self.points_on_track_sections()[track['id']]
                    if p.type in ['buffer_stop', 'detector']
                ]
                tvds_limits += (
                    elements[::-1]
                    if track['direction'] == 'STOP_TO_START'
                    else elements
                )

            detectors = \
                self.points_encountered_by_train(train_id, types='detector')
            first_detector = detectors[0]['id']
            last_detector = detectors[-1]['id']
            idx_first = tvds_limits.index(first_detector)
            idx_last = tvds_limits.index(last_detector)

            limits = tvds_limits[idx_first-1:idx_last+2]

            points = self.points_encountered_by_train(
                train_id,
                types=['signal', 'detector', 'station', ]
            )

            train_tracks = [
                t['id']
                for t in self.train_track_sections(train_id)
            ]
            for i, _ in enumerate(limits[:-1]):
                start = limits[i]
                end = limits[i+1]
                zone = self.tvd_blocks["<->".join(sorted([start, end]))]

                for i, p in enumerate(points):
                    if p['id'] == end:
                        if (points[i-2]['type'] == 'station'):
                            station_point = next(
                                pt
                                for pt in self._points()
                                if pt.id == points[i-2]['id']
                                and pt.track_section in train_tracks
                            )
                            positions[zone] = {
                                'type': 'station',
                                'offset': self.offset_in_path_of_train(
                                            station_point, train_id
                                        ),
                                'id': points[i-2]['id'],
                            }
                        elif (points[i-1]['type'] == 'signal'):
                            signal_point = next(
                                p
                                for p in self._points()
                                if p.id == points[i-1]['id']
                            )
                            positions[zone] = {
                                'type': 'signal',
                                'offset': self.offset_in_path_of_train(
                                                signal_point, train_id
                                            ),
                                'id': points[i-2]['id'],
                            }
                        else:
                            positions[zone] = {
                                'type': 'switch',
                                'offset': None,
                            }

            last_zone = "<->".join(sorted([limits[-2], limits[-1]]))
            if points[-2]['type'] == 'station':

                station_point = next(
                    p
                    for p in self._points()
                    if p.id == points[-2]['id']
                )
                positions[zone] = {
                    'type': 'signal',
                    'offset': self.offset_in_path_of_train(
                                    station_point, train_id
                                ),
                    'id': points[-2]['id'],
                }
            elif points[-1]['type'] in ['station', 'signal']:
                stop_point = next(
                    p
                    for p in self._points()
                    if p.id == points[-1]['id']
                )
                positions[zone] = {
                    'type': points[-1]['type'],
                    'offset': self.offset_in_path_of_train(
                                    stop_point, train_id
                                ),
                    'id': points[-1]['id'],
                }
            else:
                positions[self.tvd_blocks[last_zone]] = {
                    'type': 'last_zone',
                    'offset': None,
                }
            stop_positions.append(positions)

        return stop_positions
