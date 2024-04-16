import os


from railjson_generator import (
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.simulation.stop import Stop

from pyosrd.use_cases.infras.c2y1sy2sy1s import c2y1sy2sy1s


def c2y1sy2sy1s_1train(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """


           ┎SA0
    (T0)----DA0-                                            (T3)
                 \       ┎S1    ┎SB  ┎SB2    ┎S2    ┎SC      ┎SC2         ┎S3    ┎SD  ┎SD2
               SWA>-DA2---D1-----DB-o-DB2-----D2-----DC--DC0---o-DC2-------D3-----DD-o-DD2-----(T4)
           ┎SA1  /                                   SWC\            /SWC2
    (T1)----DA1-                 (T2)                    DC1--o-DC3-(T5)


    """  # noqa

    infra, stations = c2y1sy2sy1s(dir, infra_json)

    T = infra.track_sections

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
