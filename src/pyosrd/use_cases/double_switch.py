import os

from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    Location,
)

from railjson_generator.schema.infra.direction import Direction


def double_switch(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
    stationA(3 tracks)               stationB (1 track)

            ┎S0                S4┐
    (T0)-----D0------SW0-------D4---------(T4)-->              
            ┎S1     D3/ (T3) 
    (T1)-----D1-----SW1
            ┎S2     / 
    (T2)-----D2-----

    Train 0 starts from T0 at t=0 and arrives at T4
    Train 1 starts from T1 at t=100 and arrives at T5
    """  # noqa

    infra_builder = InfraBuilder()

    track_lengths = [
        504,
        500,
        500,
        5,
        1_000,
    ]
    T = [
        infra_builder.add_track_section(
            label='T'+str(i),
            length=track_lengths[i],
        )
        for i, _ in enumerate(track_lengths)
    ]

    for i in [0, 1, 2]:
        T[i].add_buffer_stop(0, label=f'buffer_stop.{i}')
    for i in [4]:
        T[i].add_buffer_stop(T[i].length, label=f'buffer_stop.{i}')

    infra_builder.add_point_switch(
        T[4].begin(),
        T[0].end(),
        T[3].end(),
        label='SW0',
    )
    infra_builder.add_point_switch(
        T[3].begin(),
        T[1].end(),
        T[2].end(),
        label='SW1',
    )

    T[0].add_detector(label='D0', position=480)
    T[0].add_signal(
        460,
        is_route_delimiter=True,
        label='S0',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[1].add_detector(label='D1', position=480)
    T[1].add_signal(
        460,
        is_route_delimiter=True,
        label='S1',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[2].add_detector(label='D2', position=480)
    T[2].add_signal(
        460,
        is_route_delimiter=True,
        label='S2',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[4].add_detector(label='D4', position=20)
    T[4].add_signal(
        40,
        is_route_delimiter=True,
        label='S4',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[3].add_detector(label='D3', position=2.5)

    stationA = infra_builder.add_operational_point(label='stationA')
    for track in range(3):
        stationA.add_part(T[track], 20)

    infra_builder.add_operational_point(label='stationB').add_part(T[4], 980)

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        Location(T[0], 20),
        Location(T[4], 980),
        label='train0-4',
        departure_time=0.,
    )

    sim_builder.add_train_schedule(
        Location(T[1], 20),
        Location(T[4], 980),
        label='train1-4',
        departure_time=120.,
    )

    sim_builder.add_train_schedule(
        Location(T[2], 20),
        Location(T[4], 980),
        label='train2-4',
        departure_time=240.,
    )

    sim_builder.add_train_schedule(
        Location(T[4], 980),
        Location(T[0], 20),
        label='train4-0',
        departure_time=360.,
    )
    sim_builder.add_train_schedule(
        Location(T[4], 980),
        Location(T[1], 20),
        label='train4-1',
        departure_time=480.,
    )

    sim_builder.add_train_schedule(
        Location(T[4], 980),
        Location(T[2], 20),
        label='train4-2',
        departure_time=600.,
    )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
