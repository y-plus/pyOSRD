import os
import json
from dataclasses import dataclass
from typing import Dict, List, Union, Tuple, Any

import base64
from IPython.display import Image, display

from dotenv import load_dotenv
import networkx as nx
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.axes._axes import Axes


def _read_json(json_file: str) -> Union[Dict, List]:
    with open(json_file, 'r') as f:
        dict_ = json.load(f)
    return dict_


@dataclass
class OSRD():
    """Class with methods to run OSRD simulations and read infra and results

    Parameters
    ----------
    dir: str, optionnal
        Directory path, by default current directory
    infra_json: str, optionnal
        Name of the file containing the infrastructure in rail_json format.
        If the file does not exist, attribute infra will be empty,
        by default 'infra.json'
    simulation_json: str, optionnal
        Name of the file containing the simulation parameters.
        If the file does not exist, attribute simulation will be empty,
        by default 'simulation.json'
    results_json: str, optionnal
        Name of the file containing the simulation results.
        If the file does not exist, attribute results will be empty,
        by default 'results.json'
    """
    dir: str = '.'
    infra_json: str = 'infra.json'
    simulation_json: str = 'simulation.json'
    results_json: str = 'results.json'

    def __post_init__(self):

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
        os.system(
            f"java -jar {os.getenv('OSRD_PATH')}/core/build/libs/osrd-all.jar "
            f"standalone-simulation --infra_path {self.infra_json} "
            f"--sim_path {self.simulation_json} --res_path {self.results_json}"
        )

        self.results = _read_json(os.path.join(self.dir, self.results_json))

    @property
    def has_results(self) -> bool:
        """True if the object has simulation results"""
        return self.results != []

    @property
    def routes(self) -> List[str]:
        """List of routes labels"""
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

        >>> {'point_label' : ('track_id', position: float), ...}

        Returns
        -------
        Dict[str, Tuple[str, float]]
            Keys are points labels,
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

        ts = nx.Graph()

        for t in self.infra['track_section_links']:
            ts.add_edge(t['src']['track'], t['dst']['track'])
        lengths = {}
        points = self.route_limits
        for route in self.routes:
            start = route.replace('rt.', '').split('->')[0]
            end = route.replace('rt.', '').split('->')[1]
            tracks = nx.shortest_path(ts, points[start][0], points[end][0])
            if len(tracks) == 1:
                lengths[route] = points[end][1] - points[start][1]
            else:
                lengths[route] = (
                    self.track_section_lengths[tracks[0]]
                    - points[start][1]
                )
                for t in tracks[1:-1]:
                    lengths[route] += self.track_section_lengths[t]
                lengths[route] += points[end][1]
        return lengths

    @property
    def num_switches(self) -> int:
        """Number of switches"""
        return len(self.infra['switches'])

    @property
    def points_of_interest(self) -> Dict[str, Any]:
        """Dict of points of interest (stations and switches)"""
        return {
            point['id']: point
            for point in (
                self.infra['switches']
                + self.infra['operational_points']
            )
        }

    @property
    def station_capacities(self) -> Dict[str, int]:
        """Dict of stations labels (operational points) and their capacities"""
        return {
            station['id']: len(station['parts'])
            for station in self.infra['operational_points']
        }

    @property
    def num_stations(self) -> int:
        """Number of stations (defined as operational points)"""
        return len(self.station_capacities)

    @property
    def convergence_entry_signals(self) -> List[str]:
        """List of signal labels located at convergences entries"""
        G = nx.DiGraph()
        G.add_edges_from([
            (
                route['id'].replace('rt.', '').split('->')[0],
                route['id'].replace('rt.', '').split('->')[1],
            )
            for route in self.infra['routes']
        ])

        convergence_entry_detectors = []
        for node in G:
            if len(list(G.predecessors(node))) > 1:
                convergence_entry_detectors += list(G.predecessors(node))

        return [
            s['id']
            for d in convergence_entry_detectors
            for s in self.infra['signals'] if s['linked_detector'] == d
        ]

    @property
    def points_on_track_sections(self) -> Dict:
        """Dict with for each track, points of interests and their positions"""

        points = {
            track['id']: {
                # track['id']+"_BEGIN": (0, 'begin'),
                # track['id']+"_END": (track["length"], 'end'),
            }
            for track in self.infra['track_sections']
        }

        for detector in self.infra['detectors']:
            track = detector['track']
            id = detector['id']
            points[track][id] = (detector['position'], 'detector')

        for signal in self.infra['signals']:
            track = signal['track']
            id = signal['id']
            tag = (
                'cvg_signal'
                if id in self.convergence_entry_signals
                else 'signal'
            )
            points[track][id] = (signal['position'], tag)

        for station in self.infra['operational_points']:
            id = station['id']
            for part in station['parts']:
                track = part['track']
                points[track][id] = (part['position'], 'station')

        # sort points by position for each track
        for track in points:
            points[track] = {
                k: v for k, v in sorted(
                    points[track].items(),
                    key=lambda item: item[1]
                )
            }

        return points

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
    def num_trains(self) -> int:
        """Number of trains in the simulation"""
        return len(self.simulation['train_schedules'])

    @property
    def trains(self) -> List[str]:
        """List of train labels in the simulation"""
        return [train['id'] for train in self.simulation['train_schedules']]

    @property
    def departure_times(self) -> List[float]:
        """List of trains departure times"""
        return [
            train_schedule['departure_time']
            for train_schedule in self.simulation['train_schedules']
        ]

    def train_track_sections(self, train: int) -> List[str]:
        """List of tracks for a given train trajectory"""

        head_positions = \
            self.results[train]['base_simulations'][0]['head_positions']
        return list(
            dict.fromkeys([
                time["track_section"]
                for time in head_positions
            ]))

    def points_encountered_by_train(
        self,
        train: int,
        types: List[str] = [
            'signal',
            'detector',
            'cvg_signal',
            'station',
        ]
    ) -> List[Tuple[str, str, float, float, float]]:
        """Points encountered by a train during its trajectory

        Parameters
        ----------
        infra : Dict
        result : Dict
        train : int
        types : List[str], optional
            Types of points, by default
            ['signal', 'detector', 'cvg_signal', 'station']
        Returns
        -------
        List[Tuple[str, str, float, float, float]]
            Points encountered (label, type, offset, t_min, t)
        """

        lengths = [
            self.track_section_lengths[ts]
            for ts in self.train_track_sections(train)
        ]

        track_offsets = [
            sum(lengths[: i]) for i, _ in enumerate(lengths)
        ]

        records_min = \
            self.results[train]['base_simulations'][0]['head_positions']
        offset = records_min[0]['offset']
        offsets_min = [offset + t['path_offset'] for t in records_min]
        t_min = [t['time'] for t in records_min]

        records_eco = \
            self.results[train]['eco_simulations'][0]['head_positions']
        offsets_eco = [offset + t['path_offset'] for t in records_eco]
        t = [t['time'] for t in records_eco]

        points = []
        for i, ts in enumerate(self.train_track_sections(train)):
            points += [{
                'id': pt,
                'type': tag,
                'offset': pos + track_offsets[i],
                't_min': np.interp(
                    [pos + track_offsets[i]],
                    offsets_min,
                    t_min
                ).item(),
                't': np.interp([pos+track_offsets[i]], offsets_eco, t).item(),
                }
                for pt, (pos, tag) in self.points_on_track_sections[ts].items()
                if tag in types
            ]

        return points

    def space_time_graph(
        self,
        train: int,
        eco_or_base: str = 'eco',
        types_to_show: List[str] = ['station', 'cvg_signal'],
    ) -> Axes:
        """Draw space-time graph for a given train

        >>> ax = sim.space_time_graph(train=0, ...)

        Parameters
        ----------
        train : int
            Train index
        eco_or_base : str, optional
            Draw eco or base simulation ?, by default 'eco'
        types_to_show : List[str], optional
            List of points types shown on y-axis.
            Possible choices are 'signal', 'detector', 'cvg_signal', 'station'.
            by default ['station', 'cvg_signal']

        Returns
        -------
        Axes
            Matplotlib axe object
        """
        _, ax = plt.subplots()

        points = self.points_encountered_by_train(
            train,
            types_to_show
        )

        simulation = eco_or_base+'_simulations'
        records_min = \
            self.results[train][simulation][0]['head_positions']
        offset = records_min[0]['offset']
        offsets = [offset + t['path_offset'] for t in records_min]
        times = [t['time']/60 for t in records_min]

        ax.plot(
            times,
            offsets,
        )
        for point in points:
            ax.axhline(point['offset'], color='k', linestyle=':');  # noqa

        ax.set_yticks(
            [point['offset'] for point in points],
            [point['id'] for point in points]
        );  # noqa

        ax.set_title(
            self.trains[train]
            + f" ({eco_or_base})"
        );  # noqa

        return ax
