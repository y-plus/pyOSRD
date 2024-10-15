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
    build_blocks,
    extend_track,
    build_station_3_5
)

def station_3_5(
    dir: str,
    infra_json: str = 'infra.json',
) -> Infra:
    """
    
    """ 
    line_name = 'L1'
    line_code = 1

    infra_builder = InfraBuilder()

    # Station 3-5

    t2 = infra_builder.add_track_section(
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


    t1bis = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V2',
        line_name=line_name,
        line_code=line_code,
        length=None,
    )
    
    t2.add_buffer_stop(0, label='bs.1bis.south')
    t1.add_buffer_stop(0, label='bs.1.south')
    t1bis.add_buffer_stop(0, label='bs.2.south')

    t2.coordinates[0] = (0.2, 45.575)
    t1.coordinates[0] = (0.20005, 45.575)
    t1bis.coordinates[0] = (0.2001, 45.575)

    extend_track(t2, 300, GeoDirection.NORTH)
    extend_track(t1, 300, GeoDirection.NORTH)
    extend_track(t1bis, 300, GeoDirection.NORTH)

    t2, t1, t1bis = build_station_3_5(
        infra_builder,
        track_in=t2,
        track_inout=t1,
        track_out=t1bis,
        geo_direction=GeoDirection.NORTH,
        station_name='A',
        signals_after=False
    )

    # Terminations if needed
    extend_track(t2, 50, GeoDirection.NORTH)
    extend_track(t1, 50, GeoDirection.NORTH)
    extend_track(t1bis, 50, GeoDirection.NORTH)

    build_blocks(t2, 2, geo_direction=GeoDirection.NORTH, forward=True, backward=False)
    build_blocks(t1, 2, geo_direction=GeoDirection.NORTH, forward=True, backward=True)
    build_blocks(t1bis, 2, geo_direction=GeoDirection.NORTH, forward=False, backward=True)

    t2.add_buffer_stop(t2.length, label='bs.2.north')


    ## Build and save
    os.makedirs(dir, exist_ok=True)
    built_infra = build_infra(infra_builder)
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra

