from pyosrd import OSRD
from random import Random


def multistation_multitrains_randomdelay(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
    delays_json: str = 'delays.json',
    num_stations: int = 1,
    num_trains: int = 1,
    delay_seed: int = 42
) -> None:
    """Create a multi train multi station simulation and add random delays.

    Delays are not completely random and follow the rule :
    - Number of delayed train is between 1 and min(3, num_trains)
    - For each delay
      - train is randomly chosen
      - the time threshold is between 0 and 100 x num_stations
      - Duration delay is between 50 and 200

    Parameters
    ----------
    dir : str
        _description_
    infra_json : str, optional
        _description_, by default 'infra.json'
    simulation_json : str, optional
        _description_, by default 'simulation.json'
    delays_json : str, optional
        _description_, by default 'delays.json'
    num_stations : int, optional
        _description_, by default 1
    num_trains : int, optional
        _description_, by default 1
    delay_seed : int, optional
        _description_, by default 42
    """
    use_case = "multistation_multitrains"
    sim = OSRD(
        dir=dir,
        infra_json=infra_json,
        simulation_json=simulation_json,
        delays_json=delays_json,
        simulation=use_case,
        params_use_case={
            "num_stations": num_stations,
            "num_trains": num_trains
        }
    )

    sim.reset_delays()

    gen = Random(delay_seed)
    num_delayed_trains = gen.randint(1, num_trains)

    for _ in range(0, num_delayed_trains):
        delayed_train = gen.randint(0, num_trains-1)
        duration = (
            sim.last_arrival_times[delayed_train]
            - sim.departure_times[delayed_train]
        )
        label = f'train{delayed_train}'
        time_threshold = (
            sim.departure_times[delayed_train]
            + gen.randint(0, int(duration))
        )
        delay = gen.randint(200, 600)
        sim.add_delay(label, time_threshold=time_threshold, delay=delay)

    sim.add_delays_in_results()
