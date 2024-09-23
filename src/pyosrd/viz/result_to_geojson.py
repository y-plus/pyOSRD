import copy
from datetime import datetime
from typing import Any

import numpy as np

import branca.colormap as cm

from haversine import haversine

from pyosrd.osrd import Point
from pyosrd.delays_between_simulations import calculate_delay_f_time


def coords_from_position_on_track(
    self,
    track_section_id: str,
    position: float,
) -> list[float]:
    
    track_section = next(
        t for t in self.infra['track_sections']
        if t['id'] == track_section_id
    )

    coordinates = [
        (point[1], point[0])
        for point in track_section['geo']['coordinates']
    ]
    geo_length = haversine(
            (
                track_section['geo']['coordinates'][0][1],
                track_section['geo']['coordinates'][0][0]
            ),
            (
                track_section['geo']['coordinates'][-1][1],
                track_section['geo']['coordinates'][-1][0]
            ),
            unit='m'
        )

    pos = position / track_section['length']
    positions = [
        haversine(
            point, coordinates[0], unit='m'
        )
        / geo_length
        for point in coordinates
    ]

    lats = [coord[0] for coord in coordinates]
    lngs = [coord[1] for coord in coordinates]

    return [
        np.interp([pos], positions, lats).item(),
        np.interp([pos], positions, lngs).item(),
    ]


def res2geojson(
    self,
    ref_sim = None,
    eco_or_base: str = 'base',
    period: int = 5
) -> dict[str, Any]:

    features = []

    for train_index, _ in enumerate(self.trains):

        coords, times = [], []
        today = datetime.combine(datetime.today(), datetime.min.time())
        today_timestamp = today.timestamp() * 1_000

        positions = copy.deepcopy(
            self._head_position(train_index, eco_or_base)
        )
        
        for p in self.points_encountered_by_train(train_index):
            if p ['type'] == 'switch':
                detector = next(
                    s for s in self.infra['switches']
                    if s['id'] == p['id']
                )
                port_key = next(p for p in detector['ports'])
                port = detector['ports'][port_key]
                position = 0 if port['endpoint'] == 'BEGIN' else self.track_section_lengths[port['track']]
                positions.append({
                    'offset': position,
                    'track_section': port['track'],
                    'path_offset': p['offset'],
                    'time': p['t_'+eco_or_base]
                })
        
        positions.sort(key=lambda x: x['path_offset'])

        for p in positions:
            coords.append(coords_from_position_on_track(
                self,
                p['track_section'],
                p['offset']
            ))
            times.append(today_timestamp + 1_000 * p['time'])

        duration = positions[-1]['time'] - positions[0]['time']
        times_interp = np.linspace(min(times), max(times), int(duration/period))
        lats = [c[1] for c in coords]
        lngs = [c[0] for c in coords]
        coords_interp = list(
            zip(
                np.interp(times_interp, times, lngs),
                np.interp(times_interp, times, lats)
            )
        )
        coords_interp[-1] = (None, None)
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [(c[1], c[0]) for c in coords_interp]
                    },
                "properties": {
                    "times": list(times_interp),
                    "icon": "circle",
                    "iconstyle": {
                        "fillColor": "black",
                        "fillOpacity": 0.9,
                        "stroke": "false",
                        "radius": 3,
                    },
                    "style": {"weight": 0},
                },
            },
        )

        if ref_sim is not None:
            times_orig = [
                today_timestamp + 1_000 * r['time']
                for r in self._head_position(train_index, eco_or_base)
            ]
            delays = calculate_delay_f_time(self, ref_sim, train_index, eco_or_base)
            delays_interp = np.interp(times_interp, times_orig, delays)
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            (c[1], c[0])
                            for i, c in enumerate(coords_interp)
                            if delays_interp[i] > 0
                        ][:-1] + [(None, None)]
                        },
                    "properties": {
                        "times": [
                            t
                            for i, t in enumerate(times_interp)
                            if delays_interp[i] > 0 
                        ],
                        "icon": "circle",
                        "iconstyle": {
                            "fillColor": 'red',
                            "fillOpacity":.5,
                            "stroke": "false",
                            "radius": 12,
                        },
                        "style": {"weight": 0},
                    },
                },
            )
        
    positions = {
        "type": "FeatureCollection",
        "features": features
    }


    return positions