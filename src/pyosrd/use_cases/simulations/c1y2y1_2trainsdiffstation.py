import os

from railjson_generator import (
    SimulationBuilder,
    Location,
)
from pyosrd.use_cases.infras.c1y2y1 import c1y2y1


def c1y2y1_2trainsdiffstation(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
                        station1 (2 tracks)
                                          ┎S1
                        --D0.1----(T1)-----D1-
                 ┎S0  /                        \               ┎S3
        |--(T0)----D0-<DVG                    CVG>-D3.0--(T3)---D3--|
                      \                   ┎S2  /
                        --D0.2----(T2)-----D2-

    All tracks are 1000m long
    Train 0 starts from T1 at t=0 and arrives at T3
    Train 1 starts from T1 at t=100 and arrives at T3 (passing by T2)
    """  # noqa

    built_infra = c1y2y1(dir, infra_json)
    T = built_infra.track_sections

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        Location(T[0], 50.),
        Location(T[3], T[3].length-10),
        label='train0',
        departure_time=0,
    )

    sim_builder.add_train_schedule(
        Location(T[0], 50.),
        Location(T[2], 50.),
        Location(T[3], T[3].length-10),
        label='train1',
        departure_time=100,
    )

    built_simulation = sim_builder.build()

    os.makedirs(dir, exist_ok=True)
    built_infra.save(os.path.join(dir, infra_json))
    built_simulation.save(os.path.join(dir, simulation_json))
