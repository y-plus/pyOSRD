import os

from haversine import inverse_haversine, Direction as Dir

from railjson_generator import (
    InfraBuilder,
    Location,
)

from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction


def c2y1sy2sy1s(
    dir: str,
    infra_json: str = 'infra.json',
) -> tuple[Infra, dict]:
    """


           ┎SA0
    (T0)----DA0-                                            (T3)
                 \       ┎S1    ┎SB  ┎SB2    ┎S2    ┎SC      ┎SC2         ┎S3    ┎SD  ┎SD2
               SWA>-DA2---D1-----DB-o-DB2-----D2-----DC--DC0---o-DC2-------D3-----DD-o-DD2-----(T4)
           ┎SA1  /                                   SWC\            /SWC2
    (T1)----DA1-                 (T2)                    DC1--o-DC3-(T5)


    """  # noqa

    infra_builder = InfraBuilder()

    track_lengths = [1_000, 1_000, 6_700, 1_000, 4_800, 1_000]

    T = [
        infra_builder.add_track_section(
            label='T'+str(id),
            track_name='T'+str(id),
            length=track_lengths[id],
        )
        for id, _ in enumerate(track_lengths)
    ]

    swa = infra_builder.add_point_switch(
        T[2].begin(),
        T[0].end(),
        T[1].end(),
        label='SWA',
    )

    swc = infra_builder.add_point_switch(
        T[2].end(),
        T[3].begin(),
        T[5].begin(),
        label='SWC'
    )
    swc2 = infra_builder.add_point_switch(
        T[4].begin(),
        T[3].end(),
        T[5].end(),
        label='SWC2'
    )

    SWA_COORDS = (0.21, 45.575988410701974)
    PINCH = 0.7
    
    swa.set_coords(*SWA_COORDS)


    t0_mid = inverse_haversine(SWA_COORDS[::-1], 500, direction=Dir.NORTHWEST-PINCH, unit='m')[::-1]
    t0_begin = inverse_haversine(t0_mid[::-1], 500, direction=Dir.WEST, unit='m')[::-1]
    T[0].set_remaining_coords([t0_begin, t0_mid])

    
    t1_mid = inverse_haversine(SWA_COORDS[::-1], 500, direction=Dir.SOUTHWEST+PINCH, unit='m')[::-1]
    t1_begin = inverse_haversine(t1_mid[::-1], 500, direction=Dir.WEST, unit='m')[::-1]
    T[1].set_remaining_coords([t1_begin, t1_mid])

    swc_coords = inverse_haversine(SWA_COORDS[::-1], 6_700, direction=Dir.EAST, unit='m')[::-1]
    swc.set_coords(*swc_coords)
    
    t3_1 = inverse_haversine(swc_coords[::-1], 250, direction=Dir.NORTHEAST+PINCH, unit='m')[::-1]
    t3_2 = inverse_haversine(t3_1[::-1], 500, direction=Dir.EAST, unit='m')[::-1]
    swc2_coords = inverse_haversine(t3_2[::-1], 250, direction=Dir.SOUTHEAST-PINCH, unit='m')[::-1]
    T[3].set_remaining_coords([t3_1, t3_2, swc2_coords])

    swc2.set_coords(*swc2_coords)

    t5_1 = inverse_haversine(swc_coords[::-1], 250, direction=Dir.SOUTHEAST-PINCH, unit='m')[::-1]
    t5_2 = inverse_haversine(t5_1[::-1], 500, direction=Dir.EAST, unit='m')[::-1]
    T[5].set_remaining_coords([t5_1, t5_2])

    t4_end = inverse_haversine(swc2_coords[::-1], 4_800, direction=Dir.EAST, unit='m')[::-1]
    T[4].set_remaining_coords([t4_end])
    
    T[0].add_buffer_stop(0, label='buffer_stop.0', )
    T[1].add_buffer_stop(0, label='buffer_stop.1', )
    T[4].add_buffer_stop(T[4].length, label='buffer_stop.4', )

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

    for i in [1, 2]:
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

    d = T[4].add_detector(
        label="D3",
        position=1_300,
    )
    T[4].add_signal(
        label="S3",
        position=d.position - 20,
        direction=Direction.START_TO_STOP,
        is_route_delimiter=True,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    stations = {}

# station B
    d_station_start = T[2].add_detector(
        label="DB",
        position=3_000,
    )
    T[2].add_signal(
        label="SB",
        position=d_station_start.position - 20,
        direction=Direction.START_TO_STOP,
        is_route_delimiter=True,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    d_station_end = T[2].add_detector(
        label="DB2",
        position=d_station_start.position + 500,
    )
    T[2].add_signal(
        label="SB2",
        position=d_station_end.position - 20,
        direction=Direction.START_TO_STOP,
        is_route_delimiter=True,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    infra_builder.add_operational_point(
            label='stationB'
        ).add_part(T[2], 3_410)
    stations['B'] = Location(T[2], 3_410)


# station C
    d_station_start = T[2].add_detector(
        label="DC",
        position=6_500,
    )
    T[2].add_signal(
        label="SC",
        position=d_station_start.position - 20,
        direction=Direction.START_TO_STOP,
        is_route_delimiter=True,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    d_station_end = T[3].add_detector(
        label="DC2",
        position=800,
    )

    T[3].add_detector(
        label='DC0',
        position=120,
    )
    T[5].add_detector(
        label='DC1',
        position=120,
    )

    T[3].add_signal(
        label="SC2",
        position=d_station_end.position - 20,
        direction=Direction.START_TO_STOP,
        is_route_delimiter=True,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    stationC = infra_builder.add_operational_point(
            label='stationC'
        )
    stationC.add_part(T[3], 710)
    stations['C'] = Location(T[3], 710)

    # Lane 2
    d_station_end = T[5].add_detector(
        label="DC3",
        position=800,
    )

    T[5].add_signal(
        label="SC3",
        position=d_station_end.position - 20,
        direction=Direction.START_TO_STOP,
        is_route_delimiter=True,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    stationC.add_part(T[5], 710)
    stations['C_2'] = Location(T[5], 710)

# station D
    d_station_start = T[4].add_detector(
        label="DD",
        position=2_800,
    )
    T[4].add_signal(
        label="SD",
        position=d_station_start.position - 20,
        direction=Direction.START_TO_STOP,
        is_route_delimiter=True,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    d_station_end = T[4].add_detector(
        label="DD2",
        position=d_station_start.position + 500,
    )
    T[4].add_signal(
        label="SD2",
        position=d_station_end.position - 20,
        direction=Direction.START_TO_STOP,
        is_route_delimiter=True,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    infra_builder.add_operational_point(
            label='stationD'
        ).add_part(T[4], 3_210)
    stations['D'] = Location(T[4], 3_210)

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra, stations
