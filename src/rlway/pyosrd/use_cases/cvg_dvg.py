import os

from railjson_generator import InfraBuilder, Location, SimulationBuilder
from railjson_generator.schema.infra.direction import Direction


def cvg_dvg(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
) -> None:
    """
    station0 (2 tracks)                        station1 (2 tracks)

           ┎S0                                      S3┐
    (T0)-----D0-                                  --D3---------(T3)-->
                 \  S2┐                   ┎S2a  /
               CVG>-D2-----(T2)------------D2a-<DVG
           ┎S1   /                              \   S4┐
    (T1)-----D1-                                  --D4---------(T4)-->

    All tracks are 1km long
    Train 0 starts from T0 at t=0 and arrives at T4
    Train 1 starts from T1 at t=100s and arrives at T3
    """  # noqa

    infra_builder = InfraBuilder()

    T = [
        infra_builder.add_track_section(label='T'+str(id), length=1_000)
        for id in range(5)
    ]

    for i in [0, 1]:
        T[i].add_buffer_stop(0, label=f'buffer_stop.{i}')
    for i in [3, 4]:
        T[i].add_buffer_stop(T[i].length, label=f'buffer_stop.{i}')

    infra_builder.add_point_switch(
        T[2].begin(),
        T[0].end(),
        T[1].end(),
        label='CVG',
    )
    # infra_builder.add_link(T[2].end(), T[3].begin())
    infra_builder.add_point_switch(
        T[2].end(),
        T[3].begin(),
        T[4].begin(),
        label='DVG',
    )

    detectors = [
        T[i].add_detector(label=f"D{i}", position=T[i].length-180)
        for i in [0, 1]
    ] + [
        T[i].add_detector(label=f"D{i}", position=180)
        for i in [2, 3, 4]
    ] + [T[2].add_detector(label='D2a', position=T[i].length-180)]
    signals = [
        T[i].add_signal(
            detectors[i].position-20,
            Direction.START_TO_STOP,
            linked_detector=detectors[i],
            label=f"S{i}"
        )
        for i in [0, 1]
    ] + [
        T[i].add_signal(
            detectors[i].position+20,
            Direction.STOP_TO_START,
            linked_detector=detectors[i],
            label=f"S{i}"
        )
        for i in [2, 3, 4]
    ] + [
        T[2].add_signal(
            T[2].length-180-20,
            Direction.START_TO_STOP,
            linked_detector=detectors[-1],
            label='S2a',
            )
    ]
    for signal in signals:
        signal.add_logical_signal("BAL", settings={"Nf": "true"})

    stations = [
        infra_builder.add_operational_point(label='station'+str(i))
        for i in range(2)
    ]
    for track in [0, 1]:
        stations[0].add_part(T[track], 780)
    for track in [3, 4]:
        stations[1].add_part(T[track], 980)

    os.makedirs(dir, exist_ok=True)

    try:
        built_infra = infra_builder.build()
        built_infra.save(os.path.join(dir, infra_json))

        sim_builder = SimulationBuilder()

        sim_builder.add_train_schedule(
            Location(T[0], 0),
            Location(T[4], T[4].length),
            label='train0',
            departure_time=0.,
        )
        sim_builder.add_train_schedule(
            Location(T[1], 0),
            Location(T[3], T[3].length),
            label='train1',
            departure_time=100.,
        )

        built_simulation = sim_builder.build()
        built_simulation.save(os.path.join(dir, simulation_json))

    except RuntimeError as e:
        print(e)
