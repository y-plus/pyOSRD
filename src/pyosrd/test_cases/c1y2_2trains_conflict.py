from rlway.pyosrd import OSRD


def c1y2_2trains_conflict() -> OSRD:
    """
    See c1y2_2trains.py in use_cases to check the infra.

    In this test case we have two trains going to different
      branch from a divergence.
    The leading train is delayed in the divergence therefore
      no the trailing train must wait before entering the divergence.
    """
    use_case = 'c1y2_2trains'
    sim = OSRD(use_case=use_case, dir='tmp')

    sim.reset_delays()
    sim.add_delay('train0', time_threshold=70, delay=120.)
    return sim
