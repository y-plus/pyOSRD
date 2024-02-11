import os

from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    Location,
)

from railjson_generator.schema.infra.direction import Direction
from railjson_generator.schema.simulation.stop import Stop


def c1(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
    station A (1 track)                        station B (1 track)

             ┎SA                                    SB┐
     (T)-|----DA------------------------------------DB-----|---->

    10 km long
    Train #1 starts from A and arrive at B
    Train #2 starts from B later
    """  # noqa

    infra_builder = InfraBuilder()

    T = infra_builder.add_track_section(label='T', length=10_000)

    T.add_buffer_stop(0, label='buffer_stop.0')
    T.add_buffer_stop(T.length, label='buffer_stop.1')

    DA = T.add_detector(label="DA", position=500, )
    DB = T.add_detector(label="DB", position=T.length-500, )

    T.add_signal(
        DA.position - 20,
        label='SA',
        direction=Direction.START_TO_STOP,
        is_route_delimiter=True,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T.add_signal(
        DB.position - 20,
        label='SB',
        direction=Direction.START_TO_STOP,
        is_route_delimiter=True,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    A = Location(T, 460)
    B = Location(T, 10_000 - 60)

    stationA = infra_builder.add_operational_point(label='stationA')
    stationA.add_part(track=T, offset=460)
    stationB = infra_builder.add_operational_point(label='stationB')
    stationB.add_part(track=T, offset=10_000-60)

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    sim_builder = SimulationBuilder()

    train1 = sim_builder.add_train_schedule(
        A,
        B,
        label='train0',
        departure_time=0,
    )
    # train1.add_stop(120., position=7_500)
    train1.add_standard_single_value_allowance("percentage", 5, )

    train2 = sim_builder.add_train_schedule(
        A,
        B,
        label='train1',
        departure_time=5*60.,
    )

    train2.add_standard_single_value_allowance("percentage", 5, )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
