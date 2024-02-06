from rlway.pyosrd import OSRD


def c2y1y2y_2_trains_reorder() -> OSRD:
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

    In this test case train0 is delayed a lot and train1 should overtake

    """  # noqa
    use_case = 'c2y1y2y'
    sim = OSRD(use_case=use_case, dir='tmp')

    sim.reset_delays()
    sim.add_delay('train0', time_threshold=130, delay=250.)

    return sim
