import os

from railjson_generator import (
    SimulationBuilder,
    # Location,
)
from railjson_generator.schema.simulation.stop import Stop

from pyosrd.use_cases.infras.hamelinfra import hamelinfra
from pyosrd.infra.build import station_location

from pyosrd.utils import hour_to_seconds


# helper function to compute seconds from a hour and minutes
def build_departure_time(hour: int, minutes: int) -> int:
    return hour_to_seconds(f'{str(hour).zfill(2)}:{str(minutes).zfill(2)}:00')


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

        # start hour for this loop
        cur_hour = start_hour + i

        # Frequence 60 min

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V2'),
            station_location(infra, 'E', 'V2', 75),
            station_location(infra, 'F', 'V2', 75),
            station_location(infra, 'G', 'V2', 75),
            station_location(infra, 'H', 'V2', 75),
            station_location(infra, 'I', 'V2', 200),
            label=f'directDI{2+2*i}',
            departure_time=build_departure_time(cur_hour, 0),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'D', 'V2', 0)),
                Stop(120, station_location(infra, 'I', 'V2', 0)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'I', 'V3'),
            station_location(infra, 'H', 'V3', -75),
            station_location(infra, 'G', 'V3', -75),
            # detector_location(infra, 'D.track.110.5'),
            station_location(infra, 'F', 'V3', -75),
            # detector_location(infra, 'D.track.080.3'),
            # detector_location(infra, 'detector.29'),
            station_location(infra, 'E', 'V3', -75),
            station_location(infra, 'D', 'V3', 75),
            label=f'directID{1+2*i}',
            departure_time=build_departure_time(cur_hour, 0),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'I', 'V3', 0)),
                Stop(120, station_location(infra, 'D', 'V3', -50)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V2'),
            station_location(infra, 'E', 'V2', 75),
            station_location(infra, 'F', 'V2', 75),
            station_location(infra, 'G', 'V2', 75),
            station_location(infra, 'J', 'V2', 75),
            station_location(infra, 'K', 'V2', 200),
            label=f'directDK{2+2*i}',
            departure_time=build_departure_time(cur_hour, 5),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'D', 'V2', 0)),
                Stop(120, station_location(infra, 'K', 'V2', 0)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'K', 'V4'),
            station_location(infra, 'J', 'V1', -75),
            station_location(infra, 'G', 'V3', -75),
            station_location(infra, 'F', 'V3', -75),
            station_location(infra, 'E', 'V3', -75),
            station_location(infra, 'D', 'V3', 75),
            label=f'directKD{1+2*i}',
            departure_time=build_departure_time(cur_hour, 5),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'K', 'V4', 0)),
                Stop(120, station_location(infra, 'D', 'V3', -50)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V2'),
            station_location(infra, 'E', 'V2', 75),
            station_location(infra, 'F', 'V2', 75),
            station_location(infra, 'G', 'V2', 75),
            station_location(infra, 'H', 'V2', 75),
            station_location(infra, 'I', 'V2', 200),
            label=f'semidirectDI{2+2*i}',
            departure_time=build_departure_time(cur_hour, 10),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'D', 'V2', 0)),
                Stop(120, station_location(infra, 'G', 'V2', 75)),
                Stop(120, station_location(infra, 'H', 'V2', 75)),
                Stop(120, station_location(infra, 'I', 'V2', 0)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'I', 'V3'),
            station_location(infra, 'H', 'V3', -75),
            station_location(infra, 'G', 'V3', -75),
            station_location(infra, 'F', 'V3', -75),
            station_location(infra, 'E', 'V3', -75),
            station_location(infra, 'D', 'V3', 75),
            label=f'semidirectID{1+2*i}',
            departure_time=build_departure_time(cur_hour, 10),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'I', 'V3', 0)),
                Stop(120, station_location(infra, 'H', 'V3', -75)),
                Stop(120, station_location(infra, 'G', 'V3', -75)),
                Stop(120, station_location(infra, 'D', 'V3', -50)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V2'),
            station_location(infra, 'E', 'V2', 75),
            station_location(infra, 'F', 'V2', 75),
            station_location(infra, 'G', 'V2', 75),
            station_location(infra, 'J', 'V2', 75),
            station_location(infra, 'K', 'V2', 200),
            label=f'semidirectDK{2+2*i}',
            departure_time=build_departure_time(cur_hour, 15),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'D', 'V2', 0)),
                Stop(120, station_location(infra, 'G', 'V2', 75)),
                Stop(120, station_location(infra, 'J', 'V2', 75)),
                Stop(120, station_location(infra, 'K', 'V2', 0)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'K', 'V3'),
            station_location(infra, 'J', 'V1', -75),
            station_location(infra, 'G', 'V3', -75),
            station_location(infra, 'F', 'V3', -75),
            station_location(infra, 'E', 'V3', -75),
            station_location(infra, 'D', 'V3', 75),
            label=f'semidirectKD{1+2*i}',
            departure_time=build_departure_time(cur_hour, 15),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'K', 'V3', 0)),
                Stop(120, station_location(infra, 'J', 'V1', -75)),
                Stop(120, station_location(infra, 'G', 'V3', -75)),
                Stop(120, station_location(infra, 'D', 'V3', -50)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'A', 'V2', 0),
            station_location(infra, 'B', 'V2', 75),
            station_location(infra, 'C', 'V2', 75),
            station_location(infra, 'D', 'V4', 75),

            label=f'omnibusAD{2+2*i}',
            departure_time=build_departure_time(cur_hour, 10),
            rolling_stock='hamelin_rolling_stock',
            stops=[

                Stop(120, station_location(infra, 'A', 'V2', 0)),
                Stop(120, station_location(infra, 'B', 'V2', 75)),
                Stop(120, station_location(infra, 'C', 'V2', 75)),
                Stop(120, station_location(infra, 'D', 'V4', -50)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V4'),
            station_location(infra, 'C', 'V1', -75),
            station_location(infra, 'B', 'V1', -75),
            station_location(infra, 'A', 'V2', -75),
            label=f'omnibusDA{1*i+1}',
            departure_time=build_departure_time(cur_hour, 40),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'D', 'V4')),
                Stop(120, station_location(infra, 'C', 'V1', -75)),
                Stop(120, station_location(infra, 'B', 'V1', -75)),
                Stop(120, station_location(infra, 'A', 'V2', 50)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V4'),
            station_location(infra, 'E', 'V4', 75),
            station_location(infra, 'F', 'V4', 75),
            station_location(infra, 'G', 'V4', 75),
            label=f'omnibusDG{2+4*i}',
            departure_time=build_departure_time(cur_hour, 20),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'D', 'V4', 0)),
                Stop(120, station_location(infra, 'E', 'V4', 75)),
                Stop(120, station_location(infra, 'F', 'V4', 75)),
                Stop(120, station_location(infra, 'G', 'V4', -50)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V2'),
            station_location(infra, 'E', 'V4', 75),
            station_location(infra, 'F', 'V4', 75),
            station_location(infra, 'G', 'V4', 75),
            label=f'omnibusDG{4+4*i}',
            departure_time=build_departure_time(cur_hour, 45),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'D', 'V2', 0)),
                Stop(120, station_location(infra, 'E', 'V4', 75)),
                Stop(120, station_location(infra, 'F', 'V4', 75)),
                Stop(120, station_location(infra, 'G', 'V4', -50)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        # # # Frequence 30 min
        sim_builder.add_train_schedule(
            station_location(infra, 'G', 'V5'),
            station_location(infra, 'F', 'V5', 75),
            station_location(infra, 'E', 'V5', 75),
            station_location(infra, 'D', 'V5', 75),
            label=f'omnibusGD{1+4*i}',
            departure_time=build_departure_time(cur_hour, 20),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'G', 'V5', 0)),
                Stop(120, station_location(infra, 'F', 'V5', 75)),
                Stop(120, station_location(infra, 'E', 'V5', 75)),
                Stop(120, station_location(infra, 'D', 'V5', -50)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'G', 'V5'),
            station_location(infra, 'F', 'V5', 75),
            station_location(infra, 'E', 'V5', 75),
            station_location(infra, 'D', 'V5', 75),
            label=f'omnibusGD{3+4*i}',
            departure_time=build_departure_time(cur_hour, 50),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'G', 'V5', 0)),
                Stop(120, station_location(infra, 'F', 'V5', 75)),
                Stop(120, station_location(infra, 'E', 'V5', 75)),
                Stop(120, station_location(infra, 'D', 'V5', -50)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V4'),
            station_location(infra, 'E', 'V4', 75),
            station_location(infra, 'F', 'V4', 75),
            station_location(infra, 'G', 'V4', 75),
            station_location(infra, 'H', 'V4', 75),
            station_location(infra, 'I', 'V4', 75),
            label=f'omnibusDI{2+2*i}',
            departure_time=build_departure_time(cur_hour, 25),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'D', 'V4', 0)),
                Stop(120, station_location(infra, 'E', 'V4', 75)),
                Stop(120, station_location(infra, 'F', 'V4', 75)),
                Stop(120, station_location(infra, 'G', 'V4', 75)),
                Stop(120, station_location(infra, 'H', 'V4', 75)),
                Stop(120, station_location(infra, 'I', 'V4', -50)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'I', 'V3'),
            station_location(infra, 'H', 'V1', -75),
            station_location(infra, 'G', 'V3', -75),
            station_location(infra, 'F', 'V3', -75),
            station_location(infra, 'E', 'V3', -75),
            station_location(infra, 'D', 'V2', 75),
            label=f'omnibusID{1+2*i}',
            departure_time=build_departure_time(cur_hour, 20),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'I', 'V3', 0)),
                Stop(120, station_location(infra, 'H', 'V1', -75)),
                Stop(120, station_location(infra, 'G', 'V3', -75)),
                Stop(120, station_location(infra, 'F', 'V3', -75)),
                Stop(120, station_location(infra, 'E', 'V3', -75)),
                Stop(120, station_location(infra, 'D', 'V2', -50)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'D', 'V2'),
            station_location(infra, 'E', 'V4', 75),
            station_location(infra, 'F', 'V4', 75),
            station_location(infra, 'G', 'V4', 75),
            station_location(infra, 'J', 'V2', 75),
            station_location(infra, 'K', 'V2', 75),
            label=f'omnibusDK{2+2*i}',
            departure_time=build_departure_time(cur_hour, 30),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'D', 'V2', 0)),
                Stop(120, station_location(infra, 'E', 'V4', 75)),
                Stop(120, station_location(infra, 'F', 'V4', 75)),
                Stop(120, station_location(infra, 'G', 'V4', 75)),
                Stop(120, station_location(infra, 'J', 'V2', 75)),
                Stop(120, station_location(infra, 'K', 'V2', -50)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        sim_builder.add_train_schedule(
            station_location(infra, 'K', 'V4'),
            station_location(infra, 'J', 'V1', -75),
            station_location(infra, 'G', 'V5', -75),
            station_location(infra, 'F', 'V5', -75),
            station_location(infra, 'E', 'V5', -75),
            station_location(infra, 'D', 'V3', 75),
            label=f'omnibusKD{1+2*i}',
            departure_time=build_departure_time(cur_hour, 25),
            rolling_stock='hamelin_rolling_stock',
            stops=[
                Stop(120, station_location(infra, 'K', 'V4', 0)),
                Stop(120, station_location(infra, 'J', 'V1', -75)),
                Stop(120, station_location(infra, 'G', 'V5', -75)),
                Stop(120, station_location(infra, 'F', 'V5', -75)),
                Stop(120, station_location(infra, 'E', 'V5', -75)),
                Stop(120, station_location(infra, 'D', 'V3', -50)),
            ]
        ).add_standard_single_value_allowance("percentage", 5, )

        # # Frequence 120 min
        if i % 2 == 0:
            sim_builder.add_train_schedule(
                station_location(infra, 'A', 'V2'),
                station_location(infra, 'B', 'V2', 75),
                station_location(infra, 'C', 'V2', 75),
                station_location(infra, 'E', 'V4', 75),
                station_location(infra, 'F', 'V4', 75),
                station_location(infra, 'G', 'V4', 75),
                station_location(infra, 'J', 'V2', 75),
                station_location(infra, 'K', 'V2', 75),
                label=f'directAK{2+2*i}',
                departure_time=build_departure_time(cur_hour, 30),
                rolling_stock='hamelin_rolling_stock',
                stops=[
                    Stop(120, station_location(infra, 'A', 'V2', 0)),
                    Stop(120, station_location(infra, 'B', 'V2', 75)),
                    Stop(120, station_location(infra, 'C', 'V2', 75)),
                    Stop(120, station_location(infra, 'E', 'V4', 75)),
                    Stop(120, station_location(infra, 'F', 'V4', 75)),
                    Stop(120, station_location(infra, 'G', 'V4', 75)),
                    Stop(120, station_location(infra, 'J', 'V2', 75)),
                    Stop(120, station_location(infra, 'K', 'V2', -50)),
                ]
            ).add_standard_single_value_allowance("percentage", 5, )

            sim_builder.add_train_schedule(
                station_location(infra, 'K', 'V1'),
                station_location(infra, 'J', 'V1', -75),
                station_location(infra, 'G', 'V5', -75),
                station_location(infra, 'F', 'V5', -75),
                station_location(infra, 'E', 'V5', -75),
                station_location(infra, 'C', 'V1', -75),
                station_location(infra, 'B', 'V1', -75),
                station_location(infra, 'A', 'V1', -75),
                label=f'directKA{1+2*i}',
                departure_time=build_departure_time(cur_hour+1, 30),
                rolling_stock='hamelin_rolling_stock',
                stops=[
                    Stop(120, station_location(infra, 'K', 'V1', 0)),
                    Stop(120, station_location(infra, 'J', 'V1', -75)),
                    Stop(120, station_location(infra, 'G', 'V5', -75)),
                    Stop(120, station_location(infra, 'F', 'V5', -75)),
                    Stop(120, station_location(infra, 'E', 'V5', -75)),
                    Stop(120, station_location(infra, 'C', 'V1', -75)),
                    Stop(120, station_location(infra, 'B', 'V1', -75)),
                    Stop(120, station_location(infra, 'A', 'V1', 50)),
                ],
            ).add_standard_single_value_allowance("percentage", 5, )

            sim_builder.add_train_schedule(
                station_location(infra, 'A', 'V2'),
                station_location(infra, 'B', 'V2', 75),
                station_location(infra, 'C', 'V2', 75),
                station_location(infra, 'E', 'V4', 75),
                station_location(infra, 'F', 'V4', 75),
                station_location(infra, 'G', 'V4', 75),
                station_location(infra, 'H', 'V4', 75),
                station_location(infra, 'I', 'V4', 75),
                label=f'directAI{2+2*i}',
                departure_time=build_departure_time(cur_hour+1, 30),
                rolling_stock='hamelin_rolling_stock',
                stops=[
                    Stop(120, station_location(infra, 'A', 'V2', 0)),
                    Stop(120, station_location(infra, 'B', 'V2', 75)),
                    Stop(120, station_location(infra, 'C', 'V2', 75)),
                    Stop(120, station_location(infra, 'E', 'V4', 75)),
                    Stop(120, station_location(infra, 'F', 'V4', 75)),
                    Stop(120, station_location(infra, 'G', 'V4', 75)),
                    Stop(120, station_location(infra, 'H', 'V4', 75)),
                    Stop(120, station_location(infra, 'I', 'V4', -50)),
                ],
            ).add_standard_single_value_allowance("percentage", 5, )

            sim_builder.add_train_schedule(
                station_location(infra, 'I', 'V3'),
                station_location(infra, 'H', 'V3', -75),
                station_location(infra, 'G', 'V5', -75),
                station_location(infra, 'F', 'V5', -75),
                station_location(infra, 'E', 'V5', -75),
                station_location(infra, 'C', 'V1', -75),
                station_location(infra, 'B', 'V1', -75),
                station_location(infra, 'A', 'V1', -75),
                label=f'directIA{1+2*i}',
                departure_time=build_departure_time(cur_hour, 30),
                rolling_stock='hamelin_rolling_stock',
                stops=[
                    Stop(120, station_location(infra, 'I', 'V3', 0)),
                    Stop(120, station_location(infra, 'H', 'V3', -75)),
                    Stop(120, station_location(infra, 'G', 'V5', -75)),
                    Stop(120, station_location(infra, 'F', 'V5', -75)),
                    Stop(120, station_location(infra, 'E', 'V5', -75)),
                    Stop(120, station_location(infra, 'C', 'V1', -75)),
                    Stop(120, station_location(infra, 'B', 'V1', -75)),
                    Stop(120, station_location(infra, 'A', 'V1', 50)),
                ],
            ).add_standard_single_value_allowance("percentage", 5, )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
