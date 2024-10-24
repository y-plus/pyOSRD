from pyosrd import OSRD


def multistation_multitrains_big_delays(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
    delays_json: str = 'delays.json',
    num_stations: int = 5,
    num_trains: int = 5
) -> None:
    """Create a multi train multi station simulation and add big delays.

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

    sim.add_delay("train0", 100, 850)
    if num_trains > 10:
        sim.add_delay("train10", 2100, 850)
    if num_trains > 20:
        sim.add_delay("train20", 4100, 850)

    sim.add_delays_in_results()
