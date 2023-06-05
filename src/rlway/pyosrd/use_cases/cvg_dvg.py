import os

from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.infra.direction import Direction


def cvg_dvg(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
    station0 (2 tracks)                        station1 (2 tracks)

    (T0)--S0-D0-                                  -S4-D4-(T4)-->
                 \                              /
             (CVG)>-(T2)---------o--S3-D3-(T3)-<(DVG)
                 /                              \
    (T1)--S1-D1-                                  -S5-D5-(T5)-->

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

    infra_builder.add_link(T[2].end(), T[3].begin())
    infra_builder.add_point_switch(
        T[2].begin(),
        T[0].end(),
        T[1].end(),
        label='CVG',
    )
    infra_builder.add_point_switch(
        T[3].end(),
        T[4].begin(),
        T[5].begin(),
        label='DVG',
    )

    detectors = {
        i: T[i].add_detector(label=f"D{i}", position=450)
        for i in [0, 1, 3, 4, 5]
    }
    S = [
        T[i].add_signal(
            detector.position-20,
            Direction.START_TO_STOP,
            detector,
            label=f"S{i}"
        )
        for i, detector in detectors.items()
    ]
    for signal in S:
        signal.add_logical_signal("BAL", settings={"Nf": "true"})

    stations = [
        infra_builder.add_operational_point(label='station'+str(i))
        for i in range(2)
    ]
    for track in range(2):
        stations[0].add_part(T[track], 300)
    for track in range(4, 6):
        stations[1].add_part(T[track], 480)

    built_infra = infra_builder.build()

    sim_builder = SimulationBuilder(built_infra)

    for train_id in range(2):
        sim_builder.add_train_schedule(
            Location(built_infra.track_sections[train_id], 300),
            Location(built_infra.track_sections[train_id+4], 480),
            label='train'+str(train_id),
            departure_time=train_id*100.
        )

    built_simulation = sim_builder.build()

    os.makedirs(dir, exist_ok=True)
    built_infra.save(os.path.join(dir, infra_json))
    built_simulation.save(os.path.join(dir, simulation_json))
