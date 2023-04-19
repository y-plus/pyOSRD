import os
import json

from typing import Tuple, Dict, List

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


def routes(infra: Dict) -> List:
    return [route['id'] for route in infra['routes']]


def route_switches(infra: Dict) -> Dict[str, str]:

    return {
        route['id']: list(route['switches_directions'].keys())[0]
        for route in infra['routes']
        if len(list(route['switches_directions'].keys())) != 0
    }


def route_limits(infra: Dict) -> Dict:
    points = {d['id']: (d['track'], d['position']) for d in infra['detectors']}
    points.update({
        bs['id']: (bs['track'], bs['position']) for bs in infra['buffer_stops']
    })
    return points


def track_section_lengths(infra: Dict) -> Dict:
    return {t['id']: t['length'] for t in infra['track_sections']}


def route_lengths(infra: Dict) -> Dict:

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
