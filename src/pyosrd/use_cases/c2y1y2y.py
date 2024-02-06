import os

from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.infra.direction import Direction


def c2y1y2y(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
    station0 (2 tracks)                        station1 (2 tracks)                      station2 (1 track)

           ┎S0                                                      ┎S4
    (T0)-----D0-                                  --D3.1----(T4)-----D4-
                 \                         ┎S3  /                        \
               CVG>-D2-----(T2)--+--(T3)----D3-<DVG                    CVG>-D6-----(T6)-+--(T7)----D7------>
           ┎S1   /                              \                   ┎S5  /
    (T1)-----D1-                                  --D3.2----(T5)-----D5-

    All tracks are 1000m long
    Train 0 starts from T0 at t=0 and arrives at T7
    Train 1 starts from T1 at t=100 and arrives at T7
    """  # noqa

    infra_builder = InfraBuilder()

    T = [
        infra_builder.add_track_section(label='T'+str(id), length=1000)
        for id in range(8)
    ]

    for i in [0, 1]:
        T[i].add_buffer_stop(0, label=f'buffer_stop.{i}')
    for i in [7]:
        T[i].add_buffer_stop(T[i].length, label=f'buffer_stop.{i-5}')

    infra_builder.add_point_switch(
        T[2].begin(),
        T[0].end(),
        T[1].end(),
        label='CVG',
    )
    infra_builder.add_link(T[2].end(), T[3].begin())
    infra_builder.add_point_switch(
        T[3].end(),
        T[4].begin(),
        T[5].begin(),
        label='DVG',
    )
    infra_builder.add_point_switch(
        T[6].begin(),
        T[4].end(),
        T[5].end(),
        label='CVG2',
    )
    infra_builder.add_link(T[6].end(), T[7].begin())

    for i, track in enumerate(T):
        d = track.add_detector(
            label=f"D{i}",
            position=(950 if i in [0, 1, 3, 4, 5, 7] else 50),
        )
        if i in [0, 1, 3, 4, 5]:
            s = track.add_signal(
                d.position - 20,
                Direction.START_TO_STOP,
                is_route_delimiter=True,
                label=f"S{i}"
            )
            s.add_logical_signal("BAL", settings={"Nf": "true"})

    T[4].add_detector(
            label="D3.1",
            position=50,
        )
    T[5].add_detector(
            label="D3.2",
            position=50,
        )

    stations = [
        infra_builder.add_operational_point(label='station'+str(i))
        for i in range(3)
    ]
    for track in range(2):
        stations[0].add_part(T[track], 300)
    for track in range(4, 6):
        stations[1].add_part(T[track], 400)

    stations[2].add_part(T[7], 480)

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        Location(T[0], 300),
        Location(T[4], 990),
        Location(T[7], 980),
        label='train0',
        departure_time=0.,
    )
    sim_builder.add_train_schedule(
        Location(T[1], 300),
        Location(T[5], 990),
        Location(T[7], 980),
        label='train1',
        departure_time=100.,
    )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
