import os


from railjson_generator import (
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.simulation.stop import Stop

from pyosrd.use_cases.infras.multistation import multistation
from pyosrd.infra.build import station_location

def multistation_multitrains_crossing(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
    length_between_stations: float = 1_000,
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

    infra = multistation(dir, infra_json, 3, length_between_stations)

    T = infra.track_sections

    sim_builder = SimulationBuilder()

    stop_time = 60.

    train1 = sim_builder.add_train_schedule(
        Location(T[0], 400),
        station_location(infra, 'multistation.0.s', 'V1', 200),
        station_location(infra, 'multistation.1.s', 'V1', 200),
        station_location(infra, 'multistation.2.s', 'V1', 200),
        Location(T[-1], 600),
        label='train1',
        departure_time=0,
        stops=[
            Stop(stop_time, station_location(infra, 'multistation.0.s', 'V1', 200)),
            Stop(stop_time, station_location(infra, 'multistation.1.s', 'V1', 200)),
            Stop(stop_time, station_location(infra, 'multistation.2.s', 'V1', 200)),
        ]
    )
    train1.add_standard_single_value_allowance("percentage", 5, )

    train2 = sim_builder.add_train_schedule(
        Location(T[-1], 600),
        station_location(infra, 'multistation.2.s', 'V2', -200),
        station_location(infra, 'multistation.1.s', 'V2', -200),
        station_location(infra, 'multistation.0.s', 'V2', -200),
        Location(T[0], 400),
        label='train2',
        departure_time=0,
        stops=[
           Stop(stop_time, station_location(infra, f'multistation.{2-i}.s', 'V2', -200))
            for i in range(3)
        ]
    )
    train2.add_standard_single_value_allowance("percentage", 5, )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
