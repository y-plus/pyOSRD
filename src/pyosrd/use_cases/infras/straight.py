import os

from haversine import inverse_haversine, Direction as Dir

from railjson_generator import (
    InfraBuilder,
)

from railjson_generator.schema.infra.infra import Infra
# from railjson_generator.schema.infra.direction import Direction

from pyosrd.use_cases.infras.helpers.builders import (
    build_blocks,
)

def straight(
    dir: str,
    infra_json: str = 'infra.json',
    num_stations: int = 4,
) -> Infra:

    infra_builder = InfraBuilder()

    T = infra_builder.add_track_section(
        label='T',
        track_name='V1',
        track_number=0,
        line_code=0,
        line_name="Ligne 1",
        length=1,

    )
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

    for n in range(num_stations):
        op = infra_builder.add_operational_point(
            chr(ord('A')+n)
        )
        op.add_part(T, (n+1) * num_blocks_btw_stations*2_000 - 200)
    

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
