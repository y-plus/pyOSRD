import os


from railjson_generator import (
    SimulationBuilder,
    Location,
)
from pyosrd.use_cases.infras.station_3_5 import station_3_5
from pyosrd.infra.build import station_location
from railjson_generator.schema.simulation.stop import Stop

def station_3_5_trains(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:

    infra = station_3_5(dir, infra_json)
    T = infra.track_sections

    north = {
        '2': T[-5],
        '1': T[-1],
        '1bis': T[-2],
    }
    south = {
        '2': T[0],
        '1': T[1],
        '1bis': T[2],
    }

    paths_north_south = [
        ('1bis', '5', '1bis'),
        ('1bis', '5', '1'),
        ('1bis', '3', '1bis'),
        ('1bis', '3', '1'),
        ('1bis', '1', '1bis'),
        ('1bis', '1', '1'),
        ('1', '5', '1bis'),
        ('1', '5', '1'),
        ('1', '3', '1bis'),
        ('1', '3', '1'),
        ('1', '1', '1bis'),
        ('1', '1', '1'),
    ]
    
    paths_south_north = [
        ('2', '4', '2'),
        ('2', '4', '1'),
        ('2', '2', '2'),
        ('2', '2', '1'),
        ('2', '1', '2'),
        ('2', '1', '1'),
        ('1', '4', '2'),
        ('1', '4', '1'),
        ('1', '2', '2'),
        ('1', '2', '1'),
        ('1', '1', '2'),
        ('1', '1', '1'),

    ]
    sim_builder = SimulationBuilder()
    for i, path in enumerate(paths_north_south):
        sim_builder.add_train_schedule(
            Location(north[path[0]], north[path[0]].length-20),
            station_location(infra, 'A', f"V{path[1]}", 0),
            Location(south[path[2]], 20),       
            label=f'train{i}',
            departure_time=180*i,
            stops=[
                Stop(60, location=station_location(infra, 'A', f"V{path[1]}", -200)),
            ],
            initial_speed=25.
        )#.add_standard_single_value_allowance("percentage", 5, )
    for i, path in enumerate(paths_south_north):
        sim_builder.add_train_schedule(
            Location(south[path[0]], 20),
            station_location(infra, 'A', f"V{path[1]}", 0),
            Location(north[path[2]], north[path[2]].length-20),       
            label=f'train{12+i}',
            departure_time=180*(12+i),
            stops=[
                Stop(60, location=station_location(infra, 'A', f"V{path[1]}", 200)),
            ],
            initial_speed=25.
        )#.add_standard_single_value_allowance("percentage", 5, )



    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
