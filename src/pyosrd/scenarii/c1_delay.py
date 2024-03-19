from pyosrd import OSRD


def c1_delay() -> OSRD:
    """
    See c1.py in use_cases to check the infra.

    In this test case the train0 is delay for 120 seconds,
    10 seconds after its start
    """
    use_case = 'c1'
    sim = OSRD(use_case=use_case, dir='tmp')

    # les trains

    sim.reset_delays()
    sim.add_delay('train0', time_threshold=10, delay=120.)
    sim.run()

    return sim
