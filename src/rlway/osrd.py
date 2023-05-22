import os
import json
from dataclasses import dataclass
from typing import Dict, List, Union, Tuple, Any

import base64
from IPython.display import Image, display
import networkx as nx


def _read_json(json_file: str) -> Union[Dict, List]:
    with open(json_file, 'r') as f:
        dict_ = json.load(f)
    return dict_


@dataclass
class OSRD():
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

        if self.infra == {} or self.simulation == {}:
            raise ValueError("Missing json file to run OSRD")

        # Run the simulation after reading the path in a file ?

        self.results = _read_json(os.path.join(self.dir, self.results_json))

    @property
    def has_results(self) -> bool:
        return self.results != []

    @property
    def routes(self) -> List[str]:
        """List of routes ids"""
        return [route['id'] for route in self.infra['routes']]

    @property
    def route_switches(self) -> Dict[str, str]:

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
        Keys are points labels, values are tuples (associated track, position)
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
        """Points of interest are stations and switches"""
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
        """List of signal labels at convergences entries"""
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
        """For each track, points of interests and their positions"""

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
        remove_bufferstop_to_bufferstop: bool = True,
    ) -> None:
        """Use mermaid.js to display the infra as a DAG with detectors as nodes"""

        def mm(graph):
            graphbytes = graph.encode("ascii")
            base64_bytes = base64.b64encode(graphbytes)
            base64_string = base64_bytes.decode("ascii")
            display(Image(url="https://mermaid.ink/img/" + base64_string))

        displayed_routes = [
            route
            for route in self.routes
            if not (('rt.buffer' in route) and ('->buffer' in route))
        ] if remove_bufferstop_to_bufferstop else self.routes

        g = "graph LR;"+";".join([
            route.replace('rt.', '').replace('->', '-->')
            for route in displayed_routes
        ])
        mm(g)

    @property
    def num_trains(self) -> int:
        """Number of trains in the simulation"""
        return len(self.simulation['train_schedules'])

    @property
    def trains(self) -> List[str]:
        """List of train ids in the simulation"""
        return [train['id'] for train in self.simulation['train_schedules']]

    @property
    def departure_times(self) -> List[float]:
        return [
            train_schedule['departure_time']
            for train_schedule in self.simulation['train_schedules']
        ]
