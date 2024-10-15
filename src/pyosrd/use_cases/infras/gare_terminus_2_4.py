import math
import os

from haversine import inverse_haversine, haversine, Direction as Dir

from railjson_generator import (
    InfraBuilder,
)
from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction

from pyosrd.infra.build import build_infra

def gare_terminus_2_4(
    dir: str,
    infra_json: str = 'infra.json',
) -> Infra:
    """
    
    """  # noqa

    infra_builder = InfraBuilder()

    track_lengths = [
        3006,
        5,
        26,
        512.5,
        9.25,
        503.25,
        6.5, 
        6.5,
        3000,
        17,
        20,
        9.25,
        503.25,
        512.5
    ]
    track_names = [
        'V1',
        'V1',
        'V1',
        'V3',
        'V1',
        'V1',
        'J',
        'J',
        'V2',
        'V2',
        'V2',
        'V2',
        'V2',
        'V4'
    ]

    T = [
        infra_builder.add_track_section(
            label='T'+str(i),
            track_name=track_names[i],
            length=track_lengths[i],
        )
        for i, _ in enumerate(track_lengths)
    ]

    for i in [0, 8]:
        T[i].add_buffer_stop(0, label=f'buffer_stop.{i}')
    for i in [3, 5, 12, 13]:
        T[i].add_buffer_stop(T[i].length, label=f'buffer_stop.{i}')

    sw0 = infra_builder.add_point_switch(
        T[1].begin(),
        T[0].end(),
        T[6].end(),
        label='SW0',
    )
    sw1 = infra_builder.add_point_switch(
        T[1].end(),
        T[2].begin(),
        T[7].begin(),
        label='SW1',
    )
    sw2 = infra_builder.add_point_switch(
        T[2].end(),
        T[3].begin(),
        T[4].begin(),
        label='SW2',
    )
    sw3 = infra_builder.add_double_slip_switch(
        north_1=T[4].end(),
        north_2=T[11].end(),
        south_1=T[5].begin(),
        south_2=T[12].begin(),
        label='SW3'
    )
    sw4 = infra_builder.add_point_switch(
        T[8].end(),
        T[6].begin(),
        T[9].begin(),
        label='SW4',
    )
    sw5 = infra_builder.add_point_switch(
        T[10].begin(),
        T[9].end(),
        T[7].end(),
        label='SW5',
    )
    sw6 = infra_builder.add_point_switch(
        T[10].end(),
        T[11].begin(),
        T[13].begin(),
        label='SW6',
    )

    SW0_COORDS = (45.575988410701974, 0.21)
    ANGLE = math.asin(5./13.)

    sw0.set_coords(*SW0_COORDS[::-1])
    t0_begin = inverse_haversine(SW0_COORDS, T[0].length, direction=Dir.WEST, unit='m')
    T[0].set_remaining_coords([t0_begin[::-1]])
    
    sw1_coords = inverse_haversine(SW0_COORDS, T[1].length, direction=Dir.EAST, unit='m')
    sw1.set_coords(*sw1_coords[::-1])
    
    sw2_coords = inverse_haversine(sw1_coords, T[2].length, direction=Dir.EAST, unit='m')
    sw2.set_coords(*sw2_coords[::-1])
    
    t3_elbow = inverse_haversine(sw2_coords, 6.5, direction=Dir.EAST-ANGLE, unit='m')
    t3_end = inverse_haversine(t3_elbow, 506., direction=Dir.EAST, unit='m')
    T[3].set_remaining_coords([t3_elbow[::-1], t3_end[::-1]])

    t4_elbow = inverse_haversine(sw2_coords, 6., direction=Dir.EAST, unit='m')

    sw3_coords = inverse_haversine(t4_elbow, 3.25, direction=Dir.EAST+ANGLE, unit='m')
    sw3.set_coords(*sw3_coords[::-1])
    T[4].set_remaining_coords([t4_elbow[::-1]])

    t5_elbow = inverse_haversine(t4_elbow, 6., direction=Dir.EAST, unit='m')
    t5_end = inverse_haversine(t5_elbow, 500., direction=Dir.EAST, unit='m')
    T[5].set_remaining_coords([t5_elbow[::-1], t5_end[::-1]])

    t8_begin = inverse_haversine(t0_begin, 2.5, direction=Dir.SOUTH, unit='m')
    sw4_coords = inverse_haversine(t8_begin, T[8].length, direction=Dir.EAST, unit='m')
    sw4.set_coords(*sw4_coords[::-1])
    T[8].set_remaining_coords([t8_begin[::-1]])
    
    sw5_coords = inverse_haversine(sw4_coords, T[9].length, direction=Dir.EAST, unit='m')
    sw5.set_coords(*sw5_coords[::-1])

    sw6_coords = inverse_haversine(sw5_coords, T[10].length, direction=Dir.EAST, unit='m')
    sw6.set_coords(*sw6_coords[::-1])
    
    t11_elbow = inverse_haversine(sw6_coords, 6., direction=Dir.EAST, unit='m')
    T[11].set_remaining_coords([t11_elbow[::-1]])

    t12_elbow = inverse_haversine(t11_elbow, 6., direction=Dir.EAST, unit='m')
    t12_end = inverse_haversine(t12_elbow, 500., direction=Dir.EAST, unit='m')
    T[12].set_remaining_coords([t12_elbow[::-1], t12_end[::-1]])

    t13_elbow = inverse_haversine(sw6_coords, 6.5, direction=Dir.EAST+ANGLE, unit='m')
    t13_end = inverse_haversine(t13_elbow, 506., direction=Dir.EAST, unit='m')
    T[13].set_remaining_coords([t13_elbow[::-1], t13_end[::-1]])

    T[0].add_signal(
        1500,
        is_route_delimiter=True,
        label='S0a',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})
    T[0].add_detector(label='D0a', position=1500)
    T[0].add_signal(
        2800,
        is_route_delimiter=True,
        label='S0b',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})
    T[0].add_detector(label='D0b', position=2800)

    T[1].add_detector(label='D1', position=T[1].length/2)
    T[2].add_detector(label='D2', position=T[2].length/2)

    T[3].add_signal(
        50,
        is_route_delimiter=True,
        label='S3',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})
    T[3].add_detector(label='D3', position=50)

    T[4].add_detector(label='D4', position=T[4].length/2)

    T[5].add_signal(
        38.25,
        is_route_delimiter=True,
        label='S5',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})
    T[5].add_detector(label='D5', position=38.25)

    T[6].add_detector(label='D6', position=T[6].length/2)
    T[7].add_detector(label='D7', position=T[7].length/2)

    T[8].add_signal(
        1500,
        is_route_delimiter=True,
        label='S8',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})
    T[8].add_detector(label='D8', position=1500)

    T[9].add_detector(label='D9', position=T[9].length/2)
    T[10].add_detector(label='D10', position=T[10].length/2)

    T[11].add_detector(label='D11', position=T[11].length/2)

    T[12].add_signal(
        38.25,
        is_route_delimiter=True,
        label='S12',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})
    T[12].add_detector(label='D12', position=38.25)

    T[13].add_signal(
        50,
        is_route_delimiter=True,
        label='S13',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})
    T[13].add_detector(label='D13', position=50)


    stationA = infra_builder.add_operational_point(label='stationA')
    for track in [0, 8]:
        stationA.add_part(T[track], 100)
    stationB = infra_builder.add_operational_point(label='stationB')
    for track in [3, 5, 12, 13]:
        stationB.add_part(T[track], 450)

    os.makedirs(dir, exist_ok=True)

    built_infra = build_infra(
        infra_builder,
        buffer_stops_in=['buffer_stop.0']
    )
    
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
