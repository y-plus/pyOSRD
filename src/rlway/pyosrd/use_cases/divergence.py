import os

from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.infra.direction import Direction


def divergence(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
                         S1┐
                        -D1---------(T1)-->
                ┎S0   / 
    --(T0)--------D0-<(DVG)            
                      \  S2┐ 
                        -D2----------(T2)-->

    All tracks are 10 km long
    Train 0 starts from the beginning of T0 at t=0s, and arrives at the end of T1
    Train 1 starts from the end of T2 at t=60s, and arrives at the beginning of T0
    """  # noqa

    infra_builder = InfraBuilder()

    T = [
        infra_builder.add_track_section(label="T"+str(id), length=10_000)
        for id in range(3)
    ]
    T[0].add_buffer_stop(0, label="buffer_stop.0")

    for i in [1, 2]:
        T[i].add_buffer_stop(T[i].length, label=f"buffer_stop.{i}")

    infra_builder.add_point_switch(
        T[0].end(),
        T[1].begin(),
        T[2].begin(),
        label="DVG",
    )
    detectors = [T[0].add_detector(label="D0", position=T[0].length-180)]
    detectors += [
        T[i].add_detector(
            label=f"D{i}",
            position=180,
        )
        for i in [1, 2]
    ]
    signals = [
        T[0].add_signal(
            detectors[0].position-20,
            Direction.START_TO_STOP,
            detectors[0],
            label="S0"
        ),
    ]
    signals += [
        T[i].add_signal(
            detectors[i].position+20,
            Direction.STOP_TO_START,
            detectors[i],
            label=f"S{i}"
        )
        for i in [1, 2]
    ]

    for signal in signals:
        signal.add_logical_signal("BAL", settings={"Nf": "true"})

    built_infra = infra_builder.build()

    sim_builder = SimulationBuilder(built_infra)

    sim_builder.add_train_schedule(
        Location(T[0], 50.),
        Location(T[1], T[1].length-50),
        label='train0',
        departure_time=0,
    )

    sim_builder.add_train_schedule(
        Location(T[2], T[1].length-50.),
        Location(T[0], 50),
        label='train1',
        departure_time=100.,
    )

    built_simulation = sim_builder.build()

    os.makedirs(dir, exist_ok=True)
    built_infra.save(os.path.join(dir, infra_json))
    built_simulation.save(os.path.join(dir, simulation_json))
