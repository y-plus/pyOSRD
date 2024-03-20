import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)
from pyosrd.infra.c2y1y2y_infra import c2y1y2y_infra


def c2y1y2y(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:

    infra = c2y1y2y_infra(dir, infra_json)
    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        Location(infra.track_sections[0], 300),
        Location(infra.track_sections[4], 990),
        Location(infra.track_sections[7], 980),
        label='train0',
        departure_time=0.,
    )
    sim_builder.add_train_schedule(
        Location(infra.track_sections[1], 300),
        Location(infra.track_sections[5], 990),
        Location(infra.track_sections[7], 980),
        label='train1',
        departure_time=100.,
    )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
