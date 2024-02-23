import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)
from pyosrd.infra.c2xx2_infra import c2xx2_infra


def c2xx2(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    built_infra = c2xx2_infra(dir, infra_json)
    T = built_infra.track_sections

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
