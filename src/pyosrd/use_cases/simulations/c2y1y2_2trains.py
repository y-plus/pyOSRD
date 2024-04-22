import os


from railjson_generator import (
    SimulationBuilder,
    Location,
)
from pyosrd.use_cases.infras.c2y1y2 import c2y1y2


def c2y1y2_2trains(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
    station0 (2 tracks)                        station1 (2 tracks)

           ┎S0                                      S4┐
    (T0)-----D0-                                  --D4---------(T4)-->
                 \  S2┐                    ┎S3  /
               CVG>-D2-----(T2)--+--(T3)----D3-<DVG
           ┎S1   /                              \   S5┐
    (T1)-----D1-                                  --D5---------(T5)-->

    All tracks are 500m long
    Train 0 starts from T0 at t=0 and arrives at T4
    Train 1 starts from T1 at t=100 and arrives at T5
    """  # noqa

    infra = c2y1y2(dir, infra_json)

    T = infra.track_sections

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        Location(T[0], 300),
        Location(T[4], 490),
        label='train0',
        departure_time=0.,
    )
    sim_builder.add_train_schedule(
        Location(T[1], 300),
        Location(T[5], 480),
        label='train1',
        departure_time=100.,
    )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
