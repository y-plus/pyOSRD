from datetime import datetime
from typing import Any

import numpy as np

import branca.colormap as cm

from haversine import haversine

from pyosrd.delays_between_simulations import calculate_delay_f_time


def coords_from_position_on_track(
    self,
    track_section: str,
    position: float,
) -> list[float]:
    
    track_section_coordinates = {
        ts['id']: [(point[1], point[0]) for point in ts['geo']['coordinates']]
        for ts in self.infra['track_sections']
    }
    
    track_section_geo_lengths = {
        ts['id']: haversine(
            (
                ts['geo']['coordinates'][0][1],
                ts['geo']['coordinates'][0][0]
            ),
            (
                ts['geo']['coordinates'][-1][1],
                ts['geo']['coordinates'][-1][0]
            ),
            unit='m'
        )
        for ts in self.infra['track_sections']
    }
    length = self.track_section_lengths[track_section]
    pos = position / length
    positions = [
        haversine(
            point, track_section_coordinates[track_section][0], unit='m'
        )
        / track_section_geo_lengths[track_section]
        for point in track_section_coordinates[track_section]
    ]
    lats = [coord[0] for coord in track_section_coordinates[track_section]]
    lngs = [coord[1] for coord in track_section_coordinates[track_section]]
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

        positions = self._head_position(train_index, eco_or_base)
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
                np.interp(times_interp,times,lngs),
                np.interp(times_interp,times,lats)
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
            delays = calculate_delay_f_time(self, ref_sim, train_index, eco_or_base)
            delays_interp = np.interp(times_interp, times, delays)
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