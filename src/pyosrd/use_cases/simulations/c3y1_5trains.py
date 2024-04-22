import os


from railjson_generator import (
    SimulationBuilder,
    Location,
)
from pyosrd.use_cases.infras.c3y1 import c3y1


def c3y1_5trains(
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

    infra = c3y1(dir, infra_json)

    T = infra.track_sections

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
