import os

from haversine import inverse_haversine, Direction as Dir

from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    Location,
)

from railjson_generator.schema.infra.direction import Direction


def cvg_dvg(
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

    infra_builder = InfraBuilder()

    T = [
        infra_builder.add_track_section(label='T'+str(id), length=500, track_name='T'+str(id),)
        for id in range(6)
    ]

    for i in [0, 1]:
        T[i].add_buffer_stop(0, label=f'buffer_stop.{i}')
    for i in [4, 5]:
        T[i].add_buffer_stop(T[i].length, label=f'buffer_stop.{i-2}')

    cvg = infra_builder.add_point_switch(
        T[2].begin(),
        T[0].end(),
        T[1].end(),
        label='CVG',
    )
    
    CVG_COORDS = (0.21, 45.575988410701974)
    PINCH = 0.75
    
    cvg.set_coords(*CVG_COORDS)

    t0_mid = inverse_haversine(CVG_COORDS[::-1], 250, direction=Dir.NORTHWEST-PINCH, unit='m')[::-1]
    t0_begin = inverse_haversine(t0_mid[::-1], 250, direction=Dir.WEST, unit='m')[::-1]
    T[0].set_remaining_coords([t0_begin, t0_mid])

    
    t1_mid = inverse_haversine(CVG_COORDS[::-1], 250, direction=Dir.SOUTHWEST+PINCH, unit='m')[::-1]
    t1_begin = inverse_haversine(t1_mid[::-1], 250, direction=Dir.WEST, unit='m')[::-1]
    T[1].set_remaining_coords([t1_begin, t1_mid])

    link = infra_builder.add_link(T[2].end(), T[3].begin(), label='L')
    dvg = infra_builder.add_point_switch(
        T[3].end(),
        T[4].begin(),
        T[5].begin(),
        label='DVG',
    )

    link_coords = inverse_haversine(CVG_COORDS[::-1], 500, direction=Dir.EAST, unit='m')[::-1]
    link.set_coords(*list(link_coords))

    dvg_coords = inverse_haversine(link_coords[::-1], 500, direction=Dir.EAST+.1, unit='m')[::-1]
    dvg.set_coords(*list(dvg_coords))
    
    t4_mid = inverse_haversine(dvg_coords[::-1], 250, direction=Dir.NORTHEAST+PINCH, unit='m')[::-1]
    t4_end = inverse_haversine(t4_mid[::-1], 250, direction=Dir.EAST, unit='m')[::-1]
    T[4].set_remaining_coords([t4_mid, t4_end])

    t5_mid = inverse_haversine(dvg_coords[::-1], 250, direction=Dir.SOUTHEAST-PINCH, unit='m')[::-1]
    t5_end = inverse_haversine(t5_mid[::-1], 250, direction=Dir.EAST, unit='m')[::-1]
    T[5].set_remaining_coords([t5_mid, t5_end])



    for i, track in enumerate(T):
        d = track.add_detector(
            label=f"D{i}",
            position=(450 if i in [0, 1, 3] else 50),
        )
        s = T[i].add_signal(
            d.position + (-20 if i in [0, 1, 3] else 20),
            (
                Direction.START_TO_STOP
                if i in [0, 1, 3] else Direction.STOP_TO_START
            ),
            is_route_delimiter=True,
            label=f"S{i}"
        )
        s.add_logical_signal("BAL", settings={"Nf": "true"})

    stations = [
        infra_builder.add_operational_point(label='station'+str(i))
        for i in range(2)
    ]
    for track in range(2):
        stations[0].add_part(T[track], 300)
    for track in range(4, 6):
        stations[1].add_part(T[track], 480)

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    sim_builder = SimulationBuilder()

    train0 = sim_builder.add_train_schedule(
        Location(T[0], 300),
        Location(T[4], 490),
        label='train0',
        departure_time=0.,
    )
    train0.add_standard_single_value_allowance("percentage", 5, )
    train1 = sim_builder.add_train_schedule(
        Location(T[1], 300),
        Location(T[5], 480),
        label='train1',
        departure_time=100.,
    )
    train1.add_standard_single_value_allowance("percentage", 5, )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
