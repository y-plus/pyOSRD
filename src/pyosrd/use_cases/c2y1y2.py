import os

from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    Location,
)

from railjson_generator.schema.infra.direction import Direction


def c2y1y2(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
    station0 (2 tracks)                        station1 (2 tracks)

           ┎S0                                      S4┐
    (T0)-----D0-                                  --D4---------(T4)-->
                 \  S2┐                    ┎S3  /
               CVG>-D2-----(T2)--+--(T3)----D3-<DVG
           ┎S1   /                              \   S5┐
    (T1)-----D1-                                  --D5---------(T5)-->

    All tracks are 500m long
    Train 0 starts from T0 at t=0 and arrives at T4
    Train 1 starts from T1 at t=100 and arrives at T5
    """  # noqa

    infra_builder = InfraBuilder()

    T = [
        infra_builder.add_track_section(label='T'+str(id), length=500)
        for id in range(6)
    ]

    for i in [0, 1]:
        T[i].add_buffer_stop(0, label=f'buffer_stop.{i}')
    for i in [4, 5]:
        T[i].add_buffer_stop(T[i].length, label=f'buffer_stop.{i-2}')

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

    for i, track in enumerate(T):
        d = track.add_detector(
            label=f"D{i}",
            position=(450 if i in [0, 1, 3] else 50),
        )
        s = T[i].add_signal(
            d.position + (-20 if i in [0, 1, 3] else 20),
            (
                Direction.START_TO_STOP
                if i in [0, 1, 3] else Direction.STOP_TO_START
            ),
            is_route_delimiter=True,
            label=f"S{i}"
        )
        s.add_logical_signal("BAL", settings={"Nf": "true"})

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
        label='train0',
        departure_time=0.,
    )
    sim_builder.add_train_schedule(
        Location(T[1], 300),
        Location(T[5], 480),
        label='train1',
        departure_time=100.,
    )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
