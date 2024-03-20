import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.simulation.stop import Stop
from pyosrd.infra.c2y1sy2sy1s_infra import c2y1sy2sy1s_infra


def c2y1sy2sy1s(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    stations = {}
    built_infra = c2y1sy2sy1s_infra(dir, infra_json, stations)
    T = built_infra.track_sections

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        Location(T[0], 20),
        stations['C_2'],
        Location(T[4], 4700),
        label='train0',
        departure_time=0.,
        stops=[
            Stop(location=stations['C_2'], duration=60., ),
        ],
    )

    sim_builder.add_train_schedule(
        Location(T[1], 20),
        # stations['C_2'],
        Location(T[4], 4700),
        label='train1',
        departure_time=120.,
        stops=[
            Stop(location=stations['B'], duration=120., ),
            Stop(location=stations['C'], duration=120., ),
            Stop(location=stations['D'], duration=120., ),
        ],
        # rolling_stock='short_fast_rolling_stock',
    )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
