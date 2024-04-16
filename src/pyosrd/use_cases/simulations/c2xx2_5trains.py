import os


from railjson_generator import (
    SimulationBuilder,
    Location,
)

from pyosrd.use_cases.infras.c2xx2 import c2xx2


def c2xx2_5trains(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
    station0 (2 tracks)                        station1 (2 tracks)

                  ┎S0              S2┐
    (T0)-----------D0--------------D2------(T2)-->
                      \     /
                         SW
                ┎S1   /     \      S3┐
    (T1)---------D1----------------D3------(T3)-->

    """  # noqa

    infra = c2xx2(dir, infra_json)

    T = infra.track_sections

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        Location(T[0], 50),
        Location(T[2], 950),
        label='train0-2',
        departure_time=0.,
    )
    sim_builder.add_train_schedule(
        Location(T[1], 50),
        Location(T[3], 950),
        label='train1-3',
        departure_time=120.,
    )
    sim_builder.add_train_schedule(
        Location(T[0], 50),
        Location(T[3], 950),
        label='train0-3',
        departure_time=240.,
    )
    sim_builder.add_train_schedule(
        Location(T[1], 50),
        Location(T[2], 950),
        label='train1-2',
        departure_time=360.,
    )
    sim_builder.add_train_schedule(
        Location(T[3], 950),
        Location(T[0], 50),
        label='train3-0',
        departure_time=480.,
    )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
