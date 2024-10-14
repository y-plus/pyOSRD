import os

from haversine import inverse_haversine, Direction as Dir

from railjson_generator import (
    InfraBuilder,
)

from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction


def c1y2y1(
    dir: str,
    infra_json: str = 'infra.json',
) -> Infra:
    """
                        station1 (2 tracks)
                                          ┎S1
                        --D0.1----(T1)-----D1-
                 ┎S0  /                        \               ┎S3
        |--(T0)----D0-<DVG                    CVG>-D3.0--(T3)---D3--|
                      \                   ┎S2  /
                        --D0.2----(T2)-----D2-

    All tracks are 1000m long
    """  # noqa

    infra_builder = InfraBuilder()

    T = [
        infra_builder.add_track_section(
            label='T'+str(id),
            track_name='V1' if id !=2 else 'V3',
            length=1000,
        )
        for id in range(4)
    ]

    T[0].add_buffer_stop(0, label='buffer_stop.0')
    T[3].add_buffer_stop(T[3].length, label='buffer_stop.3')

    dvg = infra_builder.add_point_switch(
        T[0].end(),
        T[1].begin(),
        T[2].begin(),
        label='DVG',
    )
    cvg = infra_builder.add_point_switch(
        T[3].begin(),
        T[1].end(),
        T[2].end(),
        label='CVG',
    )

    DVG_COORDS = (0.21, 45.575988410701974)
    PINCH = 0.75

    dvg.set_coords(*DVG_COORDS)

    t0_begin = inverse_haversine(DVG_COORDS[::-1], 1_000, direction=Dir.WEST, unit='m')[::-1]
    T[0].set_remaining_coords([t0_begin])

    t1_1 = inverse_haversine(DVG_COORDS[::-1], 250, direction=Dir.NORTHEAST+PINCH, unit='m')[::-1]
    t1_2 = inverse_haversine(t1_1[::-1], 500, direction=Dir.EAST, unit='m')[::-1]
    t1_end = inverse_haversine(t1_2[::-1], 250, direction=Dir.SOUTHEAST-PINCH, unit='m')[::-1]
    T[1].set_remaining_coords([t1_1, t1_2, t1_end])

    cvg.set_coords(*t1_end)

    t2_1 = inverse_haversine(DVG_COORDS[::-1], 250, direction=Dir.SOUTHEAST-PINCH, unit='m')[::-1]
    t2_2 = inverse_haversine(t2_1[::-1], 500, direction=Dir.EAST, unit='m')[::-1]
    T[2].set_remaining_coords([t2_1, t2_2])

    t3_end = inverse_haversine(t1_end[::-1], 1_000, direction=Dir.EAST, unit='m')[::-1]
    T[3].set_remaining_coords([t3_end])   
    
    for i in [0, 1, 2, 3]:
        track = T[i]
        d = track.add_detector(
            label=f"D{i}",
            position=950,
        )
        s = track.add_signal(
            d.position - 20,
            Direction.START_TO_STOP,
            is_route_delimiter=True,
            label=f"S{i}"
        )
        s.add_logical_signal("BAL", settings={"Nf": "true"})

    T[1].add_detector(
            label="D0.1",
            position=50,
        )
    T[2].add_detector(
            label="D0.2",
            position=50,
        )
    T[3].add_detector(
            label="D3.0",
            position=50,
        )

    station = infra_builder.add_operational_point(label='station0')

    for track in [1, 2]:
        station.add_part(T[track], 300)

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
