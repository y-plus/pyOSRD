from rlway.pyosrd import OSRD


def c1y2_2trains_no_conflict() -> OSRD:
    """
    See c1y2_2trains.py in use_cases to check the infra.

    In this test case we have two trains going to different branch from
      a divergence.
    The leading train is delayed after the divergence therefore no impact
      should be seen on the trailing train.
    """
    use_case = 'c1y2_2trains'
    sim = OSRD(use_case=use_case, dir='tmp')

    sim.reset_delays()
    sim.add_delay('train0', time_threshold=80, delay=120.)
    return sim
