from pyosrd.use_cases.simulations.c1_2trains import c1_2trains
from pyosrd.delays import (
    add_delay_to_json,
    reset_delays_in_json
)


def c1_2trains_delay_train1(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
    delays_json: str = 'delays.json'
) -> None:
    """
    See c1.py in use_cases simulations to check the trains and infra.

    In this test case the train0 is delay for 120 seconds,
    10 seconds after its start
    """
    c1_2trains(dir, infra_json, simulation_json)

    reset_delays_in_json(dir, delays_json)
    add_delay_to_json(
        dir,
        delays_json,
        'train0',
        time_threshold=10,
        delay=120.
    )
