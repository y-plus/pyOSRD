import os

from importlib.resources import files

from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.infra.direction import Direction
from railjson_generator.schema.simulation.simulation import (
    register_rolling_stocks
)

register_rolling_stocks(files('pyosrd').joinpath('rolling_stocks'))


def c1_with_blocks(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
                ┎SA SA.1┐       ┎S2.0 S2.1┐       ┎S8.0 S8.1┐     ┎SB SB.1┐
     (T)<---A------DA----------------D2-----...--------D8-------------DB------B---->

    10 km long, Detectors D2,D4,D6,D8 detectors every 2km
    Trains start from A and arrive at B
    """  # noqa

    infra_builder = InfraBuilder()

    T = infra_builder.add_track_section(label='T', length=10_000)

    T.add_buffer_stop(0, label='buffer_stop.0')
    T.add_buffer_stop(T.length, label='buffer_stop.1')

    DA = T.add_detector(label="DA", position=500, )
    DB = T.add_detector(label="DB", position=T.length-500, )

    for i in range(4):
        T.add_detector(label=f"D{(i+1)*2}", position=(i+1)*2_000, )
        T.add_signal(
            (i+1)*2_000 - 20,
            label=f"S{(i+1)*2}.0",
            direction=Direction.START_TO_STOP,
            is_route_delimiter=True,
        ).add_logical_signal("BAL", settings={"Nf": "true"})
        T.add_signal(
            (i+1)*2_000 + 20,
            label=f"S{(i+1)*2}.1",
            direction=Direction.STOP_TO_START,
            is_route_delimiter=True,
        ).add_logical_signal("BAL", settings={"Nf": "true"})

    T.add_signal(
        DA.position - 20,
        label='SA',
        direction=Direction.START_TO_STOP,
        is_route_delimiter=True,
    ).add_logical_signal("BAL", settings={"Nf": "true"})
   
    T.add_signal(
        DA.position + 20,
        label='SA1',
        direction=Direction.STOP_TO_START,
        is_route_delimiter=True,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T.add_signal(
        DB.position - 20,
        label='SB',
        direction=Direction.START_TO_STOP,
        is_route_delimiter=True,
    ).add_logical_signal("BAL", settings={"Nf": "true"})

    T.add_signal(
        DB.position + 20,
        label='SB1',
        direction=Direction.STOP_TO_START,
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
        label='First train',
        departure_time=0,
    )
    # train1.add_stop(120., position=7_500)
    train1.add_standard_single_value_allowance("percentage", 5, )

    train2 = sim_builder.add_train_schedule(
        A,
        B,
        label='Second train',
        departure_time=3*60.,
    )

    train2.add_standard_single_value_allowance("percentage", 5, )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
