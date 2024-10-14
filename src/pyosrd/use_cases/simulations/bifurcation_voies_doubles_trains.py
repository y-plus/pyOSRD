import os

from railjson_generator import (
    SimulationBuilder,
)

from pyosrd.use_cases.infras.bifurcation_voies_doubles import bifurcation_voies_doubles
from pyosrd.infra.build import station_location


def bifurcation_voies_doubles_trains(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:

    infra = bifurcation_voies_doubles(dir, infra_json)

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        station_location(infra,'Angouleme', 'V1'),
        station_location(infra,'Bordeaux', 'V1'),
        label='T001',
        departure_time=0,
        initial_speed=0
    ).add_standard_single_value_allowance("percentage", 5, )

    sim_builder.add_train_schedule(
        station_location(infra,'Angouleme', 'V1'),
        station_location(infra,'Cognac', 'V1'),
        label='T002',
        departure_time=90,
        initial_speed=0
    ).add_standard_single_value_allowance("percentage", 5, )

    sim_builder.add_train_schedule(
        station_location(infra,'Cognac', 'V2'),
        station_location(infra,'Angouleme', 'V2'),
        label='T003',
        departure_time=3,
        initial_speed=0
    ).add_standard_single_value_allowance("percentage", 5, )

    sim_builder.add_train_schedule(
        station_location(infra,'Bordeaux', 'V2'),
        station_location(infra,'Angouleme', 'V2'),
        label='T004',
        departure_time=120,
        initial_speed=0
    ).add_standard_single_value_allowance("percentage", 5, )



    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
