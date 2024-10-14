import os


from railjson_generator import (
    SimulationBuilder,
    Location,
)
from pyosrd.use_cases.infras.terminal_station_3_5 import terminal_station_3_5
from pyosrd.infra.build import station_location
from railjson_generator.schema.simulation.stop import Stop

def terminal_station_3_5_trains(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:

    infra = terminal_station_3_5(dir, infra_json)
    T = infra.track_sections

    ins = {
        '1': Location(T[1], 10),
        '2': Location(T[2], 10),
    }
    outs = {
        '1bis': Location(T[0], 0),
        '1': Location(T[1], 0),
    }
    stops = {
        str(i): station_location(infra, 'D', f"V{i}")
        for i in range(1, 6)
    }

    sim_builder = SimulationBuilder()

    t = 0
    for start in ins:
        for end in stops:
            print(f'train_{start}_V{end}')
            sim_builder.add_train_schedule(
                ins[start],
                stops[end],
                label=f'train_{start}_V{end}',
                departure_time=t,
                stops=[
                    # Stop(120, station_location(infra, 'D', f"V{end}", -50))
                ],
                # initial_speed=25.
            )
            t += 60
    for start in stops:
        for end in outs:
            print(f'train_V{start}_{end}')
            sim_builder.add_train_schedule(
                stops[start],
                outs[end],
                label=f'train_V{start}_{end}',
                departure_time=t,
                stops=[
                    # Stop(120, station_location(infra, 'D', f"V{end}", -50))
                ],
                # initial_speed=25.
            )
            t += 60

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
