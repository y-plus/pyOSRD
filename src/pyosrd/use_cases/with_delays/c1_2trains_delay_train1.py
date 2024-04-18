from pyosrd import OSRD


def c1_2trains_delay_train1(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
    delays_json: str = 'delays.json'
) -> None:
    """
    See c1.py in simulations simulations to check the trains and infra.

    In this test case the train0 is delay for 120 seconds,
    10 seconds after its start
    """
    simulation = "c1_2trains"
    sim = OSRD(
        dir=dir,
        infra_json=infra_json,
        simulation_json=simulation_json,
        delays_json=delays_json,
        simulation=simulation
    )

    sim.reset_delays()
    sim.add_delay('train0', time_threshold=10, delay=120.)
    sim.add_delays_in_results()
