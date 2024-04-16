import os


from railjson_generator import (
    SimulationBuilder,
    Location,
)
from pyosrd.use_cases.infras.c3yy1yy3 import c3yy1yy3


def c3yy1yy3_6trains(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
    stationA(3 tracks)                                        stationB (1 track)

          ┎S0            S4┐               ┎S5           S6┐
    (T0)---D0------SW0---D4--(T4)--+--(T5)--D5--SW2------D6---(T6)
          ┎S1     D3/(T3)                    (T9)\D9     S7┐
    (T1)---D1-----SW1                            SW3-----D7---(T7)
          ┎S2     /                               \      S8┐
    (T2)---D2-----                                  -----D8---(T8)

    """  # noqa

    infra = c3yy1yy3(dir, infra_json)

    T = infra.track_sections

    sim_builder = SimulationBuilder()

    sim_builder.add_train_schedule(
        Location(T[0], 20),
        Location(T[6], 480),
        label='train0-6',
        departure_time=0.,
    )

    sim_builder.add_train_schedule(
        Location(T[1], 20),
        Location(T[6], 480),
        label='train1-6',
        departure_time=120.,
    )

    sim_builder.add_train_schedule(
        Location(T[2], 20),
        Location(T[6], 480),
        label='train2-6',
        departure_time=240.,
    )

    sim_builder.add_train_schedule(
        Location(T[6], 480),
        Location(T[0], 20),
        label='train6-0',
        departure_time=360.,
    )
    sim_builder.add_train_schedule(
        Location(T[6], 480),
        Location(T[1], 20),
        label='train6-1',
        departure_time=480.,
    )

    sim_builder.add_train_schedule(
        Location(T[6], 480),
        Location(T[2], 20),
        label='train6-2',
        departure_time=600.,
    )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
