import os

from math import asin

from haversine import inverse_haversine, Direction as Dir

from railjson_generator import (
    InfraBuilder,
)

from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction

from pyosrd.infra.build import build_infra

def ipcs(
    dir: str,
    infra_json: str = 'infra.json',
) -> Infra:
    """
             
    """  # noqa

    infra_builder = InfraBuilder()

    track_lengths = [
        206,
        5,
        512,
        5,
        206,
        6.5,
        6.5,
        6.5,
        6.5,
        200,
        17,
        500,
        17,
        200
    ]
    track_names = ['V1'] * 5 + ['J1', 'J1', 'J2', 'J2'] + ['V2'] * 5
    T = [
        infra_builder.add_track_section(
            label='T'+str(i),
            track_name=track_names[i],
            length=track_lengths[i],
        )
        for i, _ in enumerate(track_lengths)
    ]

    T[0].add_buffer_stop(0, label=f'buffer_stop.0')
    T[4].add_buffer_stop(T[4].length, label=f'buffer_stop.4')
    T[9].add_buffer_stop(0, label=f'buffer_stop.9')
    T[13].add_buffer_stop(T[13].length, label=f'buffer_stop.13')

    sw0 = infra_builder.add_point_switch(
        T[1].begin(),
        T[0].end(),
        T[5].end(),
        label='SW0',
    )
    sw1 = infra_builder.add_point_switch(
        T[1].end(),
        T[2].begin(),
        T[6].begin(),
        label='SW1',
    )
    sw2 = infra_builder.add_point_switch(
        T[3].begin(),
        T[2].end(),
        T[7].end(),
        label='SW2',
    )
    sw3 = infra_builder.add_point_switch(
        T[3].end(),
        T[4].begin(),
        T[8].begin(),
        label='SW3',
    )
    sw4 = infra_builder.add_point_switch(
        T[9].end(),
        T[5].begin(),
        T[10].begin(),
        label='SW4',
    )
    sw5 = infra_builder.add_point_switch(
        T[11].begin(),
        T[10].end(),
        T[6].end(),
        label='SW5',
    )
    sw6 = infra_builder.add_point_switch(
        T[11].end(),
        T[7].begin(),
        T[12].begin(),
        label='SW6',
    )
    sw7 = infra_builder.add_point_switch(
        T[13].begin(),
        T[12].end(),
        T[8].end(),
        label='SW7',
    )
    
    COORDS = (0.21, 45.575988410701974)
    ANGLE = asin(5/13)

    sw0_coords = inverse_haversine(COORDS[::-1], T[0].length, direction=Dir.EAST, unit='m')[::-1]
    sw0.set_coords(*sw0_coords)
    T[0].set_remaining_coords([COORDS])
    sw1_coords = inverse_haversine(sw0_coords[::-1], T[1].length, direction=Dir.EAST, unit='m')[::-1]
    sw1.set_coords(*sw1_coords)
    sw2_coords = inverse_haversine(sw1_coords[::-1], T[2].length, direction=Dir.EAST, unit='m')[::-1]
    sw2.set_coords(*sw2_coords)
    sw3_coords = inverse_haversine(sw2_coords[::-1], T[3].length, direction=Dir.EAST, unit='m')[::-1]
    sw3.set_coords(*sw3_coords)
    t4_end = inverse_haversine(sw3_coords[::-1], T[4].length, direction=Dir.EAST, unit='m')[::-1]
    T[4].set_remaining_coords([t4_end])

    t9_begin = inverse_haversine(COORDS[::-1], 2.5, direction=Dir.SOUTH, unit='m')[::-1]
    sw4_coords = inverse_haversine(t9_begin[::-1], T[9].length, direction=Dir.EAST, unit='m')[::-1]
    sw4.set_coords(*sw4_coords)
    T[9].set_remaining_coords([t9_begin])
    sw5_coords = inverse_haversine(sw4_coords[::-1], T[10].length, direction=Dir.EAST, unit='m')[::-1]
    sw5.set_coords(*sw5_coords)
    sw6_coords = inverse_haversine(sw5_coords[::-1], T[11].length, direction=Dir.EAST, unit='m')[::-1]
    sw6.set_coords(*sw6_coords)
    sw7_coords = inverse_haversine(sw6_coords[::-1], T[12].length, direction=Dir.EAST, unit='m')[::-1]
    sw7.set_coords(*sw7_coords)
    t13_end = inverse_haversine(sw7_coords[::-1], T[13].length, direction=Dir.EAST, unit='m')[::-1]
    T[13].set_remaining_coords([t13_end])


    T[0].add_detector(label='D0', position=T[0].length-20)
    T[0].add_signal(
        track_lengths[0] - 40,
        is_route_delimiter=True,
        label='S0',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[1].add_detector(label='D1', position=T[1].length/2)
    T[2].add_detector(label='D2a', position=20)
    T[2].add_detector(label='D2b', position=T[2].length-20)
    T[2].add_signal(
        T[2].length - 40,
        is_route_delimiter=True,
        label='S2b',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[3].add_detector(label='D3', position=T[3].length/2)
    T[4].add_detector(label='D4', position=20)
    T[4].add_signal(
        40,
        is_route_delimiter=True,
        label='S4',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[5].add_detector(label='D5', position=T[5].length/2)
    T[6].add_detector(label='D6', position=T[6].length/2)
    T[7].add_detector(label='D7', position=T[7].length/2)
    T[8].add_detector(label='D8', position=T[8].length/2)

    T[9].add_detector(label='D9', position=T[9].length-20)
    T[9].add_signal(
        T[9].length - 40,
        is_route_delimiter=True,
        label='S9b',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[10].add_detector(label='D10', position=T[10].length/2)
    T[11].add_detector(label='D11a', position=20)
    T[11].add_signal(
        40,
        is_route_delimiter=True,
        label='11a',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[11].add_detector(label='D11b', position=T[11].length-20)
    T[12].add_detector(label='D12', position=T[12].length/2)
    T[13].add_detector(label='D13', position=20)   
    T[13].add_signal(
        40,
        is_route_delimiter=True,
        label='S13',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    station = infra_builder.add_operational_point(label='station')
    for track in [2, 11]:
        station.add_part(T[track],track_lengths[track]/2)

    os.makedirs(dir, exist_ok=True)

    # built_infra = infra_builder.build()
    built_infra = build_infra(
        infra_builder,
        buffer_stops_in=['buffer_stop.0', 'buffer_stop.13'],
        buffer_stops_out=['buffer_stop.9', 'buffer_stop.4'],
    )
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
