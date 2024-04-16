import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)
from pyosrd.use_cases.infras.c1y2 import c1y2


def c1y2_4trains(
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

    All tracks are 500 m long.

    Train 0 starts from the beginning of T0 at t=0s, and arrives at the end of T1
    Train 1 starts from the end of T2 at t=100s, and arrives at the beginning of T0
    """  # noqa

    built_infra = c1y2(dir, infra_json)
    T = built_infra.track_sections

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        Location(T[0], 50.),
        Location(T[1], T[1].length-10),
        label='train0-1',
        departure_time=0,
    )

    sim_builder.add_train_schedule(
        Location(T[0], 10.),
        Location(T[2], T[2].length-10),
        label='train0-2',
        departure_time=100,
    )

    sim_builder.add_train_schedule(
        Location(T[1], T[1].length-10.),
        Location(T[0], 10),
        label='train1-0',
        departure_time=200.,
    )

    sim_builder.add_train_schedule(
        Location(T[2], T[2].length-10.),
        Location(T[0], 10),
        label='train2-0',
        departure_time=300.,
    )

    built_simulation = sim_builder.build()

    os.makedirs(dir, exist_ok=True)
    built_infra.save(os.path.join(dir, infra_json))
    built_simulation.save(os.path.join(dir, simulation_json))
