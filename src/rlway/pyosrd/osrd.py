import base64
import importlib
import json
import os
import pkgutil
from dataclasses import dataclass
from importlib.resources import files
from itertools import combinations
from typing import Any, Dict, List, Tuple, Union

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from dotenv import load_dotenv
from IPython.display import Image, display
from matplotlib.axes._axes import Axes

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
    id: str
    track_section: str
    position: float
    type: str


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
    """
    dir: str = '.'
    use_case: Union[str, None] = None
    infra_json: str = 'infra.json'
    simulation_json: str = 'simulation.json'
    results_json: str = 'results.json'

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
            try:
                self.run()
            except ValueError:
                self.results = []

        self.results = (
            _read_json(os.path.join(self.dir, self.results_json))
            if os.path.exists(os.path.join(self.dir, self.results_json))
            else []
        )

    def run(self) -> None:
        """run the simulation and store the results in attribute results.

        OSRD must be installed on the machine and the path defined
        in `.env` at the root of the project

        Raises
        ------
        ValueError
            If missing infra or simulation json file.
        """
        if self.infra == {} or self.simulation == {}:
            raise ValueError("Missing json file to run OSRD")

        load_dotenv()

        jar_file = files('rlway.pyosrd').joinpath('osrd-all.jar')
        os.system(
            f"java -jar {jar_file} standalone-simulation "
            f"--infra_path {os.path.join(self.dir, self.infra_json)} "
            f"--sim_path {os.path.join(self.dir, self.simulation_json)} "
            f"--res_path {os.path.join(self.dir, self.results_json)}"
        )

        self.results = _read_json(os.path.join(self.dir, self.results_json))

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
    def route_switches(self) -> Dict[str, str]:
        """Dict of routes that are switches and corresponding switch name"""
        return {
            route['id']: list(route['switches_directions'].keys())[0]
            for route in self.infra['routes']
            if len(list(route['switches_directions'].keys())) != 0
        }

    @property
    def route_limits(self) -> Dict[str, Tuple[str, float]]:
        """Dict of routes limiting points (detectors and buffer stops)

        >>> {'point_id' : ('track_id', position: float), ...}

        Returns
        -------
        Dict[str, Tuple[str, float]]
            Keys are points ids,
            values are tuples (associated track, position)
        """

        points_dict = {
            d['id']: (d['track'], d['position'])
            for d in self.infra['detectors']
        }
        points_dict.update({
            bs['id']: (bs['track'], bs['position'])
            for bs in self.infra['buffer_stops']
        })
        return points_dict

    @property
    def track_section_lengths(self) -> Dict[str, float]:
        """Dict of track sections and their lengths"""
        return {t['id']: t['length'] for t in self.infra['track_sections']}

    @property
    def route_lengths(self) -> Dict[str, float]:
        """Dict of routes and their lengths"""

        ts = self._track_section_network

        route_lengths = dict()

        for route in self.routes:
            P1, P2 = route.replace('rt.', '').split('->')
            point1 = [point for point in self._points if point.id == P1][0]
            point2 = [point for point in self._points if point.id == P2][0]
            tracks_between = nx.shortest_path(
                ts,
                point1.track_section,
                point2.track_section
            )

            distance = 0
            if len(tracks_between) == 1:
                distance = abs(point1.position - point2.position)
            else:
                distance = (
                    point1.position
                    if nx.get_edge_attributes(ts, 'out_by')[
                        tracks_between[0],
                        tracks_between[1]
                    ] == 'BEGIN'
                    else (
                        self.track_section_lengths[point1.track_section]
                        - point1.position
                    )
                )
                distance += sum(
                    self.track_section_lengths[track]
                    for track in tracks_between[1:-1]
                )
                distance += (
                    point2.position
                    if nx.get_edge_attributes(ts, 'in_by')[
                        tracks_between[-2],
                        tracks_between[-1]
                    ] == 'BEGIN'
                    else (
                        self.track_section_lengths[point2.track_section]
                        - point2.position
                    )
                )
            route_lengths[route] = distance

        return route_lengths

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

    @property
    def _points(self) -> List[Point]:

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
                    id=op['id'],
                    track_section=part['track'],
                    position=part['position'],
                    type='station'
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

    @property
    def points_on_track_sections(self) -> Dict:
        """Dict with for each track, points of interests and their positions"""

        points_on_track_sections = {}

        for t in self.track_section_lengths:
            points = [p for p in self._points if p.track_section == t]
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

        if idx_pt_tr > 0:

            if tracks[0]['direction'] == 'START_TO_STOP':
                offset = (
                    self.track_section_lengths[track_ids[0]]
                    - self.train_departure(train).position
                )
            else:
                offset = self.train_departure(train).position

            for t in tracks[0:idx_pt_tr-1]:
                offset += self.track_section_lengths[t['id']]

            # if point.position > self.train_arrival(train).position:
            #     return None

            if tracks[0:idx_pt_tr][-1]['direction'] == 'START_TO_STOP':
                offset += point.position
            else:
                offset += (
                    self.track_section_lengths[tracks[0:idx_pt_tr][-1]['id']]
                    - point.position
                )

        return offset

    def draw_infra(
        self,
    ) -> None:
        """Use mermaid.js to display the infra with detectors as nodes"""

        def mm(graph):
            graphbytes = graph.encode("ascii")
            base64_bytes = base64.b64encode(graphbytes)
            base64_string = base64_bytes.decode("ascii")
            display(Image(url="https://mermaid.ink/img/" + base64_string))

        g = "graph LR;"+";".join([
            route.replace('rt.', '').replace('->', '-->')
            for route in self.routes
        ])
        mm(g)

    @property
    def route_tvds(self) -> Dict[str, str]:
        """Routes and their associated TVDs (Track Vacancy Detections)"""
        return {
            route['id']:
            '<->'.join(sorted(route['id'].replace('rt.', '').split('->')))
            if not route['switches_directions']
            else list(route['switches_directions'].keys())[0]
            for route in self.infra['routes']
        }

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

        if len(tracks) > 0:
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
            Types of points, by default
            ['signal', 'detector', 'station', 'switch']

        Returns
        -------
        List[TDict[str, Any]]
            Points encountered (id, type, offset)
        """

        ids = [track['id'] for track in self.train_track_sections(train)]

        points = {
            point.id: {
                'id': point.id,
                'offset': self.offset_in_path_of_train(point, train),
                'type': point.type
            }
            for point in [self.train_departure(train)] + self._points + [self.train_arrival(train)]
            if point.track_section in ids and point.type in types
        }

        list_ = [p for p in list(points.values()) if p['offset'] is not None]
        list_.sort(key=lambda point: point['offset'])

        simulations = ['base']
        try:
            self._head_position(0,'eco')
            simulations += ['eco']
        except TypeError:
            pass

        for eco_or_base in simulations:
            t = [
                record['time']
                for record in self._head_position(0, eco_or_base=eco_or_base)
            ]
            path_offset = [
                record['path_offset']
                for record in self._head_position(0, eco_or_base=eco_or_base)
            ]
            for point in list_:
                point['t_'+eco_or_base] = np.interp(
                    [point['offset']],
                    path_offset,
                    t
                ).item()

        return list_

    def space_time_graph(
        self,
        train: int,
        eco_or_base: str = 'base',
        points_to_show: List[str] = ['station', 'switch'],
    ) -> Axes:
        """Draw space-time graph for a given train

        >>> ax = sim.space_time_graph(train=0, ...)

        Parameters
        ----------
        train : int
            Train index
        eco_or_base : str, optional
            Draw eco or base simulation ?, by default 'base'
        points_to_show : List[str], optional
            List of points types shown on y-axis.
            Possible choices are 'signal', 'detector', 'station', 'switch'.
            by default ['station', 'switch"]

        Returns
        -------
        Axes
            Matplotlib axe object
        """

        _, ax = plt.subplots()

        for i, train_id in enumerate(self.trains):
            t = [record['time'] / 60. for record in self._head_position(i)]
            offset = [
                self.offset_in_path_of_train(
                    Point(
                        id='',
                        track_section=record['track_section'],
                        type='record',
                        position=record['offset']
                    ),
                    train
                )
                for record in self._head_position(i)
            ]
            ax.plot(t, offset, label=train_id, linewidth=3)

        ax.legend()

        ax.set_xlim(left=0)
        ax.set_xlabel('Time [min]')
        ax.set_title(
            self.trains[train]
            + f" ({eco_or_base})"
        )

        ids = [track['id'] for track in self.train_track_sections(train)]

        points = {
            point.id: self.offset_in_path_of_train(point, train)
            for point in self._points
            if point.track_section in ids and point.type in points_to_show
        }

        for offset in points.values():
            ax.axhline(offset, linestyle='-', color='#aaa', linewidth=.5)

        ax.set_yticks(
            [offset for offset in points.values()],
            [id for id in points],
        )

        return ax
