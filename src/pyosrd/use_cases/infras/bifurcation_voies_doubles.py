import math
import os

from haversine import inverse_haversine, haversine, Direction as Dir

from railjson_generator import (
    InfraBuilder,
)
from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction

from pyosrd.infra.build import build_infra

def bifurcation_voies_doubles(
    dir: str,
    infra_json: str = 'infra.json',
) -> Infra:
    """
    
    """  # noqa

    infra_builder = InfraBuilder()

    track_lengths = [
        2_000,
        2_025,
        2_015,
        2_010,
        2_014,
        2_003.5
    ]
    track_names = [
        'V1',
        'V1',
        'V2',
        'V2',
        'V1',
        'V2',        
    ]

    line_names = [
        "Ligne1",
        "Ligne1",
        "Ligne1",
        "Ligne1",
        "Ligne2",
        "Ligne2",
    ]

    T = [
        infra_builder.add_track_section(
            label='T'+str(i),
            track_name=track_names[i],
            line_name=line_names[i],
            line_code=int(line_names[i][-1]),
            length=track_lengths[i],
        )
        for i, _ in enumerate(track_lengths)
    ]

    for i in [0, 2]:
        T[i].add_buffer_stop(0, label=f'buffer_stop.{i}')
    for i in [1, 3, 4, 5]:
        T[i].add_buffer_stop(T[i].length, label=f'buffer_stop.{i}')

    sw0 = infra_builder.add_point_switch(
        T[0].end(),
        T[1].begin(),
        T[4].begin(),
        label='SW0',
    )
    sw1 = infra_builder.add_point_switch(
        T[2].end(),
        T[3].begin(),
        T[5].begin(),
        label='SW1',
    )

    SW0_COORDS = (45.575988410701974, 0.21)
    sw0.set_coords(*SW0_COORDS[::-1])

    t0_begin = inverse_haversine(SW0_COORDS, T[0].length, direction=Dir.WEST, unit='m')
    T[0].set_remaining_coords([t0_begin[::-1]])

    t1_end = inverse_haversine(SW0_COORDS, T[1].length, direction=Dir.EAST, unit='m')
    T[1].set_remaining_coords([t1_end[::-1]])
    
    t2_begin = inverse_haversine(t0_begin, 2.5, Dir.SOUTH, unit='m')
    sw1_coords =  inverse_haversine(t2_begin, T[2].length, Dir.EAST, unit='m')
    sw1.set_coords(*sw1_coords[::-1])
    T[2].set_remaining_coords([t2_begin[::-1]])

    t3_end = inverse_haversine(sw1_coords, T[3].length, direction=Dir.EAST, unit='m')
    T[3].set_remaining_coords([t3_end[::-1]])

    t4_1 = inverse_haversine(SW0_COORDS, 3.5, direction=Dir.NORTHEAST, unit='m')
    t4_2 = inverse_haversine(t4_1, 10., direction=Dir.EAST, unit='m')
    t4_3 = inverse_haversine(t4_2, 10.5, direction=Dir.SOUTHEAST, unit='m')
    t4_end = inverse_haversine(t4_3, 2_000, direction=Dir.SOUTHEAST, unit='m')
    T[4].set_remaining_coords([t4_1[::-1], t4_2[::-1], t4_3[::-1], t4_end[::-1]])

    t5_1 = inverse_haversine(sw1_coords, 3.5, direction=Dir.SOUTHEAST, unit='m')
    t5_end = inverse_haversine(t5_1, 2_000, direction=Dir.SOUTHEAST, unit='m')
    T[5].set_remaining_coords([t5_1[::-1], t5_end[::-1]])

    s0s = T[0].add_signal(
        T[0].length-1500.,
        is_route_delimiter=True,
        label='S0s',
        direction=Direction.START_TO_STOP,
    )
    s0s.add_logical_signal("BAL", settings={"Nf": "false"})
    T[0].add_detector(label='D0s', position=s0s.position+20)

    s0c = T[0].add_signal(
        T[0].length-200.,
        is_route_delimiter=True,
        label='S0c',
        direction=Direction.START_TO_STOP,
    )
    s0c.add_logical_signal("BAL", settings={"Nf": "true"})
    T[0].add_detector(label='D0c', position=s0c.position+20)

    s1s = T[1].add_signal(
        1_500.,
        is_route_delimiter=True,
        label='S1s',
        direction=Direction.START_TO_STOP,
    )
    s1s.add_logical_signal("BAL", settings={"Nf": "false"})
    T[1].add_detector(label='D1s', position=s1s.position+20)

    s4 = T[4].add_signal(
        1_500.,
        is_route_delimiter=True,
        label='S4',
        direction=Direction.START_TO_STOP,
    )
    s4.add_logical_signal("BAL", settings={"Nf": "false"})
    T[4].add_detector(label='D4', position=s4.position+20)

    T[1].add_detector(label='D1r', position=20.)
    T[4].add_detector(label='D4r', position=20.)


    s2s = T[2].add_signal(
        T[2].length-1_500.,
        is_route_delimiter=True,
        label='S2s',
        direction=Direction.STOP_TO_START,
    )
    s2s.add_logical_signal("BAL", settings={"Nf": "false"})
    T[2].add_detector(label='D2s', position=s2s.position-20)

    s3c = T[3].add_signal(
        200.,
        is_route_delimiter=True,
        label='S3c',
        direction=Direction.STOP_TO_START,
    )
    s3c.add_logical_signal("BAL", settings={"Nf": "true"})
    T[3].add_detector(label='D3c', position=s3c.position-20)
    
    s3s = T[3].add_signal(
        1_500.,
        is_route_delimiter=True,
        label='S3s',
        direction=Direction.STOP_TO_START,
    )
    s3s.add_logical_signal("BAL", settings={"Nf": "false"})
    T[3].add_detector(label='D3s', position=s3s.position-20)

    s5c = T[5].add_signal(
        200.,
        is_route_delimiter=True,
        label='S5c',
        direction=Direction.STOP_TO_START,
    )
    s5c.add_logical_signal("BAL", settings={"Nf": "true"})
    T[5].add_detector(label='D5c', position=s5c.position-20)

    s5s = T[5].add_signal(
        1_500.,
        is_route_delimiter=True,
        label='S5s',
        direction=Direction.STOP_TO_START,
    )
    s5s.add_logical_signal("BAL", settings={"Nf": "false"})
    T[5].add_detector(label='D5s', position=s5s.position-20)

    angouleme = infra_builder.add_operational_point(label='Angouleme')
    for track in [0, 2]:
        angouleme.add_part(T[track], 250)
    bordeaux = infra_builder.add_operational_point(label='Bordeaux')
    for track in [1, 3]:
        bordeaux.add_part(T[track], track_lengths[track]-250)
    cognac = infra_builder.add_operational_point(label='Cognac')
    for track in [4, 5]:
        cognac.add_part(T[track], track_lengths[track]-250)

    os.makedirs(dir, exist_ok=True)

    built_infra = build_infra(
        infra_builder,
        buffer_stops_in=['buffer_stop.0']
    )
    
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
