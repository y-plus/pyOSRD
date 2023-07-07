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
                      S1s┐           ┎S1e
                     -D1s-(T1)---o---D1e--
             ┎S0e  /                       \   S3s┐
    --(T0)----D0e-<DVG                   CVG>--D3s----(T3)--->
                   \  S2s┐          ┎S2e   /
                     -D2s-(T2)---o---D2e--

    All tracks are 1 km long
    Train 0 starts from T0 at t=0s, stops at T1, and arrives at T3
    Train 1 starts from T0 at t=300s, stops at T2, and arrives at T3
    """  # noqa

    infra_builder = InfraBuilder()
    track_sections = [
        infra_builder.add_track_section(label='T'+str(id), length=1_000)
        for id in range(4)
    ]
    track_sections[0].add_buffer_stop(0, label='buffer_stop.0')
    track_sections[3].add_buffer_stop(
        track_sections[3].length,
        label='buffer_stop.1',
    )

    infra_builder.add_point_switch(
        track_sections[0].end(),
        track_sections[1].begin(),
        track_sections[2].begin(),
        label='DVG',
    )

    infra_builder.add_point_switch(
        track_sections[3].begin(),
        track_sections[1].end(),
        track_sections[2].end(),
        label='CVG',
    )

    detectors = [
        track_sections[i].add_detector(
            label=f"D{i}e",
            position=track_sections[i].length-180,
        )
        for i in [0, 1, 2]
    ] + [
        track_sections[i].add_detector(
            label=f"D{i}s",
            position=180.,
        )
        for i in [1, 2, 3]
    ]
    signals = [
        track_sections[i].add_signal(
            detectors[i].position-20,
            Direction.START_TO_STOP,
            detectors[i],
            label=f"S{i}e"
        )
        for i in [0, 1, 2]
    ] + [
        track_sections[i].add_signal(
            detectors[i].position+20,
            Direction.STOP_TO_START,
            detectors[i],
            label=f"S{i}s",
        )
        for i in [1, 2, 3]
    ]
    for signal in signals:
        signal.add_logical_signal("BAL", settings={"Nf": "true"})

    station = infra_builder.add_operational_point(label='station')
    for i in [1, 2]:
        station.add_part(
            track_sections[i],
            track_sections[i].length-210,
        )

    os.makedirs(dir, exist_ok=True)

    try:
        built_infra = infra_builder.build()
        built_infra.save(os.path.join(dir, infra_json))
    except RuntimeError as e:
        print('infra: ', e)

    try:
        sim_builder = SimulationBuilder()

        sim_builder.add_train_schedule(
            Location(built_infra.track_sections[0], 10.),
            Location(built_infra.track_sections[1], 790),
            Location(built_infra.track_sections[3], 990),
            label='train0',
            departure_time=0.,
        )

        sim_builder.add_train_schedule(
            Location(built_infra.track_sections[0], 10.),
            Location(built_infra.track_sections[2], 790),
            Location(built_infra.track_sections[3], 990),
            label='train1',
            departure_time=300.,
        )

        built_simulation = sim_builder.build()
        built_simulation.save(os.path.join(dir, simulation_json))
    except RuntimeError as e:
        print('simulation: ', e)
