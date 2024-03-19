import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)

from pyosrd.infra.straight_line_infra import straight_line_infra


def straight_line(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
    Train #1 start from A and arrive at B
    Train #2 start from B and arrive at A
    The two train collide !
    """  # noqa

    built_infra = straight_line_infra(dir, infra_json)
    T = built_infra.track_sections

    A = Location(T[0], 460)
    B = Location(T[0], 10_000 - 460)

    sim_builder = SimulationBuilder()

    train1 = sim_builder.add_train_schedule(
        A,
        B,
        label='train0',
        departure_time=0,
    )
    train1.add_stop(120., position=7_500)
    train1.add_standard_single_value_allowance("percentage", 5, )

    train2 = sim_builder.add_train_schedule(
        B,
        A,
        label='train1',
        departure_time=7*60.,
    )

    train2.add_standard_single_value_allowance("percentage", 5, )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
