import os


from railjson_generator import (
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.simulation.stop import Stop

from pyosrd.infra.build import station_location
from pyosrd.use_cases.infras.voie_unique import voie_unique


def voie_unique_circulations(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
    num_stations: int = 3,
    num_blocks_between_stations: int = 5,
    num_trains: int = 1,
    alternate: bool = False,
    crossing: bool = False,
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
    if crossing:
        num_stations = 3
    infra = voie_unique(
        dir,
        infra_json,
        num_stations,
        num_blocks_between_stations,
    )

    sim_builder = SimulationBuilder()
    last_station = chr(ord('A')+num_stations-1)
    if crossing:
        alternate = True
        departure_times = [0+600*(i) if i%2==0 else 600*(i-1) for i in range(num_trains)]
    else:
        departure_times = [300*i for i in range(num_trains)]

    for i in range(num_trains):
        if alternate:
            platform = f'V{i%2+1}'
        else:
            platform = 'V1'
        intermediate_locations = [
            station_location(infra, chr(ord('A')+station-1), platform)
            for station in range(2,num_stations)
        ]
        intermediate_stops = [
            Stop(120, location) for location in intermediate_locations
        ]

        locations = (
                [station_location(infra, 'A', platform)]
                + intermediate_locations
                + [station_location(infra, last_station, platform, 100)]
        )
        stops = (
            [Stop(120, station_location(infra, 'A', platform))]
            + intermediate_stops
            + [Stop(120, station_location(infra, last_station, platform, -100))]
        )
        if crossing and i%2 == 1:
            locations = (
                [station_location(infra, last_station, 'V1')]
                + intermediate_locations[::-1]
                + [station_location(infra, 'A', 'V1', 100)]
            )
            stops = (
                [Stop(120, station_location(infra, last_station, 'V1'))]
                + intermediate_stops[::-1]
                + [Stop(120, station_location(infra, 'A', 'V1', -100))]
            )

        sim_builder.add_train_schedule(
            *locations,
            label=f'train{str(i).zfill(2)}',
            departure_time=departure_times[i],
            initial_speed=0,
            stops=stops,
            rolling_stock='hamelin_rolling_stock'
        ).add_standard_single_value_allowance("percentage", 5, )



    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
