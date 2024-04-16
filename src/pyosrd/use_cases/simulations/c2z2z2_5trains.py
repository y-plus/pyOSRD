import os


from railjson_generator import (
    SimulationBuilder,
    Location,
)
from pyosrd.use_cases.infras.c2z2z2 import c2z2z2


def c2z2z2_5trains(
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

    infra = c2z2z2(dir, infra_json)

    T = infra.track_sections

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
