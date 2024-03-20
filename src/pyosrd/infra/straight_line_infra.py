import os

from railjson_generator import (
    InfraBuilder,
)

from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction


def straight_line_infra(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> Infra:
    """
    station A (1 track)                        station B (1 track)

             ┎SA                                    SB┐
     (T)-|----DA------------------------------------DB-----|---->

    10 km long
    Train #1 start from A and arrive at B
    Train #2 start from B and arrive at A
    The two train collide !
    """  # noqa

    infra_builder = InfraBuilder()

    T = infra_builder.add_track_section(label='T', length=10_000)

    T.add_buffer_stop(0, label='buffer_stop.0')
    T.add_buffer_stop(T.length, label='buffer_stop.1')

    DA = T.add_detector(label="DA", position=500, )
    DB = T.add_detector(label="DB", position=T.length-500, )

    SA = T.add_signal(
        DA.position - 20,
        label='SA',
        direction=Direction.START_TO_STOP,
        is_route_delimiter=True,
    )
    SB = T.add_signal(
        DB.position + 20,
        label='SB',
        direction=Direction.STOP_TO_START,
        is_route_delimiter=True,
    )
    SA.add_logical_signal("BAL", settings={"Nf": "true"})
    SB.add_logical_signal("BAL", settings={"Nf": "true"})

    stationA = infra_builder.add_operational_point(label='stationA')
    stationA.add_part(track=T, offset=460)
    stationB = infra_builder.add_operational_point(label='stationB')
    stationB.add_part(track=T, offset=10_000-460)

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
