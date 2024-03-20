import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)

from pyosrd.infra.c1_with_blocks_infra import c1_with_blocks_infra


def c1_with_blocks(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    built_infra = c1_with_blocks_infra(dir, infra_json)

    A = Location(built_infra.track_sections[0], 460)
    B = Location(built_infra.track_sections[0], 10_000 - 60)

    sim_builder = SimulationBuilder()

    train1 = sim_builder.add_train_schedule(
        A,
        B,
        label='First train',
        departure_time=0,
    )
    # train1.add_stop(120., position=7_500)
    train1.add_standard_single_value_allowance("percentage", 5, )

    train2 = sim_builder.add_train_schedule(
        A,
        B,
        label='Second train',
        departure_time=3*60.,
    )

    train2.add_standard_single_value_allowance("percentage", 5, )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
