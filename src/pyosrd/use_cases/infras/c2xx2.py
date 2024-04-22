import os

from railjson_generator import (
    InfraBuilder,
)

from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction


def c2xx2(
    dir: str,
    infra_json: str = 'infra.json',
) -> Infra:
    """
    station0 (2 tracks)                        station1 (2 tracks)

                  ┎S0              S2┐
    (T0)-----------D0--------------D2------(T2)-->
                      \     /
                         SW
                ┎S1   /     \      S3┐
    (T1)---------D1----------------D3------(T3)-->

    """  # noqa

    infra_builder = InfraBuilder()

    T = [
        infra_builder.add_track_section(
            label='T'+str(i),
            length=1_000,
        )
        for i in range(4)
    ]

    for i in [0, 1]:
        T[i].add_buffer_stop(0, label=f'buffer_stop.{i}')
    for i in [2, 3]:
        T[i].add_buffer_stop(T[i].length, label=f'buffer_stop.{i}')

    infra_builder.add_double_slip_switch(
        south_1=T[0].end(),
        south_2=T[1].end(),
        north_1=T[2].begin(),
        north_2=T[3].begin(),
        label='SW',
    )

    T[0].add_detector(label='D0', position=980)
    T[0].add_signal(
        960,
        is_route_delimiter=True,
        label='S0',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[1].add_detector(label='D1', position=980)
    T[1].add_signal(
        960,
        is_route_delimiter=True,
        label='S1',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[2].add_detector(label='D2', position=20)
    T[2].add_signal(
        40,
        is_route_delimiter=True,
        label='S2',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[3].add_detector(label='D3', position=20)
    T[3].add_signal(
        40,
        is_route_delimiter=True,
        label='S3',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    stations = [
        infra_builder.add_operational_point(label='station'+str(i))
        for i in range(2)
    ]
    for track in range(2):
        stations[0].add_part(T[track], 50)
    for track in [2, 3]:
        stations[1].add_part(T[track], 950)

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
