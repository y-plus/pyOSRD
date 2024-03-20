import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)
from pyosrd.infra.c3yy1yy3_infra import c3yy1yy3_infra


def c3yy1yy3(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:

    built_infra = c3yy1yy3_infra(dir, infra_json)
    T = built_infra.track_sections

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        Location(T[0], 20),
        Location(T[6], 480),
        label='train0-6',
        departure_time=0.,
    )

    sim_builder.add_train_schedule(
        Location(T[1], 20),
        Location(T[6], 480),
        label='train1-6',
        departure_time=120.,
    )

    sim_builder.add_train_schedule(
        Location(T[2], 20),
        Location(T[6], 480),
        label='train2-6',
        departure_time=240.,
    )

    sim_builder.add_train_schedule(
        Location(T[6], 480),
        Location(T[0], 20),
        label='train6-0',
        departure_time=360.,
    )
    sim_builder.add_train_schedule(
        Location(T[6], 480),
        Location(T[1], 20),
        label='train6-1',
        departure_time=480.,
    )

    sim_builder.add_train_schedule(
        Location(T[6], 480),
        Location(T[2], 20),
        label='train6-2',
        departure_time=600.,
    )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
