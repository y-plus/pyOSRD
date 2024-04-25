import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)
from pyosrd.use_cases.infras.c1_with_blocks import c1_with_blocks


def c1_with_blocks_3trains(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
                ┎SA SA.1┐       ┎S2.0 S2.1┐       ┎S8.0 S8.1┐     ┎SB SB.1┐
     (T)<---A------DA----------------D2-----...--------D8-------------DB------B---->

    10 km long, Detectors D2,D4,D6,D8 detectors every 2km
    Trains start from A and arrive at B
    """  # noqa

    infra_builder = c1_with_blocks(dir, infra_json)
    T = infra_builder.track_sections

    A = Location(T[0], 460)
    B = Location(T[0], 10_000 - 60)

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
        departure_time=3*60,
    )

    train2.add_standard_single_value_allowance("percentage", 5, )

    train3 = sim_builder.add_train_schedule(
        A,
        B,
        label='Third train',
        departure_time=6*60,
    )

    train3.add_standard_single_value_allowance("percentage", 5, )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
