from rlway.pyosrd import OSRD


def c2y11s_conflict_20_trains() -> OSRD:
    """
    See c2y11s.py in use_cases to check the infra.

      TODO
    """
    use_case = 'c2y11s'
    sim = OSRD(use_case=use_case, dir='tmp')

    for i in [1, 2, 3]:
        sim.copy_train('train0', f'train0.{i}', departure_time=300.*i)
        sim.copy_train('train1', f'train1.{i}', departure_time=100.+300.*i)

    sim.reset_delays()
    sim.add_delay('train0', time_threshold=70, delay=100.)

    sim.run()
    return sim
