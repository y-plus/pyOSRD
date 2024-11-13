import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)

from railjson_generator.schema.simulation.stop import Stop

from pyosrd.use_cases.infras.c1yy3yy1 import c1yy3yy1
from pyosrd.infra.build import station_location


def c1yy3yy1_3trains(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:

    infra = c1yy3yy1(dir, infra_json)

    sim_builder = SimulationBuilder()

    START = Location(infra.track_sections[0], 100)
    END = Location(infra.track_sections[-1], 400)
    sim_builder.add_train_schedule(
        START,
        station_location(infra, 'station', 'T2'),
        END,
        label='train0',
        departure_time=0,
        stops=[
            Stop(120, station_location(infra, 'station', 'T2', 200))
        ]

    ).add_standard_single_value_allowance("percentage", 5, )

    sim_builder.add_train_schedule(
        START,
        station_location(infra, 'station', 'T3'),
        END,
        label='train1',
        departure_time=120,
        stops=[
            Stop(120, station_location(infra, 'station', 'T3', 200))
        ]

    ).add_standard_single_value_allowance("percentage", 5, )

    sim_builder.add_train_schedule(
        START,
        station_location(infra, 'station', 'T2'),
        END,
        label='train2',
        departure_time=240,
        stops=[
            Stop(120, station_location(infra, 'station', 'T2', 200))
        ]

    ).add_standard_single_value_allowance("percentage", 5, )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
