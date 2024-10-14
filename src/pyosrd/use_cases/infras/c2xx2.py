import os

from haversine import inverse_haversine, Direction as Dir

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
            track_name='T'+str(i)
        )
        for i in range(4)
    ]

    for i in [0, 1]:
        T[i].add_buffer_stop(0, label=f'buffer_stop.{i}')
    for i in [2, 3]:
        T[i].add_buffer_stop(T[i].length, label=f'buffer_stop.{i}')

    sw = infra_builder.add_double_slip_switch(
        north_1=T[0].end(),  # A1
        north_2=T[1].end(),  # A2
        south_1=T[3].begin(), # B1
        south_2=T[2].begin(), # B2
        label='SW',
    )

    SW_COORDS = (0.21, 45.575988410701974)
    PINCH = 0

    sw.set_coords(*SW_COORDS)

    t0_mid = inverse_haversine(SW_COORDS[::-1], 5, direction=Dir.NORTHWEST-PINCH, unit='m')[::-1]
    t0_begin = inverse_haversine(t0_mid[::-1], 995, direction=Dir.WEST, unit='m')[::-1]
    T[0].set_remaining_coords([t0_begin, t0_mid])

    t1_mid = inverse_haversine(SW_COORDS[::-1], 5, direction=Dir.SOUTHWEST+PINCH, unit='m')[::-1]
    t1_begin = inverse_haversine(t1_mid[::-1], 995, direction=Dir.WEST, unit='m')[::-1]
    T[1].set_remaining_coords([t1_begin, t1_mid])

    t2_mid = inverse_haversine(SW_COORDS[::-1], 5, direction=Dir.NORTHEAST+PINCH, unit='m')[::-1]
    t2_begin = inverse_haversine(t2_mid[::-1], 995, direction=Dir.EAST, unit='m')[::-1]
    T[2].set_remaining_coords([t2_mid, t2_begin])

    t3_mid = inverse_haversine(SW_COORDS[::-1], 5, direction=Dir.SOUTHEAST-PINCH, unit='m')[::-1]
    t3_begin = inverse_haversine(t3_mid[::-1], 995, direction=Dir.EAST, unit='m')[::-1]
    T[3].set_remaining_coords([t3_mid, t3_begin])

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
