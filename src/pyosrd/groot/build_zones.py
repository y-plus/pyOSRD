import base64
import os
import requests
import shutil

import PIL

from PIL.JpegImagePlugin import JpegImageFile

import networkx as nx

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

def switches_and_detectors_on_route(self, route_id: str):

    route = next(r for r in self.infra['routes'] if r['id'] == route_id)
    
    curr_track = next(
        p['track']
        for p in self.infra['detectors'] + self.infra['buffer_stops']
        if p['id'] == route['entry_point']['id']
    )

    SWITCHES_TRACKS = {
        s['id']: [e['track'] for e in s['ports'].values()]
        for s in self.infra['switches']
    }

    not_visited = set(route['switches_directions'].keys())
    track_sections = []
    elements = []

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

            release_detectors = [
                detector | {'type': 'detector'}
                for detector in self.infra['detectors'] 
                if detector['id'] in route['release_detectors']
                and detector['track'] == curr_track
            ]
            release_detectors.sort(key=lambda d: d['position'])
            if direction == 'STOP_TO_START':
                release_detectors = release_detectors[::-1]
            elements += release_detectors
        exit_port =\
            SWITCH_EXIT[sw['switch_type']][switch_direction][entry_port]
        direction = (
            'START_TO_STOP'
            if sw['ports'][exit_port]['endpoint'] == 'BEGIN'
            else 'STOP_TO_START'
        )
        elements.append({
            'id': sw_id,
            'entry_port': entry_port,
            'exit_port': exit_port,
            'type': sw['switch_type']
        })
        curr_track = sw['ports'][exit_port]['track']
        track_sections.append({'id': curr_track, 'direction': direction})
        release_detectors = [
            detector | {'type': 'detector'}
            for detector in self.infra['detectors'] 
            if detector['id'] in route['release_detectors']
            and detector['track'] == curr_track
        ]
        release_detectors.sort(key=lambda d: d['position'])
        if direction == 'STOP_TO_START':
            release_detectors = release_detectors[::-1]
        elements += release_detectors
        not_visited.remove(sw_id)

    return elements

def diverging_release_detectors_in_route(self, route_id: str) -> set[str]:
    elements = switches_and_detectors_on_route(self, route_id)
    zone_delimiters = set()
    for idx, element in enumerate(elements[:-1]):
        if (
            element['type']=='double_slip_switch'
            or
            element['type']=='point_switch' and element['entry_port']=='A'
        ):
            zone_delimiters.add(elements[idx+1]['id'])
    return zone_delimiters


def build_zones(self, merge: bool = False):

    points = self.points_on_track_sections()

    def route_elements(self, route_id):

        switches_ids = [s['id'] for s in self.switches]   
        route = next(r for r in self.infra['routes'] if r['id']==route_id)
        previous = ''
        elements = []
        for t in self.route_track_sections(route_id):
            for p in (points[t['id']] if t['direction']=='START_TO_STOP' else points[t['id']][::-1]):
                if p.id in (
                    route['release_detectors']
                    + [route['entry_point']['id'], route['exit_point']['id']]
                    + [ s for s in route ['switches_directions'] if s in switches_ids]
                ) and previous != p.id:

                    elements.append(p.id)
                    previous = p.id
        return elements


    tvd_zones = dict()
    diverging_release_detectors = set()

    for route in self.infra['routes']:
        diverging_release_detectors = diverging_release_detectors.union(
            diverging_release_detectors_in_route(self, route['id'])
        )

    exit_points = set(
        route['exit_point']['id']
        for route in self.infra['routes']
    ).union(diverging_release_detectors)

    for route in self.infra['routes']:
        entry_point_id = route['entry_point']['id']
        entry_point_type = route['entry_point']['type']
        exit_point_type = route['exit_point']['type']
        elements = route_elements(self, route['id'])
        if (entry_point_type==exit_point_type=='BufferStop'):
            continue
        for d in route['release_detectors']+[route['exit_point']['id']]:
            if d in exit_points:
                if merge:
                    tvd_zones[f"{entry_point_id}->{d}"] = False if set(
                        elements[elements.index(entry_point_id)+1:elements.index(d)]
                    ) else True
                else:
                    tvd_zones[f"{entry_point_id}->{d}"] = (
                        elements[elements.index(entry_point_id)+1]
                        if set(elements[elements.index(entry_point_id)+1:elements.index(d)])
                        else "<->".join(sorted([entry_point_id, d]))
                    )

                entry_point_id = d

    if merge:
        # merge switch zones
        merge_with = dict()
        for tvd, v in tvd_zones.items():
            if v:
                tvd_zones[tvd] = "<->".join(sorted(tvd.split("->")))
            else:
                for other_tvd, other_v in tvd_zones.items():
                    if not other_v:
                        if set(tvd.split('->')).intersection(set(other_tvd.split('->'))):
                            if tvd not in merge_with:
                                merge_with[tvd] = set()
                            merge_with[tvd].add(other_tvd)

        merge_zones = []
        for value in merge_with.values():
            if value not in merge_zones:
                merge_zones.append(value)

        merges = nx.Graph()
        for tvd, with_ in merge_with.items():
            for other_tvd in with_:
                merges.add_edge(tvd, other_tvd)

        for i, sub in enumerate(nx.connected_components(merges)):
            for tvd in sub:
                tvd_zones[tvd] = f'switch_zone.{i}'

    # stations
    g = nx.Graph()
    for _, points_on_track in points.items():
        for i, _ in enumerate(points_on_track[:-1]):
            g.add_edge(
                f"{points_on_track[i].id}",
                f"{points_on_track[i+1].id}"
            )

    stations = []
    for tvd, zone in tvd_zones.items():
        if '<->' in zone:
            for p in nx.shortest_path(g, *zone.split(("<->"))):
                if '/' in p:
                    tvd_zones[tvd] = p
                    stations.append(p)

    return tvd_zones, stations


def zones_graph(zones) -> nx.Graph:

    zones_graph = nx.DiGraph()

    for tvd, zone in zones.items():
        for other_tvd, other_zone in zones.items():
            if tvd != other_tvd:
                if tvd.split('->')[1] == other_tvd.split('->')[0]:
                    if zone != other_zone:
                        zones_graph.add_edge(
                            zone,
                            other_zone,
                            detector=tvd.split('->')[1]
                        )

    return zones_graph


def draw_graph_zones(
    self,
    save: str | None = None,
) -> JpegImageFile:

    graph = zones_graph(self)
    g = 'graph LR;'

    for e in graph.edges:
        g += f"{e[0].replace('<->', '-')}-->{e[1].replace('<->', '-')};"

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