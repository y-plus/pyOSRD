import os
import json

from typing import Tuple, Dict, List, Any

import base64
from IPython.display import Image, display
import networkx as nx


def read_json(file: str) -> Dict:
    with open(file, 'r') as f:
        dict_ = json.load(f)
    return dict_


def read_jsons_in_dir(directory: str) -> Tuple[Dict, Dict, List]:

    return (
        read_json(os.path.join(directory, file+'.json'))
        for file in ['infra', 'simulation', 'results']
    )


def routes(infra: Dict) -> List[str]:
    """List of routes ids"""
    return [route['id'] for route in infra['routes']]


def route_switches(infra: Dict) -> Dict[str, str]:

    return {
        route['id']: list(route['switches_directions'].keys())[0]
        for route in infra['routes']
        if len(list(route['switches_directions'].keys())) != 0
    }


def route_limits(infra: Dict) -> Dict[str, Tuple[str, float]]:
    """Dict of routes limiting points (detectors and buffer stops)

    >>> {'point_label' : ('track_id', position: float), ...}

    Returns
    -------
    Dict[str, Tuple[str, float]]
      Keys are points labels, values are tuples (associated track, position)
    """

    points_dict = {
        d['id']: (d['track'], d['position']) for d in infra['detectors']
    }
    points_dict.update({
        bs['id']: (bs['track'], bs['position']) for bs in infra['buffer_stops']
    })
    return points_dict


def track_section_lengths(infra: Dict) -> Dict[str, float]:
    """Dict of track sections and their lengths"""
    return {t['id']: t['length'] for t in infra['track_sections']}


def route_lengths(infra: Dict) -> Dict[str, float]:
    """Dict of routes and their lengths"""

    ts = nx.Graph()

    for t in infra['track_section_links']:
        ts.add_edge(t['src']['track'], t['dst']['track'])
    lengths = {}
    points = route_limits(infra)
    for route in routes(infra):
        start = route.replace('rt.', '').split('->')[0]
        end = route.replace('rt.', '').split('->')[1]
        tracks = nx.shortest_path(ts, points[start][0], points[end][0])
        if len(tracks) == 1:
            lengths[route] = points[end][1] - points[start][1]
        else:
            lengths[route] = (
                track_section_lengths(infra)[tracks[0]]
                - points[start][1]
            )
            for t in tracks[1:-1]:
                lengths[route] += track_section_lengths(infra)[t]
            lengths[route] += points[end][1]
    return lengths


def num_switches(infra: Dict) -> int:
    """Number of switches"""
    return len(infra['switches'])


def points_of_interest(infra: Dict) -> Dict[str, Any]:
    """Points of interest are stations and switches"""
    return {
        point['id']: point
        for point in infra['switches'] + infra['operational_points']
    }


def station_capacities(infra: Dict) -> Dict[str, int]:
    """Dict of stations labels (operational points) and their capacities"""
    return {
        station['id']: len(station['parts'])
        for station in infra['operational_points']
    }


def num_stations(infra: Dict) -> int:
    """Number of stations (defined as operational points)"""
    return len(station_capacities(infra))


def convergence_entry_signals(infra: Dict) -> List[str]:
    """List of signal labels at convergences entries"""
    G = nx.DiGraph()
    G.add_edges_from([
        (
            route['id'].replace('rt.', '').split('->')[0],
            route['id'].replace('rt.', '').split('->')[1],
        )
        for route in infra['routes']
    ])

    convergence_entry_detectors = []
    for node in G:
        if len(list(G.predecessors(node))) > 1:
            convergence_entry_detectors += list(G.predecessors(node))

    return [
        s['id']
        for d in convergence_entry_detectors
        for s in infra['signals'] if s['linked_detector'] == d
    ]


def points_on_track_sections(infra: Dict) -> Dict:
    """For each track, points of interests and their positions"""

    points = {
        track['id']: {
            # track['id']+"_BEGIN": (0, 'begin'),
            # track['id']+"_END": (track["length"], 'end'),
        }
        for track in infra['track_sections']
    }

    for detector in infra['detectors']:
        track = detector['track']
        id = detector['id']
        points[track][id] = (detector['position'], 'detector')

    for signal in infra['signals']:
        track = signal['track']
        id = signal['id']
        tag = (
            'cvg_signal'
            if id in convergence_entry_signals(infra)
            else 'signal'
        )
        points[track][id] = (signal['position'], tag)

    for station in infra['operational_points']:
        id = station['id']
        for part in station['parts']:
            track = part['track']
            points[track][id] = (part['position'], 'station')

    for track in points:
        points[track] = {
            k: v for k, v in sorted(
                points[track].items(),
                key=lambda item: item[1]
            )
        }

    return points


def draw_infra(
    infra: Dict,
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
        for route in routes(infra)
        if not (('rt.buffer' in route) and ('->buffer' in route))
    ] if remove_bufferstop_to_bufferstop else routes(infra)

    g = "graph LR;"+";".join([
        route.replace('rt.', '').replace('->', '-->')
        for route in displayed_routes
    ])
    mm(g)
