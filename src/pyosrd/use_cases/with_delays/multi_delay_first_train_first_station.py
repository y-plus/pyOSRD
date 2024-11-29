from pyosrd import OSRD


def multi_delay_first_train_first_station(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
    delays_json: str = 'delays.json',
    num_stations: int = 5,
    num_trains: int = 5,
    alternate: bool=True,
    length_between_stations: float = 1_000,
    alternate_omnibus_direct: bool = False,
    delay: float = 120,
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
    use_case = "multistation_multitrains_stops"
    sim = OSRD(
        dir=dir,
        infra_json=infra_json,
        simulation_json=simulation_json,
        delays_json=delays_json,
        simulation=use_case,
        params_use_case={
            "num_stations": num_stations,
            "num_trains": num_trains,
            "alternate": alternate,
            "length_between_stations": length_between_stations,
            "alternate_omnibus_direct": alternate_omnibus_direct,

        }
    )

    sim.reset_delays()

    # sim.add_delay("train0", 120, delay)
    sim.add_delay_at_station("train0", 'multistation.0.s', delay)
    # sim.add_delays_in_results()
