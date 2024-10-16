import os

from railjson_generator import (
    SimulationBuilder,
    # Location,
)
from railjson_generator.schema.simulation.stop import Stop

from pyosrd.use_cases.infras.hamelinfra import hamelinfra
from pyosrd.infra.build import station_location


def hamelinfra_trains(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:

    infra = hamelinfra(dir, infra_json)

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        station_location(infra, 'A', 'V2', 200),
        station_location(infra, 'B', 'V1', 200),
        station_location(infra, 'C', 'V4', 200),
        station_location(infra, 'E', 'V4', 200),
        station_location(infra, 'F', 'V4', 200),
        station_location(infra, 'G', 'V2', 200),
        station_location(infra, 'J', 'V2', 200),
        station_location(infra, 'K', 'V1', 200),
        label='trainAG',
        departure_time=0.,
        stops=[
            Stop(120, station_location(infra, 'B', 'V1', 200)),
            Stop(120, station_location(infra, 'C', 'V4', 200)),
            Stop(120, station_location(infra, 'E', 'V4', 200)),
            Stop(120, station_location(infra, 'F', 'V4', 200)),
            Stop(120, station_location(infra, 'G', 'V2', 200)),
            Stop(120, station_location(infra, 'J', 'V2', 200)),
        ]
    ).add_standard_single_value_allowance("percentage", 5, )
    
    sim_builder.add_train_schedule(
        station_location(infra, 'D', 'V4'),
        station_location(infra, 'E', 'V1', 200),
        station_location(infra, 'F', 'V2', 200),
        station_location(infra, 'G', 'V4', 200),
        station_location(infra, 'H', 'V2', 200),
        station_location(infra, 'I', 'V3'),
        label='trainDI',
        departure_time=60.,
        stops=[
            Stop(120, station_location(infra, 'E', 'V1', 200)),
            Stop(120, station_location(infra, 'F', 'V2', 200)),
            Stop(120, station_location(infra, 'G', 'V4', 200)),
            Stop(120, station_location(infra, 'H', 'V2', 200)),
        ]
    ).add_standard_single_value_allowance("percentage", 5, )
    
    sim_builder.add_train_schedule(
        station_location(infra, 'G', 'V3', -200),
        station_location(infra, 'F', 'V1', -200),
        station_location(infra, 'E', 'V5', -200),
        station_location(infra, 'D', 'V4'),
        label='trainGD',
        departure_time=120.,
        stops=[
            Stop(120, station_location(infra, 'F', 'V1', -200)),
            Stop(120, station_location(infra, 'E', 'V5', -200)),
        ]
    ).add_standard_single_value_allowance("percentage", 5, )

    sim_builder.add_train_schedule(
        station_location(infra, 'I', 'V2', -200),
        station_location(infra, 'H', 'V1', -200),
        station_location(infra, 'G', 'V3', -200),
        station_location(infra, 'F', 'V1', -200),
        station_location(infra, 'E', 'V5', -200),
        station_location(infra, 'C', 'V3', -200),
        station_location(infra, 'B', 'V2', -200),
        station_location(infra, 'A', 'V1', -200),
        label='trainIA',
        departure_time=180.,
        stops=[
            Stop(120, station_location(infra, 'H', 'V1', -200),),
            Stop(120, station_location(infra, 'G', 'V3', -200),),
            Stop(120, station_location(infra, 'F', 'V1', -200),),
            Stop(120, station_location(infra, 'E', 'V5', -200),),
            Stop(120, station_location(infra, 'C', 'V3', -200),),
            Stop(120, station_location(infra, 'B', 'V2', -200),),
        ]
    ).add_standard_single_value_allowance("percentage", 5, )

    sim_builder.add_train_schedule(
        station_location(infra, 'J', 'V6'),
        station_location(infra, 'L', 'V1', 200),
        label='trainJL',
        departure_time=0.,
        stops=[],
    ).add_standard_single_value_allowance("percentage", 5, )
    
    sim_builder.add_train_schedule(
        station_location(infra, 'L', 'V1', -200),
        station_location(infra, 'J', 'V6'),
        label='trainLJ',
        departure_time=621,
        stops=[],
    ).add_standard_single_value_allowance("percentage", 5, )

    sim_builder.add_train_schedule(
        station_location(infra, 'D', 'V1'),
        station_location(infra, 'C', 'V1', -200),
        label='trainDC',
        departure_time=0,
        stops=[],
    ).add_standard_single_value_allowance("percentage", 5, )

    sim_builder.add_train_schedule(
        station_location(infra, 'C', 'V2', 200),
        station_location(infra, 'D', 'V1'),

        label='trainCD',
        departure_time=0,
        stops=[],
    ).add_standard_single_value_allowance("percentage", 5, )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
