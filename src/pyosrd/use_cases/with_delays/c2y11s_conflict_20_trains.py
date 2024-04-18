from pyosrd import OSRD


def c2y11s_conflict_20_trains(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
    delays_json: str = 'delays.json'
  ) -> None:
    """
    See c2y11s.py in simulations to check the infra.

      TODO
    """
    simulation = 'c2y11s_2trains'
    sim = OSRD(
        dir=dir,
        infra_json=infra_json,
        simulation_json=simulation_json,
        delays_json=delays_json,
        simulation=simulation
    )

    for i in [1, 2, 3]:
        sim.copy_train('train0', f'train0.{i}', departure_time=300.*i)
        sim.copy_train('train1', f'train1.{i}', departure_time=100.+300.*i)

    sim.reset_delays()
    sim.add_delay('train0', time_threshold=70, delay=100.)
    sim.add_delays_in_results()
