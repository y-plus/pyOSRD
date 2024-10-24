import base64
import importlib
import json
import os
import pkgutil
import shutil
import subprocess

from dataclasses import dataclass
from dataclasses import field
from importlib.resources import files
from itertools import combinations
from typing import Any

import networkx as nx
import numpy as np
import PIL
from PIL.JpegImagePlugin import JpegImageFile
import requests
from dotenv import load_dotenv
from typing_extensions import Self
from methodtools import lru_cache

import pyosrd.use_cases.infras as infras
import pyosrd.use_cases.simulations as simulations
import pyosrd.use_cases.with_delays as with_delays


def _read_json(json_file: str) -> dict | list:
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
    infra: str or None, optional
        If set, build a infra
        among all availables given by `OSRD.infras`, by default None
    simulation: str or None, optional
        If set, build a simulation (composed of an infra and trains)
        among all availables given by `OSRD.simulations`, by default None
    with_delay: str or None, optional
        If set, build a simulation with delays (composed of an infra,
        trains and delays) among all availables given by
        `OSRD.with_delays`, by default None
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
    infra: str | None = None
    simulation: str | None = None
    with_delay: str | None = None
    infra_json: str = 'infra.json'
    simulation_json: str = 'simulation.json'
    results_json: str = 'results.json'
    delays_json: str = 'delays.json'
    params_use_case: dict = field(default_factory=dict)

    from .agents import Agent
    from .delays import add_delay, add_delays_in_results, delayed, reset_delays
    from .regulation import add_stop, add_stops
    from .viz.map import folium_map, folium_results
    from .viz.space_time_charts import (
        space_time_chart,
        space_time_chart_plotly,
    )
    from .viz.delays_chart import (
        delays_chart,
        delays_chart_plotly
    )
    from .modify_simulation import (
        add_train,
        add_scheduled_points,
        cancel_train,
        cancel_all_trains,
        stop_train,
        copy_train
    )

    def __post_init__(self):

        # If working with a use_case
        if (
            self.infra
            or self.simulation
            or self.with_delay
        ):
            # Clean json files and delayed/ in the indicated directory
            for json_file in [
                self.infra_json,
                self.simulation_json,
                self.results_json,
                self.delays_json,
            ]:
                if os.path.exists(os.path.join(self.dir, json_file)):
                    os.remove(os.path.join(self.dir, json_file))

            if os.path.exists(os.path.join(self.dir, 'delayed')):
                shutil.rmtree(os.path.join(self.dir, 'delayed'))

        # Load with_delay if any is given
        if self.with_delay:

            if self.with_delay not in OSRD.with_delays():
                raise ValueError(
                    f"{self.with_delay} is not a valid use case " +
                    "with_delay name."
                )

            module = importlib.import_module(
                f".{self.with_delay}",
                "pyosrd.use_cases.with_delays"
            )
            function = getattr(module, self.with_delay)
            function(
                self.dir,
                self.infra_json,
                self.simulation_json,
                self.delays_json,
                **self.params_use_case
            )

        # Load simulation if any is given
        elif self.simulation:

            if self.simulation not in OSRD.simulations():
                raise ValueError(
                    f"{self.simulation} is not a valid use case " +
                    "simulation name."
                )

            module = importlib.import_module(
                f".{self.simulation}",
                "pyosrd.use_cases.simulations"
            )
            function = getattr(module, self.simulation)
            function(
                self.dir,
                self.infra_json,
                self.simulation_json,
                **self.params_use_case
            )

        elif self.infra:

            if self.infra not in OSRD.infras():
                raise ValueError(
                    f"{self.infra} is not a valid use case name."
                )

            module = importlib.import_module(
                f".{self.infra}",
                "pyosrd.use_cases.infras"
            )
            function = getattr(module, self.infra)
            function(
                self.dir,
                self.infra_json,
                **self.params_use_case
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

        self.results = (
            _read_json(os.path.join(self.dir, self.results_json))
            if os.path.exists(os.path.join(self.dir, self.results_json))
            else []
        )

        if self.simulation and not self.results:
            self.run()

    def run(self) -> None:
        """run the simulation and store the results in attribute results.

        Raises
        ------
        ValueError
            If missing infra or simulation json file.
        """
        if (
            self.infra == {} or self.simulation == {} or
            self.infra is None or self.simulation is None
        ):
            raise ValueError("Missing json file to run OSRD")

        if os.path.exists(os.path.join(self.dir, self.results_json)):
            os.remove(os.path.join(self.dir, self.results_json))

        load_dotenv()
        JAVA = os.getenv('JAVA') or 'java'

        jar_file = files('pyosrd').joinpath('osrd-0213.jar')

        output = subprocess.run(
            f"{JAVA} -jar {jar_file} standalone-simulation "
            f"--infra_path {os.path.join(self.dir, self.infra_json)} "
            f"--sim_path {os.path.join(self.dir, self.simulation_json)} "
            f"--res_path {os.path.join(self.dir, self.results_json)}",
            shell=True,
            stderr=subprocess.PIPE,
        )

        self.train_track_sections.cache_clear()

        try:
            self.results = _read_json(
                os.path.join(self.dir, self.results_json)
            )
        except FileNotFoundError:
            raise RuntimeError(output.stderr.decode())

    def validate_infra(self) -> None:
        """Loads the infra in core and validates"

        Raises
        ------
        ValueError
            If missing infra json file.
        """
        if (
            self.infra == {} or self.infra is None
        ):
            raise ValueError("Missing infra json file")

        load_dotenv()
        JAVA = os.getenv('JAVA') or 'java'

        jar_file = files('pyosrd').joinpath('osrd-0213.jar')

        try:
            output = subprocess.run(
                f"{JAVA} -jar {jar_file} load-infra "
                f"--path {os.path.join(self.dir, self.infra_json)} ",
                shell=True,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError:
            raise RuntimeError(output.stderr.decode())

    @property
    def has_results(self) -> bool:
        """True if the object has simulation results"""
        return self.results != []

    def infras() -> list[str]:
        """List of available infras"""
        return [
            name
            for _, name, _ in pkgutil.iter_modules(infras.__path__)
        ]

    def simulations(infra: str | None = None) -> list[str]:
        """List of available simulations"""
        return [
            name
            for _, name, _ in pkgutil.iter_modules(simulations.__path__)
            if infra is None or infra+"_" in name
        ]

    def with_delays(sim: str | None = None) -> list[str]:
        """List of available simulations"""
        return [
            name
            for _, name, _ in pkgutil.iter_modules(with_delays.__path__)
            if sim is None or sim+"_" in name
        ]

    @property
    def routes(self) -> list[str]:
        """List of routes ids"""
        return [route['id'] for route in self.infra['routes']]

    @property
    def track_section_lengths(self) -> dict[str, float]:
        """Dict of track sections and their lengths"""
        return {t['id']: t['length'] for t in self.infra['track_sections']}

    @property
    def switches(self) -> list[dict[str, Any]]:
        """ List of switches (track section links excluded)"""
        return [
            switch for switch in self.infra['switches']
            if switch['switch_type'] != 'link'
        ]

    @property
    def num_switches(self) -> int:
        """Number of switches"""
        return len(self.switches)

    @property
    def station_capacities(self) -> dict[str, int]:
        """Dict of stations ids (operational points) and their capacities"""
        return {
            station['id']: len(station['parts'])
            for station in self.infra['operational_points']
        }

    @property
    def num_stations(self) -> int:
        """Number of stations (defined as operational points)"""
        return len(self.station_capacities)

    def _points(self, op_part_tracks: bool = False) -> list[Point]:

        points = []
        lengths = self.track_section_lengths
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
            if op['extensions']['sncf']['ch'] in ['00', 'BV']:
                for part in op['parts']:
                    track_section = next(
                        track 
                        for track in self.infra['track_sections']
                        if track['id'] == part['track']
                    )
                    name = track_section['extensions']['sncf']['track_name']
                    if name == 'placeholder_track':
                        name = track_section['id']
                    points.append(Point(
                        id=op['extensions']['identifier']['name'] + f"/{name}",
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
                        else lengths[port['track']]
                    ),
                    type=(
                        'switch'
                        if switch['switch_type'] != 'link'
                        else 'link'
                    )
                ))
        return points

    def train_departure(self, train: int | str) -> Point:
        """Train departure point"""

        if isinstance(train, str):
            train = self.trains.index(train)

        departure = self._head_position(train)[0]
        return Point(
            id=f'departure_{self.trains[train]}',
            track_section=departure['track_section'],
            position=departure['offset'],
            type='departure'
        )

    def train_arrival(self, train: int | str) -> Point:

        if isinstance(train, str):
            train = self.trains.index(train)

        arrival = self._head_position(train)[-1]
        return Point(
            id=f'arrival_{self.trains[train]}',
            track_section=arrival['track_section'],
            position=arrival['offset'],
            type='arrival'
        )

    def _head_position(self, train: int | str, eco_or_base: str = 'base'):

        if isinstance(train, str):
            train = self.trains.index(train)

        group, idx = self._train_schedule_group[
            self.trains[train]
        ]

        sim = f'{eco_or_base}_simulations'
        return self.results[group][sim][idx]['head_positions']

    def points_on_track_sections(self, op_part_tracks: bool = False) -> dict:
        """Dict with for each track, points of interests and their positions"""

        _points = self._points(op_part_tracks=op_part_tracks)
        points_on_track_sections = {}

        for t in self.track_section_lengths:
            points = [
                p for p in _points
                if p.track_section == t
            ]
            points.sort(key=lambda p: p.position)
            points_on_track_sections[t] = points

        return points_on_track_sections

    def offset_in_path_of_train(
        self,
        point: Point,
        train: int | str
    ) -> float | None:

        if isinstance(train, str):
            train = self.trains.index(train)

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
                self.track_section_lengths[
                    self.train_departure(train).track_section
                ]
                - self.train_departure(train).position
            )
        else:
            offset = self.train_departure(train).position

        for id in track_ids[1:idx_pt_tr]:
            offset += self.track_section_lengths[id]

        if tracks[idx_pt_tr]['direction'] == 'START_TO_STOP':
            offset += point.position
        else:
            offset += (
                self.track_section_lengths[point.track_section]
                - point.position
            )
        return offset

    def draw_infra_points(
        self,
        save: str | None = None,
    ) -> JpegImageFile:
        """Use mermaid.js to display the infra as a graph of specific points

        Parameters
        ----------
        save : str | None, optional
            File name to save image, by default None

        Returns
        -------
        PIL.JpegImagePlugin.JpegImageFile
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
    def trains(self) -> list[str]:
        """List of train ids in the simulation"""
        return [
            train['id']
            for group in self.simulation['train_schedule_groups']
            for train in group['schedules']
        ]

    @property
    def departure_times(self) -> list[float]:
        """List of trains departure times"""
        return [
            self._head_position(train)[0]['time']
            for train in self.trains
        ]

    @property
    def last_arrival_times(self) -> list[float]:
        """List of train last arrival times"""
        return [
            self._head_position(train)[-1]['time']
            for train in self.trains
        ]

    @property
    def _train_schedule_group(self) -> dict[str, int]:
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

    def get_point(sim, point_id):
        for point in sim._points():
            if point.id == point_id:
                return point
        return None

    def points_encountered_by_train(
        self,
        train: int | str,
        types: list[str] = [
            'departure',
            'signal',
            'detector',
            'station',
            'switch',
            # 'link',
            'arrival',
        ],
    ) -> list[dict[str, Any]]:
        """Points encountered by a train during its path

        Parameters
        ----------
        types : list[str], optional
            Types of points, all types by default

        Returns
        -------
        list[Dict[str, Any]]
            Points encountered (id, type, offset)
        """

        if isinstance(train, str):
            train = self.trains.index(train)

        train_track_sections_list = self.train_track_sections(train)
        ids = [track['id'] for track in train_track_sections_list]

        points = {
            point.id: point
            for point in (
                [self.train_departure(train)]
                + self._points()
                + [self.train_arrival(train)]
            )
            if (
                point.track_section in ids
                and point.type in types
            )
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
                        return 'BOTH'  # detector['applicable_directions']

        def train_direction(point: Point, train: int | str) -> str:

            if isinstance(train, str):
                train = self.trains.index(train)

            for track in train_track_sections_list:
                if track['id'] == point.track_section:
                    return track['direction']

        list_ = []
        for point in list(points.values()):
            offset = self.offset_in_path_of_train(point, train)
            if (
                (
                    point_direction(point) == train_direction(point, train)
                    or point_direction(point) == 'BOTH'
                )
                and offset is not None
            ):
                list_.append({
                    'id': point.id,
                    'offset': offset,
                    'type': point.type,
                })
        list_.sort(key=lambda point: point['offset'])

        simulations = ['base']
        try:
            self._head_position(train, 'eco')
            simulations += ['eco']
        except TypeError:
            pass

        for eco_or_base in simulations:
            head_position = self._head_position(train, eco_or_base)
            t = [
                record['time']
                for record in head_position
            ]
            path_offset = [
                record['path_offset']
                for record in head_position
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
        
        points_before_arrival = []
        for p in list_:
            points_before_arrival.append(p)
            if p['type'] == 'arrival':
                break
        return points_before_arrival

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
    def _tvds(self) -> list[frozenset[str]]:

        tvds = []
        for route in self.infra['routes']:
            limit_tvds = []
            limit_tvds.append(route['entry_point']['id'])
            for d in route['release_detectors']:
                if d not in [
                    route['entry_point']['id'],
                    route['exit_point']['id']
                ]:
                    limit_tvds.append(d)
            limit_tvds.append(route['exit_point']['id'])
            for tvd in [
                frozenset([limit_tvds[i], limit_tvds[i+1]])
                for i, _ in enumerate(limit_tvds[:-1])
            ]:
                tvds.append(tvd)

        unique_tvds = []
        for tvd in tvds:
            if tvd not in unique_tvds:
                unique_tvds.append((tvd))

        return unique_tvds

    @property
    def tvd_zones(self) -> dict[str, str]:

        _tvds = self._tvds

        dict_tvd_zones = {
            "<->".join(sorted(d)): "<->".join(sorted(d))
            for d in _tvds
        }
        points = self.points_on_track_sections()
        for switch in self.switches:
            detectors = []
            for port in switch['ports'].values():
                idx = 0 if port['endpoint'] == 'BEGIN' else -1
                detectors_on_track = [
                    p.id
                    for p in points[port['track']]
                    if p.type == 'detector'
                ]
                if detectors_on_track:
                    detectors.append(detectors_on_track[idx])

            for a in combinations(detectors, 2):
                if set(a) in _tvds:
                    dict_tvd_zones["<->".join(sorted(a))] = switch['id']

        return dict_tvd_zones

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
            during the train's path and the values are dicts with
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
                zone = self.tvd_zones["<->".join(sorted([start, end]))]

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
                positions[self.tvd_zones[last_zone]] = {
                    'type': 'last_zone',
                    'offset': None,
                }
            stop_positions.append(positions)

        return stop_positions

    def train_routes(self, train, eco_or_base: str = 'base') -> list[str]:
        if isinstance(train, str):
            train = self.trains.index(train)

        group, idx = self._train_schedule_group[
            self.trains[train]
        ]

        sim = f'{eco_or_base}_simulations'

        return [
            route['route']
            for route in self.results[group][sim][idx]['routing_requirements']
        ]

    def route_track_sections(
        self,
        route_id: str
    ) -> list[str]:

        SWITCHES_TRACKS = {
            s['id']: [e['track'] for e in s['ports'].values()]
            for s in self.infra['switches']
        }

        route = next(r for r in self.infra['routes'] if r['id'] == route_id)

        curr_track = next(
            p['track']
            for p in self.infra['detectors'] + self.infra['buffer_stops']
            if p['id'] == route['entry_point']['id']
        )

        if not route['switches_directions']:
            entry_position = next(
                p['position']
                for p in self.infra['detectors'] + self.infra['buffer_stops']
                if p['id'] == route['entry_point']['id']
            )
            exit_position = next(
                p['position']
                for p in self.infra['detectors'] + self.infra['buffer_stops']
                if p['id'] == route['exit_point']['id']
            )
            if entry_position < exit_position:
                direction = 'START_TO_STOP'
            else:
                direction = 'STOP_TO_START'
            return [{'id': curr_track, 'direction': direction}]

        not_visited = set(route['switches_directions'].keys())
        track_sections = []

        while not_visited:
            sw = next(
                switch
                for switch in self.infra['switches']
                if curr_track in SWITCHES_TRACKS[switch['id']]
                and switch['id'] in not_visited
            )
            sw_id = sw['id']
            entry_port = next(
                p
                for p, details in sw['ports'].items()
                if details['track'] == curr_track
            )
            switch_direction = route['switches_directions'][sw_id]
            if not track_sections:
                direction = (
                    'START_TO_STOP'
                    if sw['ports'][entry_port]['endpoint'] == 'END'
                    else 'STOP_TO_START'
                )
                track_sections.append(
                    {'id': curr_track, 'direction': direction}
                )
            exit_port =\
                SWITCH_EXIT[sw['switch_type']][switch_direction][entry_port]
            direction = (
                'START_TO_STOP'
                if sw['ports'][exit_port]['endpoint'] == 'BEGIN'
                else 'STOP_TO_START'
            )
            curr_track = sw['ports'][exit_port]['track']
            track_sections.append({'id': curr_track, 'direction': direction})
            not_visited.remove(sw_id)

        return track_sections

    @lru_cache()
    def train_track_sections(self, train: int | str) -> list[dict[str, str]]:

        if isinstance(train, str):
            train = self.trains.index(train)

        group_id, idx = self._train_schedule_group[
            self.trains[train]
        ]
        group = next(
            gr
            for gr in self.simulation['train_schedule_groups']
            if gr['id'] == group_id
        )
        first_track_id = group['waypoints'][0][0]['track_section']
        last_track_id = group['waypoints'][-1][-1]['track_section']
        list_of_tracks = []
        for route_id in self.train_routes(train):
            for track in self.route_track_sections(route_id):
                if track not in list_of_tracks:
                    list_of_tracks.append(track)
                if track['id'] == last_track_id:
                    break
        first_track = next(
            track
            for track in list_of_tracks
            if track['id']==first_track_id
        )
        return list_of_tracks[list_of_tracks.index(first_track):]

    def path_length(self, train: int | str) -> float:
        return self._head_position(train=train)[-1]['path_offset']

    def get_stops(self, train: int | str) -> float:

        if isinstance(train, str):
            train = self.trains.index(train)

        group, idx = self._train_schedule_group[
            self.trains[train]
        ]

        group_idx = _group_idx(self, group)

        return (
            self.simulation['train_schedule_groups']
            [group_idx]['schedules'][idx]['stops']
        )


def _group_idx(self, group: str) -> int:
    return [
        group['id']
        for group in self.simulation['train_schedule_groups']
    ].index(group)


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
