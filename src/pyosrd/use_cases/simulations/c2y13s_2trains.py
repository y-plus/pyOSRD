import os


from railjson_generator import (
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.simulation.stop import Stop
from pyosrd.use_cases.infras.c2y13s import c2y13s


def c2y13s_2trains(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """


           ┎SA0
    (T0)----DA0-
                 \       ┎S1    ┎SB  ┎SB2    ┎S2    ┎SC  ┎SC2    ┎S3    ┎SD  ┎SD2
               SWA>-DA2---D1-----DB-o-DB2-----D2-----DC-o-DC2-----D3-----DD-o-DD2-----(T2)
           ┎SA1  /
    (T1)----DA1-

    All blocks are 1,5 km long
    All station lanes are 500m long
    Train 0 starts from T0 at t=0 and arrives at T4
    Train 1 starts from T1 at t=100 and arrives at T5
    """  # noqa

    infra, stations = c2y13s(dir, infra_json)

    T = infra.track_sections

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        Location(T[0], 20),
        Location(T[2], 11_990),
        label='train0',
        departure_time=0.,
    )

    sim_builder.add_train_schedule(
        Location(T[1], 20),
        Location(T[2], 11_990),
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
