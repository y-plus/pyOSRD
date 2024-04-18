from pyosrd import OSRD


def c1y2_2trains_no_conflict(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
    delays_json: str = 'delays.json'
  ) -> None:
    """
    See c1y2_2trains.py in simulations to check the infra.

    In this test case we have two trains going to different branch from
      a divergence.
    The leading train is delayed after the divergence therefore no impact
      should be seen on the trailing train.
    """
    simulation = 'c1y2_2trains'
    sim = OSRD(
        dir=dir,
        infra_json=infra_json,
        simulation_json=simulation_json,
        delays_json=delays_json,
        simulation=simulation
    )

    sim.reset_delays()
    sim.add_delay('train0', time_threshold=40, delay=50.)
    sim.add_delays_in_results()
