import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)

from pyosrd.use_cases.infras.gare_terminus_2_4 import gare_terminus_2_4
from pyosrd.infra.build import station_location


def gare_terminus_2_4_8trains(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:

    infra = gare_terminus_2_4(dir, infra_json)

    sim_builder = SimulationBuilder()

    train1 = sim_builder.add_train_schedule(
        # station_location(infra,'stationA', 'V1'),
        Location(infra.track_sections[0], 3000),
        station_location(infra,'stationB', 'V1'),
        label='train0',
        departure_time=0,
        initial_speed=5
    )
    # train1.add_stop(120., position=0)
    train1.add_standard_single_value_allowance("percentage", 5, )



    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
