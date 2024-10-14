import os


from railjson_generator import (
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.simulation.stop import Stop

from pyosrd.use_cases.infras.multistation import multistation


def multistation_multitrains_stops(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
    num_stations: int = 1,
    num_trains: int = 1,
    alternate: bool = True,
) -> None:
    """Create a serie of N stations (see build_N_dvg_station_cvg for details).

    Generate a divergence/stations/convergence sequence.

                                        stations

                                     S1┐         ┎S2
                                -----D1---(t1)----D2--
                        ┎S0   /                        \  S5┐
        ----(track_in)---D0--<DVG                    CVG>-D5-----(track_out)-
                              \      S3┐         ┎S4  /
                                -----D3----(t2)---D4--


    """  # noqa

    infra = multistation(dir, infra_json, num_stations)

    T = infra.track_sections

    sim_builder = SimulationBuilder()

    for i in range(0, num_trains):
        odds = i % 2
        locations = [Location(T[0], 400)]
        for j in range(0, num_stations):
            locations.append(Location(T[1+3*j+(odds if alternate else 0)], 500))
        locations.append(Location(T[-1], 1_000))
        train = sim_builder.add_train_schedule(
            *locations,
            label='train'+str(i),
            departure_time=i*300.+0.,
            initial_speed=15,
            stops=[
                Stop(duration=120, position=1_300+2_000*i)
                for i in range(num_stations)
            ]
        )
        train.add_standard_single_value_allowance("percentage", 5, )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
