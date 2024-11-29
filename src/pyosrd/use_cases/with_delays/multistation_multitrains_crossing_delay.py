from pyosrd import OSRD


def multistation_multitrains_crossing_delay(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
    delays_json: str = 'delays.json',
    length_between_stations: float = 1_000,
    delay: float = 120,
) -> None:
    
    use_case = "multistation_multitrains_crossing"
    sim = OSRD(
        dir=dir,
        infra_json=infra_json,
        simulation_json=simulation_json,
        delays_json=delays_json,
        simulation=use_case,
        params_use_case={
            "length_between_stations": length_between_stations,
        }
    )

    sim.reset_delays()

    # sim.add_delay("train0", 120, delay)
    sim.add_delay_at_station(0, 'multistation.0.s', delay)
    # sim.add_delays_in_results()
