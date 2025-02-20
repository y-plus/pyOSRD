import math
import os

from haversine import inverse_haversine, haversine, Direction as GeoDirection

from railjson_generator import (
    InfraBuilder,
)
from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction

from pyosrd.infra.build import build_infra

from pyosrd.use_cases.infras.helpers.builders import (
    build_blocks,
    build_station_1_2,
    build_terminal_station_1_2,
    extend_track,
)

def voie_unique(
    dir: str,
    infra_json: str = 'infra.json',
    num_stations: int = 3,
    num_blocks_between_stations: int = 5,
) -> Infra:
    """

    """  # noqa

    infra_builder = InfraBuilder()

    # Ligne A->...
    line_name="A"+"-"+chr(ord('A')+num_stations-1)
    line_code=1_000

    track1 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='VU',
        line_name=line_name,
        line_code=line_code,
        length=None,
    )

    BEGIN = (45.575988410701974, 0.21)
    track1.coordinates[0] = tuple(BEGIN[::-1])
    extend_track(track1, 1, geo_direction=GeoDirection.EAST)

    
    track0 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='VU',
        line_name=line_name,
        line_code=line_code,
        length=None,
    )
    infra_builder.add_link(
        track0.begin(),
        track1.begin()
    )
    track0.coordinates[0] = tuple(BEGIN[::-1])
    extend_track(track0, 1, geo_direction=GeoDirection.WEST)

    build_terminal_station_1_2(
        infra_builder=infra_builder,
        track_in=track0,
        station_name='A',
        track_names=['V2', 'V1'],
        geo_direction=GeoDirection.WEST
    )

    build_blocks(
        track1,
        num_blocks=num_blocks_between_stations,
        forward=True,
        backward=True,
    )
    
    for station in range(2,num_stations):
        track1 = build_station_1_2(
            infra_builder=infra_builder,
            track_in=track1,
            station_name=chr(ord('A')+station-1),
            forward=True,
            backward=True,
            track_names=['V2', 'V1']
        )
        build_blocks(
            track1,
            num_blocks=num_blocks_between_stations,
            forward=True,
            backward=True,
        )

    build_terminal_station_1_2(
        infra_builder=infra_builder,
        track_in=track1,
        station_name=chr(ord('A')+num_stations-1),
        track_names=['V2', 'V1']
    )



    ## Build and save

    os.makedirs(dir, exist_ok=True)

    built_infra = build_infra(
        infra_builder,
    )
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra

