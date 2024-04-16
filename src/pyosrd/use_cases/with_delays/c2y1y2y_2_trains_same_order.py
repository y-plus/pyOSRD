from pyosrd import OSRD


def c2y1y2y_2_trains_same_order(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
    delays_json: str = 'delays.json'
  ) -> None:
    """
    See c2y1y2y.py in use_cases to check the infra. (reminder here :)
       station0 (2 tracks)                        station1 (2 tracks)                      station2 (1 track)

           ┎S0                                                      ┎S4
    (T0)-----D0-                                  --D3.1----(T4)-----D4-
                 \                         ┎S3  /                        \
               CVG>-D2-----(T2)--+--(T3)----D3-<DVG                    CVG>-D6-----(T6)-+--(T7)----D7------>
           ┎S1   /                              \                   ┎S5  /
    (T1)-----D1-                                  --D3.2----(T5)-----D5-

    train0 goes from T0 to T7 (passing by T4)
    train1 foes from T1 to T7 (passing by T5)

    In this test case train0 is slightly delayed BUT train1 should be stopped a little bit (but not overtake)

    """  # noqa
    use_case = 'c2y1y2y_2trains'
    sim = OSRD(
        dir=dir,
        infra_json=infra_json,
        simulation_json=simulation_json,
        delays_json=delays_json,
        simulation=use_case
    )

    sim.reset_delays()
    sim.add_delay('train0', time_threshold=130, delay=75.)
    sim.add_delays_in_results()
