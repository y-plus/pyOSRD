
import folium
import folium.plugins
import numpy as np

from haversine import haversine


def folium_map(
    osrd,
    markers: list[str] | None = None
) -> folium.folium.Map:
    """Infra as a folium map"""

    track_section_names = {
        track['id']: track['extensions']['sncf']['track_name']
        for track in osrd.infra['track_sections']
    }

    track_section_coordinates = {
        ts['id']: [(point[1], point[0]) for point in ts['geo']['coordinates']]
        for ts in osrd.infra['track_sections']
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
        for ts in osrd.infra['track_sections']
    }

    def coords_from_position_on_track(
        track_section: str,
        position: float,
    ) -> list[float]:
        length = osrd.track_section_lengths[track_section]
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

    detector_geo_positions = {
        detector['id']: coords_from_position_on_track(
            detector['track'],
            detector['position']
        )
        for detector in osrd.infra['detectors']
    }

    buffer_stop_geo_positions = {
        buffer_stop['id']: coords_from_position_on_track(
            buffer_stop['track'],
            buffer_stop['position']
        )
        for buffer_stop in osrd.infra['buffer_stops']
    }

    signal_geo_positions = {
        signal['id']: coords_from_position_on_track(
            signal['track'],
            signal['position']
        )
        for signal in osrd.infra['signals']
    }

    operational_point_names = {
        (operational_point['id'], part['track']): (
            (
                operational_point['extensions']['sncf']['ch_long_label']
                if 'sncf' in operational_point['extensions']
                else ''
            )
            + ' ' + operational_point['extensions']['identifier']['name']
            + ' ' + track_section_names[part['track']]
        )
        for operational_point in osrd.infra['operational_points']
        for part in operational_point['parts']
    }

    operational_point_geo_positions = {
        (operational_point['id'], part['track']):
            coords_from_position_on_track(
                part['track'],
                part['position']
            )
        for operational_point in osrd.infra['operational_points']
        for part in operational_point['parts']
    }

    platform_names = {
        (operational_point['id'], part['track']): (
            (
                operational_point['extensions']['sncf']['ch_long_label']
                if 'sncf' in operational_point['extensions']
                else ''
            )
            + ' ' + operational_point['extensions']['identifier']['name']
            + ' ' + track_section_names[part['track']]
        )
        for operational_point in osrd.infra['operational_points']
        for part in operational_point['parts']
        if operational_point['extensions']['sncf']['ch'] in ['BV', '00']
    }

    platform_geo_positions = {
        (operational_point['id'], part['track']):
            coords_from_position_on_track(
                part['track'],
                part['position']
            )
        for operational_point in osrd.infra['operational_points']
        for part in operational_point['parts']
        if operational_point['extensions']['sncf']['ch'] in ['BV', '00']
    }

    switch_geo_positions = {
        switch['id']: coords_from_position_on_track(
            switch['ports'][list(switch['ports'].keys())[0]]['track'],
            0
            if (
                switch['ports'][list(switch['ports'].keys())[0]]['endpoint']
                == 'BEGIN'
            )
            else osrd.track_section_lengths[
                switch['ports'][list(switch['ports'].keys())[0]]['track']
            ]
        )
        for switch in osrd.infra['switches']
    }

    m = folium.Map(location=[49.5, -0.4])

    tracks = folium.FeatureGroup(name='Rails')
    for id, line in track_section_coordinates.items():
        folium.PolyLine(
            line,
            tooltip=track_section_names[id],
            color='black'
        ).add_to(tracks)
    tracks.add_to(m)

    m.fit_bounds(tracks.get_bounds())

    detectors = folium.FeatureGroup('Detectors', show=False)
    for id, position in detector_geo_positions.items():
        folium.Marker(
            position,
            popup=id,
            icon=folium.DivIcon(html="""
            <div><svg>
                <rect x="-5" y="-5" width="20"
                height="20", fill="green", opacity=".8" />
            </svg></div>"""),
            ).add_to(detectors)
    detectors.add_to(m)

    buffer_stops = folium.FeatureGroup('Buffer Stops', show=False)
    for id, position in buffer_stop_geo_positions.items():
        folium.Marker(
            position,
            popup=id,
            icon=folium.DivIcon(html="""
            <div><svg>
                <rect x="-5" y="-5" width="20"
                height="20", fill="black", opacity=".8" />
            </svg></div>"""),
            ).add_to(buffer_stops)
    buffer_stops.add_to(m)

    signals = folium.FeatureGroup('Signals', show=False)
    for id, position in signal_geo_positions.items():
        folium.Marker(
            position,
            popup=id,
            icon=folium.DivIcon(html="""
            <div><svg>
                <circle cx="5" cy="5" r="5", fill="red", opacity=".8" />
            </svg></div>"""),
            ).add_to(signals)
    signals.add_to(m)

    operational_points = folium.FeatureGroup('Operational Points', show=False)
    for id, position in operational_point_geo_positions.items():
        folium.Marker(
            position,
            popup=operational_point_names[id],
            icon=folium.DivIcon(html="""
            <div><svg>
                <circle cx="5" cy="5" r="5", fill="cyan", opacity=".9" />
            </svg></div>"""),
            ).add_to(operational_points)
    operational_points.add_to(m)

    platforms = folium.FeatureGroup('Stations', show=False)
    for id, position in platform_geo_positions.items():
        folium.Marker(
            position,
            popup=platform_names[id],
            icon=folium.DivIcon(html="""
            <div><svg>
                <rect x="-5" y="-5" width="20"
                height="20", fill="grey", opacity=".8" />
            </svg></div>"""),
            ).add_to(platforms)
    platforms.add_to(m)

    switches = folium.FeatureGroup('Switches', show=False)
    for id, position in switch_geo_positions.items():
        folium.Marker(
            position,
            popup=id,
            icon=folium.DivIcon(html="""
            <div><svg>
                <circle cx="5" cy="5" r="5", fill="black", opacity=".8" />
            </svg></div>"""),
            ).add_to(switches)
    switches.add_to(m)

    folium.LayerControl().add_to(m)

    m.add_child(folium.plugins.Fullscreen())

    if markers:
        for marker in markers:
            for positions in [
                buffer_stop_geo_positions,
                detector_geo_positions,
                signal_geo_positions,
                switch_geo_positions,
            ]:
                if marker in positions:
                    m.add_child(folium.Marker(positions[marker]))

    return m
