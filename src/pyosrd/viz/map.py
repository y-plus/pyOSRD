
import distinctipy
import folium
import folium.plugins
import numpy as np

from haversine import haversine

from .result_to_geojson import res2geojson

def folium_map(
    osrd,
    markers: list[str] | None = None,
    fit: bool=True
) -> folium.folium.Map:
    """Infra as a folium map"""

    track_section_names = {
        track['id']: track['extensions']['sncf']['track_name']
        for track in osrd.infra['track_sections']
    }

    TRACK_SECTIONS_COORDINATES = {
        ts['id']: [(point[1], point[0]) for point in ts['geo']['coordinates']]
        for ts in osrd.infra['track_sections']
    }

    track_section_geo_lengths = dict()
    for ts in osrd.infra['track_sections']:
        geo_length = 0
        for i, _ in enumerate(coords:= ts['geo']['coordinates']):
            if i > 0:
                geo_length += round(haversine(
                    coords[i][::-1],
                    coords[i-1][::-1],
                    unit='m'
                ), 2)
        track_section_geo_lengths[ts['id']] = geo_length

    def coords_from_position_on_track(
        track_section: str,
        position: float,
    ) -> list[float]:
        length = osrd.track_section_lengths[track_section]
        pos = position / length
        
        geo_lengths = [0]
        for i, _ in enumerate(coords:=  TRACK_SECTIONS_COORDINATES[track_section]):
            if i > 0:
                geo_lengths.append(
                    round(haversine(
                        coords[i][::-1],
                        coords[i-1][::-1],
                        unit='m'
                    ), 2) + geo_lengths[i-1]
                )
        positions = [length / geo_lengths[-1] for length in geo_lengths]

        lats = [coord[0] for coord in TRACK_SECTIONS_COORDINATES[track_section]]
        lngs = [coord[1] for coord in TRACK_SECTIONS_COORDINATES[track_section]]
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
                operational_point['extensions']['identifier']['name']
                if 'sncf' in operational_point['extensions']
                else ''
            )
            + '/' + operational_point['extensions']['sncf']['ch']
            + '\n' + operational_point['extensions']['sncf']['ch_long_label']
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
        if switch['switch_type'] != 'link'
    }

    m = folium.Map(location=[49.5, -0.4],tiles=None)

    folium.TileLayer("cartodbpositron", name="Positron", attr="blank").add_to(m)
    folium.TileLayer("openstreetmap", name="OpenStreetMap", attr="blank", show=False).add_to(m)
    folium.TileLayer("", name="None", attr="blank", show=False).add_to(m)

    tracks = folium.FeatureGroup(name='Rails')
    for id, line in TRACK_SECTIONS_COORDINATES.items():
        folium.PolyLine(
            line,
            tooltip=track_section_names[id],
            color='black',
            weight=1
        ).add_to(tracks)
    tracks.add_to(m)

    if fit:
        m.fit_bounds(tracks.get_bounds())

    detectors = folium.FeatureGroup('Detectors', show=False)
    for id, position in detector_geo_positions.items():
        folium.Marker(
            position,
            popup=id,
            icon=folium.DivIcon(
                html="""
                    <i class="fas fa-equals fa-rotate-by"
                    style='font-size: 14px; --fa-rotate-angle: -45deg'></i>
                """,
            )
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
            icon=folium.DivIcon(
            html="""
            <i class="fa fa-traffic-light" style='border: 0px solid red; font-size:24px; color: #555'></i><br/>""",
            icon_size=[25, 50],
            # icon_anchor=(20, 0),
            ),
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
            icon=folium.DivIcon(
                """<i class="fas fa-house-user" style='font-size: 24px'></i>""",
                icon_size=[50, 50]
            )
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

    m.add_child(folium.plugins.Fullscreen())

    zones_limits = dict()
    for tvd, zone in osrd.tvd_zones.items():
        if zone not in zones_limits:
            zones_limits[zone] = set()
        for d in tvd.split('<->'):
            zones_limits[zone].add(d)
    colors = distinctipy.get_colors(len(zones_limits))
    colors_iter = (distinctipy.get_hex(c) for c in colors)

    zones = folium.FeatureGroup('Zones', show=False)
    limits_geo_positions = detector_geo_positions | buffer_stop_geo_positions
    for zone, limits in zones_limits.items():
        zone_group = folium.FeatureGroup(zone)
        for d in limits:
            folium.Marker(limits_geo_positions[d]).add_to(zone_group)
        folium.Rectangle(
            zone_group.get_bounds(),
            popup=zone,
            color=next(colors_iter),
            fill=True,
            weight=1,
            name=zone,
        ).add_to(zones)
    zones.add_to(m)

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

    folium.LayerControl().add_to(m)
    
    folium.plugins.MiniMap(
        toggle_display=True,
        zoom_level_offset=-7
    ).add_to(m)

    return m


def folium_results(
    self,
    ref_sim = None,
    eco_or_base: str = 'base',
    period: int = 5,
) -> folium.Map:
    """Results as a folium map"""

    m = folium_map(self)
    data = res2geojson(self, ref_sim=ref_sim, period=period, eco_or_base=eco_or_base)
    folium.plugins.TimestampedGeoJson(
        data=data,
        auto_play=False,
        loop=False,
        period=f'PT{period}S',
        min_speed=1,
        max_speed=12
    ).add_to(m)

    return m
