import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)
from pyosrd.infra.cvg_dvg_infra import cvg_dvg_infra


def cvg_dvg(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
    Train 0 starts from T0 at t=0 and arrives at T4
    Train 1 starts from T1 at t=100 and arrives at T5
    """  # noqa

    built_infra = cvg_dvg_infra(dir, infra_json)
    T = built_infra.track_sections

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
