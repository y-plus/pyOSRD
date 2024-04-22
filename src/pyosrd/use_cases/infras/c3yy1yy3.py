import os

from railjson_generator import (
    InfraBuilder,
)

from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction


def c3yy1yy3(
    dir: str,
    infra_json: str = 'infra.json',
) -> Infra:
    """
    stationA(3 tracks)                                        stationB (1 track)

          ┎S0            S4┐               ┎S5           S6┐
    (T0)---D0------SW0---D4--(T4)--+--(T5)--D5--SW2------D6---(T6)
          ┎S1     D3/(T3)                    (T9)\D9     S7┐
    (T1)---D1-----SW1                            SW3-----D7---(T7)
          ┎S2     /                               \      S8┐
    (T2)---D2-----                                  -----D8---(T8)

    """  # noqa

    infra_builder = InfraBuilder()

    track_lengths = [
        504,
        500,
        500,
        5,
        500,
        500,
        504,
        500,
        500,
        5,
    ]
    T = [
        infra_builder.add_track_section(
            label='T'+str(i),
            length=track_lengths[i],
        )
        for i, _ in enumerate(track_lengths)
    ]

    for i in [0, 1, 2]:
        T[i].add_buffer_stop(0, label=f'buffer_stop.{i}')
    for i in [6, 7, 8]:
        T[i].add_buffer_stop(T[i].length, label=f'buffer_stop.{i}')

    infra_builder.add_point_switch(
        T[4].begin(),
        T[0].end(),
        T[3].end(),
        label='SW0',
    )
    infra_builder.add_point_switch(
        T[3].begin(),
        T[1].end(),
        T[2].end(),
        label='SW1',
    )
    infra_builder.add_link(T[4].end(), T[5].begin())
    infra_builder.add_point_switch(
        T[5].end(),
        T[6].begin(),
        T[9].begin(),
        label='SW2',
    )
    infra_builder.add_point_switch(
        T[9].end(),
        T[7].begin(),
        T[8].begin(),
        label='SW3',
    )

    T[0].add_detector(label='D0', position=480)
    T[0].add_signal(
        460,
        is_route_delimiter=True,
        label='S0',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[1].add_detector(label='D1', position=480)
    T[1].add_signal(
        460,
        is_route_delimiter=True,
        label='S1',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[2].add_detector(label='D2', position=480)
    T[2].add_signal(
        460,
        is_route_delimiter=True,
        label='S2',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[4].add_detector(label='D4', position=20)
    T[4].add_signal(
        40,
        is_route_delimiter=True,
        label='S4',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[3].add_detector(label='D3', position=2.5)

    T[5].add_detector(label='D5', position=480)
    T[5].add_signal(
        460,
        is_route_delimiter=True,
        label='S5',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[6].add_detector(label='D6', position=20)
    T[6].add_signal(
        40,
        is_route_delimiter=True,
        label='S6',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[7].add_detector(label='D7', position=20)
    T[7].add_signal(
        40,
        is_route_delimiter=True,
        label='S7',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[8].add_detector(label='D8', position=20)
    T[8].add_signal(
        40,
        is_route_delimiter=True,
        label='S8',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[9].add_detector(label='D9', position=2.5)

    stationA = infra_builder.add_operational_point(label='stationA')
    for track in [0, 1, 2]:
        stationA.add_part(T[track], 20)

    stationB = infra_builder.add_operational_point(label='stationB')
    for track in [6, 7, 8]:
        stationB.add_part(T[track], 480)

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
