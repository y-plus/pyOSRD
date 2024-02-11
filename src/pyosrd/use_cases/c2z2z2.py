import os

from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.infra.direction import Direction


def c2z2z2(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
    station0 (2 tracks)                        station1 (2 tracks)

            ┎S0      S2┐               ┎S2b        S4┐
    (T0)-----D0--SW0-D2-----(T2)--------D2b--SW4---D4---------(T4)-->              
            ┎S1 D6/ S3┐                   ┎S3b \D7   S5┐
    (T1)-----D1-SW1-D3---------(T3)--------D3b--SW5--D5------(T5)-->

    Train 0 starts from T0 at t=0 and arrives at T4
    Train 1 starts from T1 at t=100 and arrives at T5
    """  # noqa

    infra_builder = InfraBuilder()

    track_lengths = [
        504,
        500,
        992,
        1_000,
        504,
        500,
        5,
        5,
    ]
    T = [
        infra_builder.add_track_section(
            label='T'+str(i),
            length=track_lengths[i],
        )
        for i in range(8)
    ]

    for i in [0, 1]:
        T[i].add_buffer_stop(0, label=f'buffer_stop.{i}')
    for i in [4, 5]:
        T[i].add_buffer_stop(T[i].length, label=f'buffer_stop.{i-2}')

    infra_builder.add_point_switch(
        T[2].begin(),
        T[0].end(),
        T[6].end(),
        label='SW0',
    )
    infra_builder.add_point_switch(
        T[2].end(),
        T[4].begin(),
        T[7].begin(),
        label='SW4',
    )
    infra_builder.add_point_switch(
        T[1].end(),
        T[6].begin(),
        T[3].begin(),
        label='SW1',
    )
    infra_builder.add_point_switch(
        T[5].begin(),
        T[3].end(),
        T[7].end(),
        label='SW5',
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

    T[2].add_detector(label='D2', position=20)
    T[2].add_signal(
        40,
        is_route_delimiter=True,
        label='S2',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[2].add_detector(label='D2b', position=980)
    T[2].add_signal(
        960,
        is_route_delimiter=True,
        label='S2b',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[3].add_detector(label='D3', position=20)
    T[3].add_signal(
        40,
        is_route_delimiter=True,
        label='S3',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[3].add_detector(label='D3b', position=980)
    T[3].add_signal(
        960,
        is_route_delimiter=True,
        label='S3b',
        direction=Direction.START_TO_STOP,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[4].add_detector(label='D4', position=20)
    T[4].add_signal(
        40,
        is_route_delimiter=True,
        label='S4',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[5].add_detector(label='D5', position=20)
    T[5].add_signal(
        40,
        is_route_delimiter=True,
        label='S5',
        direction=Direction.STOP_TO_START,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T[6].add_detector(label='D6', position=2.5)
    T[7].add_detector(label='D7', position=2.5)

    stations = [
        infra_builder.add_operational_point(label='station'+str(i))
        for i in range(2)
    ]
    for track in range(2):
        stations[0].add_part(T[track], 300)
    for track in range(4, 6):
        stations[1].add_part(T[track], 480)

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        Location(T[0], 300),
        Location(T[4], 490),
        label='train0-4',
        departure_time=0.,
    )
    sim_builder.add_train_schedule(
        Location(T[1], 300),
        Location(T[3], 300),
        Location(T[5], 480),
        label='train1-3-5',
        departure_time=120.,
    )
    sim_builder.add_train_schedule(
        Location(T[0], 300),
        Location(T[5], 490),
        label='train0-5',
        departure_time=240.,
    )
    sim_builder.add_train_schedule(
        Location(T[1], 300),
        Location(T[4], 480),
        label='train1-4',
        departure_time=360.,
    )
    sim_builder.add_train_schedule(
        Location(T[1], 300),
        Location(T[2], 300),
        Location(T[5], 480),
        label='train1-2-5',
        departure_time=480.,
    )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
