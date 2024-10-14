import os

from haversine import inverse_haversine, Direction as Dir

from railjson_generator import (
    InfraBuilder,
)

from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction


def c1(
    dir: str,
    infra_json: str = 'infra.json',
) -> Infra:
    """
    station A (1 track)                        station B (1 track)

             ┎SA                                   ┎SB
     (T)-|----DA------------------------------------DB-----|---->

    10 km long
    """  # noqa

    infra_builder = InfraBuilder()

    T = infra_builder.add_track_section(label='T', length=10_000)

    begin = (0.21, 45.575988410701974)
    end = inverse_haversine(begin[::-1], 10, direction=Dir.WEST, unit='km')[::-1]
    T.set_remaining_coords([begin, end])

    T.add_buffer_stop(0, label='buffer_stop.0')
    T.add_buffer_stop(T.length, label='buffer_stop.1')

    DA = T.add_detector(label="DA", position=500, )
    DB = T.add_detector(label="DB", position=T.length-500, )

    T.add_signal(
        DA.position - 20,
        label='SA',
        direction=Direction.START_TO_STOP,
        is_route_delimiter=True,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T.add_signal(
        DB.position - 20,
        label='SB',
        direction=Direction.START_TO_STOP,
        is_route_delimiter=True,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    stationA = infra_builder.add_operational_point(label='stationA')
    stationA.add_part(track=T, offset=460)
    stationB = infra_builder.add_operational_point(label='stationB')
    stationB.add_part(track=T, offset=10_000-60)

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()

    os.makedirs(dir, exist_ok=True)
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
