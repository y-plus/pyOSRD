import os

from railjson_generator import (
    InfraBuilder,
)
from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction


def station_capacity2_infra(
    dir: str,
    infra_json: str = 'infra.json',
) -> Infra:
    """
                                 o = station(2 lanes)
                     S1┐          ┎S3
                    -D1-(T1)---+-o-D3-(T3)
              ┎S0  /                       \   S5┐
    --(T0)-----D0-<DVG                   CVG>--D5-------(T5)--->
                   \  S2┐          ┎S4     /
                     -D2-(T2)---+-o-D4-(T4)

    All tracks are 1 km long
    Train 0 starts from T0 at t=0s, stops at T3, and arrives at T5
    Train 1 starts from T0 at t=300s, stops at T4, and arrives at T5
    """  # noqa

    infra_builder = InfraBuilder()
    track_sections = [
        infra_builder.add_track_section(label='T'+str(id), length=1_000)
        for id in range(6)
    ]
    track_sections[0].add_buffer_stop(0, label='buffer_stop.0')
    track_sections[5].add_buffer_stop(
        track_sections[3].length,
        label='buffer_stop.5',
    )

    infra_builder.add_point_switch(
        track_sections[0].end(),
        track_sections[1].begin(),
        track_sections[2].begin(),
        label='DVG',
    )

    infra_builder.add_link(
        track_sections[1].end(),
        track_sections[3].begin(),
        label='L1-3',
    )
    infra_builder.add_link(
        track_sections[2].end(),
        track_sections[4].begin(),
        label='L2-4',
    )

    infra_builder.add_point_switch(
        track_sections[5].begin(),
        track_sections[3].end(),
        track_sections[4].end(),
        label='CVG',
    )

    for i in [0, 3, 4]:
        detector = track_sections[i].add_detector(
            label=f"D{i}",
            position=track_sections[i].length-180,
        )
        signal = track_sections[i].add_signal(
            detector.position-20,
            Direction.START_TO_STOP,
            is_route_delimiter=True,
            label=f"S{i}"
        )
        signal.add_logical_signal("BAL", settings={"Nf": "true"})
    for i in [1, 2, 5]:
        detector = track_sections[i].add_detector(
            label=f"D{i}",
            position=180,
        )
        signal = track_sections[i].add_signal(
            detector.position+20,
            Direction.STOP_TO_START,
            is_route_delimiter=True,
            label=f"S{i}"
        )
        signal.add_logical_signal("BAL", settings={"Nf": "true"})

    station = infra_builder.add_operational_point(label='station')
    for i in [3, 4]:
        station.add_part(
            track_sections[i],
            790,
        )

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
