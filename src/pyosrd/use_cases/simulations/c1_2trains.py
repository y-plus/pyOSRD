import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)

from pyosrd.use_cases.infras.c1 import c1


def c1_2trains(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:

    infra = c1(dir, infra_json)

    sim_builder = SimulationBuilder()

    A = Location(infra.track_sections[0], 460)
    B = Location(infra.track_sections[0], 10_000 - 60)

    train1 = sim_builder.add_train_schedule(
        A,
        B,
        label='train0',
        departure_time=0,
    )
    # train1.add_stop(120., position=7_500)
    train1.add_standard_single_value_allowance("percentage", 5, )

    train2 = sim_builder.add_train_schedule(
        A,
        B,
        label='train1',
        departure_time=5*60.,
    )

    train2.add_standard_single_value_allowance("percentage", 5, )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
