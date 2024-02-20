import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)
from pyosrd.infra.c2y11s_infra import c2y11s_infra


def c2y11s(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
    Train 0 starts from T0 at t=0 and arrives at T2
    Train 1 starts from T1 at t=100 and arrives at T2
    """  # noqa

    built_infra = c2y11s_infra(dir, infra_json)
    T = built_infra.track_sections

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        Location(T[0], 20),
        Location(T[2], 4_990),
        label='train0',
        departure_time=0.,
    )

    sim_builder.add_train_schedule(
        Location(T[1], 20),
        Location(T[2], 4_990),
        label='train1',
        departure_time=120.,
        # rolling_stock='short_fast_rolling_stock',
    )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
