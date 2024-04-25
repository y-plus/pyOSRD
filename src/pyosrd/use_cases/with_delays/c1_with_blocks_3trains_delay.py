from pyosrd import OSRD


def c1_with_blocks_3trains_delay(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
    delays_json: str = 'delays.json'
) -> None:
    """
    See c1_with_blocks_3trains_delay.py in simulations
    to check the trains and infra.

    In this test case the first train is delayed for 150 seconds
    """
    simulation = "c1_with_blocks_3trains"
    sim = OSRD(
        dir=dir,
        infra_json=infra_json,
        simulation_json=simulation_json,
        delays_json=delays_json,
        simulation=simulation
    )

    sim.reset_delays()
    sim.add_delay(0, time_threshold=0, delay=150.)
    sim.add_delays_in_results()
