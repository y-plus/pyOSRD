import json
import os

from railjson_generator import (
    SimulationBuilder,
    # Location,
)
from railjson_generator.schema.simulation.stop import Stop

from pyosrd.use_cases.infras.hamelinfra import hamelinfra
from pyosrd.infra.build import station_location

from pyosrd.utils import hour_to_seconds

def hamelinfra_circulations(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:

    infra = hamelinfra(dir, infra_json)

    sim_builder = SimulationBuilder()

    n_hours = 4
    start_hour = 8

    for i in range(n_hours):

        # Frequence 60 min

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V1'),
            station_location(infra, 'E', 'V1', 200),
            station_location(infra, 'F', 'V1', 200),
            station_location(infra, 'G', 'V1', 200),
            station_location(infra, 'H', 'V4', 200),
            station_location(infra, 'I', 'V4', 200),
            label=f'directDI{2+2*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:00:00'),
            stops=[
                # Stop(120, station_location(infra, 'D', 'V2', 200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'I', 'V3', 200),
            station_location(infra, 'H', 'V1', -200),
            station_location(infra, 'G', 'V1', -200),
            station_location(infra, 'F', 'V1', -200),
            station_location(infra, 'E', 'V1', -200),
            station_location(infra, 'D', 'V1'),
            label=f'directID{2+2*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:30:00'),
            stops=[
                # Stop(120, station_location(infra, 'D', 'V2', 200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V1'),
            station_location(infra, 'E', 'V1', 200),
            station_location(infra, 'F', 'V1', 200),
            station_location(infra, 'G', 'V1', 200),
            station_location(infra, 'J', 'V2', 200),
            station_location(infra, 'K', 'V4', 200),
            label=f'directDK{2+2*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:05:00'),
            stops=[
                # Stop(120, station_location(infra, 'D', 'V2', 200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'K', 'V4', 200),
            station_location(infra, 'J', 'V1', -200),
            station_location(infra, 'G', 'V1', -200),
            station_location(infra, 'F', 'V1', -200),
            station_location(infra, 'E', 'V1', -200),
            station_location(infra, 'D', 'V1'),
            label=f'directKD{2+2*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:35:00'),
            stops=[
                # Stop(120, station_location(infra, 'D', 'V2', 200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'A', 'V2', 200),
            station_location(infra, 'B', 'V2', 200),
            station_location(infra, 'C', 'V2', 200),
            station_location(infra, 'D', 'V4'),

            label=f'omnibusAD{2+2*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:05:00'),
            stops=[

                Stop(120, station_location(infra, 'B', 'V2', 200)),
                Stop(120, station_location(infra, 'C', 'V2', 200)),
                Stop(120, station_location(infra, 'D', 'V4')),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V4'),
            station_location(infra, 'C', 'V1', -200),
            station_location(infra, 'B', 'V1', -200),
            station_location(infra, 'A', 'V2', -200),
            label=f'omnibusDA{2*i+1}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:30:00'),
            stops=[
                Stop(120, station_location(infra, 'D', 'V4')),
                Stop(120, station_location(infra, 'C', 'V1', -200)),
                Stop(120, station_location(infra, 'B', 'V1', -200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V2'),
            station_location(infra, 'E', 'V4', 200),
            station_location(infra, 'F', 'V4', 200),
            station_location(infra, 'G', 'V4', 200),
            station_location(infra, 'H', 'V4', 200),
            station_location(infra, 'I', 'V4', 200),
            label=f'semidirectDI{2+2*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:10:00'),
            stops=[
                # Stop(120, station_location(infra, 'D', 'V4', 200)),
                # Stop(120, station_location(infra, 'E', 'V4', 200)),
                # Stop(120, station_location(infra, 'F', 'V4', 200)),
                Stop(120, station_location(infra, 'G', 'V4', 200)),
                Stop(120, station_location(infra, 'H', 'V4', 200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'I', 'V3', 200),
            station_location(infra, 'H', 'V1', -200),
            station_location(infra, 'G', 'V5', -200),
            station_location(infra, 'F', 'V5', -200),
            station_location(infra, 'E', 'V5', -200),
            station_location(infra, 'D', 'V2', -200),
            label=f'semidirectID{1+2*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:00:00'),
            stops=[
                Stop(120, station_location(infra, 'H', 'V1', -200)),
                Stop(120, station_location(infra, 'G', 'V5', -200)),
                # Stop(120, station_location(infra, 'F', 'V5', -200)),
                # Stop(120, station_location(infra, 'E', 'V5', -200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V2'),
            station_location(infra, 'E', 'V4', 200),
            station_location(infra, 'F', 'V4', 200),
            station_location(infra, 'G', 'V4', 200),
            station_location(infra, 'J', 'V2', 200),
            station_location(infra, 'K', 'V4', 200),
            label=f'semidirectDK{2+2*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:15:00'),
            stops=[
                # Stop(120, station_location(infra, 'D', 'V4', 200)),
                # Stop(120, station_location(infra, 'E', 'V4', 200)),
                # Stop(120, station_location(infra, 'F', 'V4', 200)),
                Stop(120, station_location(infra, 'G', 'V4', 200)),
                Stop(120, station_location(infra, 'J', 'V2', 200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'K', 'V4', 200),
            station_location(infra, 'J', 'V1', -200),
            station_location(infra, 'G', 'V5', -200),
            station_location(infra, 'F', 'V5', -200),
            station_location(infra, 'E', 'V5', -200),
            station_location(infra, 'D', 'V2', -200),
            label=f'semidirectKD{1+2*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:05:00'),
            stops=[
                Stop(120, station_location(infra, 'J', 'V1', -200)),
                Stop(120, station_location(infra, 'G', 'V5', -200)),
                # Stop(120, station_location(infra, 'F', 'V5', -200)),
                # Stop(120, station_location(infra, 'E', 'V5', -200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V2'),
            station_location(infra, 'E', 'V4', 200),
            station_location(infra, 'F', 'V4', 200),
            station_location(infra, 'G', 'V4', 200),
            label=f'omnibusDG{2+4*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:20:00'),
            stops=[
                # Stop(120, station_location(infra, 'D', 'V2', 0)),
                Stop(120, station_location(infra, 'E', 'V4', 200)),
                Stop(120, station_location(infra, 'F', 'V4', 200)),
                Stop(120, station_location(infra, 'G', 'V4', 200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V2'),
            station_location(infra, 'E', 'V4', 200),
            station_location(infra, 'F', 'V4', 200),
            station_location(infra, 'G', 'V4', 200),
            label=f'omnibusDG{4+4*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:46:00'),
            stops=[
                # Stop(120, station_location(infra, 'D', 'V2', 0)),
                Stop(120, station_location(infra, 'E', 'V4', 200)),
                Stop(120, station_location(infra, 'F', 'V4', 200)),
                Stop(120, station_location(infra, 'G', 'V4', 200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'G', 'V5', 200),
            station_location(infra, 'F', 'V5', -200),
            station_location(infra, 'E', 'V5', -200),
            station_location(infra, 'D', 'V2', -200),
            label=f'omnibusGD{2+2*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:25:00'),
            stops=[
                Stop(120, station_location(infra, 'F', 'V5', -200)),
                Stop(120, station_location(infra, 'E', 'V5', -200)),
                Stop(120, station_location(infra, 'D', 'V2', -200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V2'),
            station_location(infra, 'E', 'V4', 200),
            station_location(infra, 'F', 'V4', 200),
            station_location(infra, 'G', 'V4', 200),
            station_location(infra, 'H', 'V4', 200),
            station_location(infra, 'I', 'V4', 200),
            label=f'omnibusDI{2+2*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:25:00'),
            stops=[
                # Stop(120, station_location(infra, 'D', 'V4', 200)),
                Stop(120, station_location(infra, 'E', 'V4', 200)),
                Stop(120, station_location(infra, 'F', 'V4', 200)),
                Stop(120, station_location(infra, 'G', 'V4', 200)),
                Stop(120, station_location(infra, 'H', 'V4', 200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'I', 'V3', 200),
            station_location(infra, 'H', 'V1', -200),
            station_location(infra, 'G', 'V5', -200),
            station_location(infra, 'F', 'V5', -200),
            station_location(infra, 'E', 'V5', -200),
            station_location(infra, 'D', 'V2'),
            label=f'omnibusID{1+2*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:15:00'),
            stops=[
                Stop(120, station_location(infra, 'H', 'V1', -200)),
                Stop(120, station_location(infra, 'G', 'V5', -200)),
                Stop(120, station_location(infra, 'F', 'V5', -200)),
                Stop(120, station_location(infra, 'E', 'V5', -200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V2'),
            station_location(infra, 'E', 'V4', 200),
            station_location(infra, 'F', 'V4', 200),
            station_location(infra, 'G', 'V4', 200),
            station_location(infra, 'J', 'V2', 200),
            station_location(infra, 'K', 'V2', 200),
            label=f'omnibusDK{2+2*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:30:00'),
            stops=[
                # Stop(120, station_location(infra, 'D', 'V4', 200)),
                Stop(120, station_location(infra, 'E', 'V4', 200)),
                Stop(120, station_location(infra, 'F', 'V4', 200)),
                Stop(120, station_location(infra, 'G', 'V4', 200)),
                Stop(120, station_location(infra, 'J', 'V2', 200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'K', 'V4', 200),
            station_location(infra, 'J', 'V1', -200),
            station_location(infra, 'G', 'V5', -200),
            station_location(infra, 'F', 'V5', -200),
            station_location(infra, 'E', 'V5', -200),
            station_location(infra, 'D', 'V2'),
            label=f'omnibusKD{1+2*i}',
            departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:20:00'),
            stops=[
                Stop(120, station_location(infra, 'J', 'V1', -200)),
                Stop(120, station_location(infra, 'G', 'V5', -200)),
                Stop(120, station_location(infra, 'F', 'V5', -200)),
                Stop(120, station_location(infra, 'E', 'V5', -200)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        # # Frequence 30 min

        # # Frequence 120 min
        if i%2 == 0:
            sim_builder.add_train_schedule(
                station_location(infra, 'A', 'V2', 200),
                station_location(infra, 'B', 'V2', 200),
                station_location(infra, 'C', 'V2', 200),
                station_location(infra, 'E', 'V4', 200),
                station_location(infra, 'F', 'V4', 200),
                station_location(infra, 'G', 'V4', 200),
                station_location(infra, 'J', 'V2', 200),
                station_location(infra, 'K', 'V2', 200),
                label=f'directAK{2+2*i}',
                departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:20:00'),
                stops=[
                    Stop(120, station_location(infra, 'B', 'V2', 200)),
                    Stop(120, station_location(infra, 'C', 'V2', 200)),
                    Stop(120, station_location(infra, 'E', 'V4', 200)),
                    Stop(120, station_location(infra, 'F', 'V4', 200)),
                    Stop(120, station_location(infra, 'G', 'V4', 200)),
                    Stop(120, station_location(infra, 'J', 'V2', 200)),
                ]
            ).add_standard_single_value_allowance("percentage", 5, )

            sim_builder.add_train_schedule(
                station_location(infra, 'K', 'V1', 200),
                station_location(infra, 'J', 'V1', -200),
                station_location(infra, 'G', 'V5', -200),
                station_location(infra, 'F', 'V5', -200),
                station_location(infra, 'E', 'V5', -200),
                station_location(infra, 'C', 'V1', -200),
                station_location(infra, 'B', 'V1', -200),
                station_location(infra, 'A', 'V1', -200),

                label=f'directKA{2*i+1}',
                departure_time=hour_to_seconds(f'{str(start_hour+i+1).zfill(2)}:25:00'),
                stops=[
                    Stop(120, station_location(infra, 'J', 'V1', -200)),
                    Stop(120, station_location(infra, 'G', 'V5', -200)),
                    Stop(120, station_location(infra, 'F', 'V5', -200)),
                    Stop(120, station_location(infra, 'E', 'V5', -200)),
                    Stop(120, station_location(infra, 'C', 'V1', -200)),
                    Stop(120, station_location(infra, 'B', 'V1', -200)),
                ],
            ).add_standard_single_value_allowance("percentage", 5, )

            sim_builder.add_train_schedule(
                station_location(infra, 'A', 'V2', 200),
                station_location(infra, 'B', 'V2', 200),
                station_location(infra, 'C', 'V2', 200),
                station_location(infra, 'E', 'V4', 200),
                station_location(infra, 'F', 'V4', 200),
                station_location(infra, 'G', 'V4', 200),
                station_location(infra, 'H', 'V4', 200),
                station_location(infra, 'I', 'V4', 200),
                label=f'directAI{2+2*i}',
                departure_time=hour_to_seconds(f'{str(start_hour+i+1).zfill(2)}:20:00'),
                stops=[
                    Stop(120, station_location(infra, 'B', 'V2', 200)),
                    Stop(120, station_location(infra, 'C', 'V2', 200)),
                    Stop(120, station_location(infra, 'E', 'V4', 200)),
                    Stop(120, station_location(infra, 'F', 'V4', 200)),
                    Stop(120, station_location(infra, 'G', 'V4', 200)),
                    Stop(120, station_location(infra, 'H', 'V4', 200)),
                ],
            ).add_standard_single_value_allowance("percentage", 5, )

            sim_builder.add_train_schedule(
                station_location(infra, 'I', 'V3', 200),
                station_location(infra, 'H', 'V3', -200),
                station_location(infra, 'G', 'V5', -200),
                station_location(infra, 'F', 'V5', -200),
                station_location(infra, 'E', 'V5', -200),
                station_location(infra, 'C', 'V1', -200),
                station_location(infra, 'B', 'V1', -200),
                station_location(infra, 'A', 'V1', -200),
                label=f'directIA{2*i+1}',
                departure_time=hour_to_seconds(f'{str(start_hour+i).zfill(2)}:25:00'),
                stops=[
                    Stop(120, station_location(infra, 'H', 'V3', -200)),
                    Stop(120, station_location(infra, 'G', 'V5', -200)),
                    Stop(120, station_location(infra, 'F', 'V5', -200)),
                    Stop(120, station_location(infra, 'E', 'V5', -200)),
                    Stop(120, station_location(infra, 'C', 'V1', -200)),
                    Stop(120, station_location(infra, 'B', 'V1', -200)),
                ],
            ).add_standard_single_value_allowance("percentage", 5, )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))

    # hardcore modification of the json
    sim = {}
    with open(os.path.join(dir, simulation_json), 'r') as f:
        sim = json.load(f)
        sim["rolling_stocks"][0]["max_speed"] = 40
        sim["rolling_stocks"][0]["length"] = 150
        sim["rolling_stocks"][0]["mass"] = 250000
        sim["rolling_stocks"][0]["effort_curves"]["modes"]["thermal"]["default_curve"]["speeds"] = \
            sim["rolling_stocks"][0]["effort_curves"]["modes"]["thermal"]["default_curve"]["speeds"][0:9]
        sim["rolling_stocks"][0]["effort_curves"]["modes"]["thermal"]["default_curve"]["max_efforts"] = \
            sim["rolling_stocks"][0]["effort_curves"]["modes"]["thermal"]["default_curve"]["max_efforts"][0:9]

    with open(os.path.join(dir, simulation_json), 'w') as f:
        json.dump(sim, f)
