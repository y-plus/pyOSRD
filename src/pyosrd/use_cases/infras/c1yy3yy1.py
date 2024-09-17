import os

from math import asin

from haversine import inverse_haversine, Direction as Dir

from railjson_generator import (
    InfraBuilder,
)

from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction


def c1yy3yy1(
    dir: str,
    infra_json: str = 'infra.json',
) -> Infra:
    """
                 ----------D2------------------------
         ┎S0    /                                    \
    (TO)--D0---sw1--D1-sw2--D3----------------sw3-----sw4--------(T9)
                        \                     /
                         ---D4---------------             

    """  # noqa

    infra_builder = InfraBuilder()

    track_lengths = [
        500,
        12,
        826,
        800,
        802,
        12,
        500,
    ]

    T = [
        infra_builder.add_track_section(
            label='T'+str(i),
            track_name='T'+str(i),
            length=track_lengths[i],
        )
        for i, _ in enumerate(track_lengths)
    ]

    T[0].add_buffer_stop(0, label=f'buffer_stop.0')
    T[6].add_buffer_stop(T[6].length, label=f'buffer_stop.6')

    sw0 = infra_builder.add_point_switch(
        T[0].end(),
        T[1].begin(),
        T[2].begin(),
        label='SW0',
    )
    sw1 = infra_builder.add_point_switch(
        T[1].end(),
        T[3].begin(),
        T[4].begin(),
        label='SW1',
    )
    sw2 = infra_builder.add_point_switch(
        T[5].begin(),
        T[3].end(),
        T[4].end(),
        label='SW2',
    )
    sw3 = infra_builder.add_point_switch(
        T[6].begin(),
        T[2].end(),
        T[5].end(),
        label='SW3',
    )

    SW0_COORDS = (0.21, 45.575988410701974)
    ANGLE = asin(5/13)

    sw0.set_coords(*SW0_COORDS)
    t0_begin = inverse_haversine(SW0_COORDS[::-1], track_lengths[0], direction=Dir.WEST, unit='m')[::-1]
    T[0].set_remaining_coords([t0_begin])

    sw1_coords = inverse_haversine(SW0_COORDS[::-1], track_lengths[1], direction=Dir.EAST, unit='m')[::-1]
    sw2_coords = inverse_haversine(sw1_coords[::-1], track_lengths[3], direction=Dir.EAST, unit='m')[::-1]
    sw3_coords = inverse_haversine(sw2_coords[::-1], track_lengths[5], direction=Dir.EAST, unit='m')[::-1]
    sw1.set_coords(*sw1_coords)
    sw2.set_coords(*sw2_coords)
    sw3.set_coords(*sw3_coords)

    t2_1 = inverse_haversine(SW0_COORDS[::-1], 13, direction=Dir.EAST - ANGLE, unit='m')[::-1]
    t2_2 = inverse_haversine(sw3_coords[::-1], 13, direction=Dir.WEST + ANGLE, unit='m')[::-1]
    T[2].set_remaining_coords([t2_1, t2_2])

    t4_1 = inverse_haversine(sw1_coords[::-1], 13, direction=Dir.EAST + ANGLE, unit='m')[::-1]
    t4_2 = inverse_haversine(sw2_coords[::-1], 13, direction=Dir.WEST - ANGLE, unit='m')[::-1]
    T[4].set_remaining_coords([t4_1, t4_2])
    
    t6_end = inverse_haversine(sw3_coords[::-1], track_lengths[6], direction=Dir.EAST, unit='m')[::-1]
    T[6].set_remaining_coords([t6_end])

    T[0].add_detector(label='D0', position=480)
    T[0].add_signal(
        460,
        is_route_delimiter=True,
        label='S0',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[1].add_detector(label='D1', position=6)


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

    T[4].add_detector(label='D4', position=20)
    T[4].add_signal(
        40,
        is_route_delimiter=True,
        label='S4',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})
    

    T[2].add_detector(label='D5', position=track_lengths[2]-20)
    T[2].add_signal(
        track_lengths[2] - 40,
        is_route_delimiter=True,
        label='S5',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[3].add_detector(label='D6', position=track_lengths[3]-20)
    T[3].add_signal(
        track_lengths[3] - 40,
        is_route_delimiter=True,
        label='S6',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[4].add_detector(label='D7', position=track_lengths[4]-20)
    T[4].add_signal(
        track_lengths[4] - 40,
        is_route_delimiter=True,
        label='S7',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[5].add_detector(label='D8', position=6)

    T[6].add_detector(label='D9', position=20)
    T[6].add_signal(
        track_lengths[6] - 40,
        is_route_delimiter=True,
        label='S9',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    station = infra_builder.add_operational_point(label='station')
    for track in [2, 3, 4]:
        station.add_part(T[track],track_lengths[track]/2)

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
