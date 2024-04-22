import os

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
        infra_builder.add_track_section(label='T'+str(id), length=1000)
        for id in range(4)
    ]

    T[0].add_buffer_stop(0, label='buffer_stop.0')
    T[3].add_buffer_stop(T[3].length, label='buffer_stop.3')

    infra_builder.add_point_switch(
        T[0].end(),
        T[1].begin(),
        T[2].begin(),
        label='DVG',
    )
    infra_builder.add_point_switch(
        T[3].begin(),
        T[1].end(),
        T[2].end(),
        label='CVG',
    )

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
