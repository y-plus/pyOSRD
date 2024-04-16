import os

from importlib.resources import files

from railjson_generator import (
    InfraBuilder,
    Location,
)

from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction
from railjson_generator.schema.simulation.simulation import (
    register_rolling_stocks
)

register_rolling_stocks(files('pyosrd').joinpath('rolling_stocks'))


def c2y11s(
    dir: str,
    infra_json: str = 'infra.json',
) -> Infra:
    """


           ┎SA0
    (T0)----DA0-
                 \       ┎S1
               SWA>-DA2---D1---(T2)
           ┎SA1  /
    (T1)----DA1-

    All blocks are 1,5 km long
    All station lanes are 500m long
    Train 0 starts from T0 at t=0 and arrives at T2
    Train 1 starts from T1 at t=100 and arrives at T2
    """  # noqa

    infra_builder = InfraBuilder()

    track_lengths = [1_000, 1_000, 5_000]

    T = [
        infra_builder.add_track_section(
            label='T'+str(id),
            length=track_lengths[id],
        )
        for id, _ in enumerate(track_lengths)
    ]

    infra_builder.add_point_switch(
        T[2].begin(),
        T[0].end(),
        T[1].end(),
        label='SWA',
    )

    T[0].add_buffer_stop(0, label='buffer_stop.0', )
    T[1].add_buffer_stop(0, label='buffer_stop.1', )
    T[2].add_buffer_stop(T[2].length, label='buffer_stop.2', )

    for i in [0, 1]:
        d = T[i].add_detector(
            label=f"DA{i}",
            position=T[i].length - 200,
        )
        T[i].add_signal(
            d.position - 20,
            Direction.START_TO_STOP,
            is_route_delimiter=True,
            label=f"SA{i}"
        ).add_logical_signal("BAL", settings={"Nf": "true"})
    T[2].add_detector(
        label="DA2",
        position=200,
    )
    for i in [1]:
        d = T[2].add_detector(
            label=f"D{i}",
            position=1_500 + (i-1) * 3_500,
        )
        T[2].add_signal(
            label=f"S{i}",
            position=d.position - 20,
            direction=Direction.START_TO_STOP,
            is_route_delimiter=True,
        ).add_logical_signal("BAL", settings={"Nf": "true"})

        d_station_start = T[2].add_detector(
            label=f"D{chr(65+i)}",
            position=d.position + 1_500,
        )
        T[2].add_signal(
            label=f"S{chr(65+i)}",
            position=d_station_start.position - 20,
            direction=Direction.START_TO_STOP,
            is_route_delimiter=True,
        ).add_logical_signal("BAL", settings={"Nf": "true"})

        d_station_end = T[2].add_detector(
            label=f"D{chr(65+i)}2",
            position=d_station_start.position + 500,
        )
        T[2].add_signal(
            label=f"S{chr(65+i)}2",
            position=d_station_end.position - 20,
            direction=Direction.START_TO_STOP,
            is_route_delimiter=True,
        ).add_logical_signal("BAL", settings={"Nf": "true"})

    stations = {}

    for i in [1, 2, 3]:
        infra_builder.add_operational_point(
            label='station'+chr(65+i)
        ).add_part(T[2], 3_410 + (i-1) * 3_500)
        stations[chr(65+i)] = Location(T[2], 3_410 + (i-1) * 3_500)
    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
