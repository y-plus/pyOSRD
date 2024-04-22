from pyosrd import OSRD


def c1y2y1_2trainsdiffstation_delay50(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json',
    delays_json: str = 'delays.json'
  ) -> None:
    """
                        station1 (2 tracks)
                                          ┎S1
                        --D0.1----(T1)-----D1-
                 ┎S0  /                        \               ┎S3
        |--(T0)----D0-<DVG                    CVG>-D3.0--(T3)---D3--|
                      \                   ┎S2  /
                        --D0.2----(T2)-----D2-

    All tracks are 1000m long
    Train 0 starts from T1 at t=0 and arrives at T3
    Train 1 starts from T1 at t=100 and arrives at T3
    """  # noqa
    simulation = 'c1y2y1_2trainsdiffstation'
    sim = OSRD(
        dir=dir,
        infra_json=infra_json,
        simulation_json=simulation_json,
        delays_json=delays_json,
        simulation=simulation
    )

    sim.reset_delays()
    sim.add_delay('train0', time_threshold=80, delay=50.)
    sim.add_delays_in_results()
