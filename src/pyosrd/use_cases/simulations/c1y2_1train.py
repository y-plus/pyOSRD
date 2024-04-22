import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)

from pyosrd.use_cases.infras.c1y2 import c1y2


def c1y2_1train(
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

    - Train 0 starts from the beginning of T0 at t=0s,
        and arrives at the end of T1
    """  # noqa

    built_infra = c1y2(dir, infra_json)
    T = built_infra.track_sections

    sim_builder = SimulationBuilder()

    train1 = sim_builder.add_train_schedule(
        Location(T[0], 50.),
        Location(T[1], T[1].length-10),
        label='train0',
        departure_time=0,
    )
    train1.add_standard_single_value_allowance("percentage", 5, )

    built_simulation = sim_builder.build()

    os.makedirs(dir, exist_ok=True)
    built_simulation.save(os.path.join(dir, simulation_json))
