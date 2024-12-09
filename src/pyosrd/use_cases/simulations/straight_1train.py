import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.simulation.stop import Stop

from pyosrd.use_cases.infras.straight import straight
from pyosrd.infra.build import station_location

def straight_1train(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
    num_stations: int = 4,
) -> None:

    infra = straight(dir, infra_json, num_stations=num_stations)

    sim_builder = SimulationBuilder()

    START = Location(infra.track_sections[0], 460)
    END = Location(infra.track_sections[0], infra.track_sections[0].length - 60)
    first = ord('A')

    sim_builder.add_train_schedule(
        START,
        END,
        label='train1',
        departure_time=0,
        rolling_stock='short_fast_rolling_stock',
        stops=[
            Stop(120, station_location(infra, chr(first+n), 'V1'))
            for n in range(num_stations)
        ]
    ).add_standard_single_value_allowance("percentage", 15, )


    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
