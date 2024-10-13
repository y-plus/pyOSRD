import math
import os

from haversine import inverse_haversine, Direction as GeoDirection

from railjson_generator import (
    InfraBuilder,
)
from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction

from pyosrd.infra.build import build_infra

from pyosrd.use_cases.infras.helpers.builders import (
    extend_track,
    build_terminal_station_3_5
)

def terminal_station_3_5(
    dir: str,
    infra_json: str = 'infra.json',
) -> Infra:
    """

    """

    LENGTH_STATION = 800.
    LENGTH_BLOCK = 1_500.
    DISTANCE_SIGNAL_SWITCH = 50.
    DISTANCE_SIGNAL_DETECTOR = 20.
    LENGTH_ELBOW = 20
    ANGLE_ELBOW = math.pi/16

    line_name = 'L1'
    line_code = 1

    infra_builder = InfraBuilder()

    # Station 3-5-terminus

    t1bis = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V1bis',
        line_name=line_name,
        line_code=line_code,
        length=None,
    )

    t1 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V1',
        line_name=line_name,
        line_code=line_code,
        length=None,
    )

    t2 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V2',
        line_name=line_name,
        line_code=line_code,
        length=None,
    )
    t1bis.add_buffer_stop(0, label='bs.1bis')
    t1.add_buffer_stop(0, label='bs.1')
    t2.add_buffer_stop(0, label='bs.2')

    t1bis.coordinates[0] = (0.2, 45.575)
    t1.coordinates[0] = (0.20005, 45.575)
    t2.coordinates[0] = (0.2001, 45.575)
    geo_direction=GeoDirection.SOUTH

    build_terminal_station_3_5(
        infra_builder,
        track_in = t2,
        track_inout = t1,
        track_out = t1bis,
        station_name = 'D',
        geo_direction=geo_direction
    )

    ## Build and save
    os.makedirs(dir, exist_ok=True)
    built_infra = build_infra(infra_builder)
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra

