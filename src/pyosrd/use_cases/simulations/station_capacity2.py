import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)
from pyosrd.infra.station_capacity2_infra import station_capacity2_infra


def station_capacity2(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
    Train 0 starts from T0 at t=0s, stops at T3, and arrives at T5
    Train 1 starts from T0 at t=300s, stops at T4, and arrives at T5
    """  # noqa

    built_infra = station_capacity2_infra(dir, infra_json)

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        Location(built_infra.track_sections[0], 10.),
        Location(built_infra.track_sections[3], 790),
        Location(built_infra.track_sections[5], 990),
        label='train0',
        departure_time=0.,
    )

    sim_builder.add_train_schedule(
        Location(built_infra.track_sections[0], 10.),
        Location(built_infra.track_sections[4], 790),
        Location(built_infra.track_sections[5], 990),
        label='train1',
        departure_time=300.,
    )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
