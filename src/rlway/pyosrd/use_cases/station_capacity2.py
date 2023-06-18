import os

from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.infra.direction import Direction


def station_capacity2(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
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

    infra_builder.add_link(track_sections[1].end(), track_sections[3].begin())
    infra_builder.add_link(track_sections[2].end(), track_sections[4].begin())

    infra_builder.add_point_switch(
        track_sections[5].begin(),
        track_sections[3].end(),
        track_sections[4].end(),
        label='CVG',
    )

    detectors = [
        track_sections[i].add_detector(
            label=f"D{i}",
            position=track_sections[i].length-180,
        )
        for i in [0, 3, 4]
    ] + [
        track_sections[i].add_detector(
            label=f"D{i}",
            position=180.,
        )
        for i in [1, 2, 5]
    ]
    signals = [
        track_sections[i].add_signal(
            detectors[i].position-20,
            Direction.START_TO_STOP,
            detectors[i],
            label=f"S{i}"
        )
        for i in [0, 3, 4]
    ] + [
        track_sections[i].add_signal(
            detectors[i].position+20,
            Direction.STOP_TO_START,
            detectors[i],
            label=f"S{i}",
        )
        for i in [1, 2, 5]
    ]
    for signal in signals:
        signal.add_logical_signal("BAL", settings={"Nf": "true"})

    station = infra_builder.add_operational_point(label='station')
    for i in [3, 4]:
        station.add_part(
            track_sections[i],
            signals[i].position-10,
        )

    os.makedirs(dir, exist_ok=True)

    try:
        built_infra = infra_builder.build()
        built_infra.save(os.path.join(dir, infra_json))
    except RuntimeError as e:
        print('infra: ', e)

    try:
        sim_builder = SimulationBuilder(built_infra)

        sim_builder.add_train_schedule(
            Location(built_infra.track_sections[0], 10.),
            Location(built_infra.track_sections[3], 790),
            Location(built_infra.track_sections[5], 990),
            label='train0',
            departure_time=0.,
        )

        sim_builder.add_train_schedule(
            Location(built_infra.track_sections[0], 10.),
            Location(built_infra.track_sections[4], 790),
            Location(built_infra.track_sections[5], 990),
            label='train1',
            departure_time=300.,
        )

        built_simulation = sim_builder.build()
        built_simulation.save(os.path.join(dir, simulation_json))
    except RuntimeError as e:
        print('simulation: ', e)