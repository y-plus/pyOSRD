import os

from haversine import inverse_haversine, Direction as Dir

from railjson_generator import (
    InfraBuilder,
)

from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction

from pyosrd.use_cases.infras.helpers.builders import (
    build_junction,
    add_carre_with_detector,
    add_semaphores_with_detector,
    build_blocks,
    build_station,
    extend_track,
    build_station_3_5,
    build_terminal_station_3_5,
    build_terminal_station_2_4
)

def straight(
    dir: str,
    infra_json: str = 'infra.json',
    num_stations: int = 4,
) -> Infra:
    """
                ┎SA SA.1┐       ┎S2.0 S2.1┐       ┎S8.0 S8.1┐     ┎SB SB.1┐
     (T)<---A------DA----------------D2-----...--------D8-------------DB------B---->

    10 km long, Detectors D2,D4,D6,D8 detectors every 2km
    Trains start from A and arrive at B
    """  # noqa

    infra_builder = InfraBuilder()

    T = infra_builder.add_track_section(
        label='T',
        track_name='V1',
        track_number=0,
        line_code=0,
        line_name="Ligne 1",
        length=1,

    )
    num_stations = 4
    num_blocks_btw_stations = 5

    BEGIN = (45.575988410701974, 0.21)
    T.coordinates[0] = tuple(BEGIN[::-1])
    build_blocks(
        track=T,
        num_blocks=(num_stations+1)*num_blocks_btw_stations,
        forward=True,
        backward=False,
        geo_direction=Dir.EAST,
        length_block=2_000,
    )

    first = ord('A')

    for n in range(num_stations):
        op = infra_builder.add_operational_point(
            chr(first+n)
        )
        op.add_part(T, (n+1) * num_blocks_btw_stations*2_000 - 200)
    

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
