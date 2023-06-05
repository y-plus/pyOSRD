import os

import pytest
from rlway.schedules import Schedule
from rlway.pyosrd import OSRD

from ._build_case_cvg_dvg import infra_cvg_dvg, simulation_cvg_dvg_two_trains
from ._build_case_two_lanes import infra_two_lanes, simulation_two_lanes_two_trains


@pytest.fixture
def three_trains() -> Schedule:
    schedule = Schedule(6, 3)

    schedule.df.at[0, 0] = [0, 1]
    schedule.df.at[2, 0] = [1, 2]
    schedule.df.at[3, 0] = [2, 3]
    schedule.df.at[4, 0] = [3, 4]

    schedule.df.at[1, 1] = [1, 2]
    schedule.df.at[2, 1] = [2, 3]
    schedule.df.at[3, 1] = [3, 4]
    schedule.df.at[5, 1] = [4, 5]

    schedule.df.at[0, 2] = [2, 3]
    schedule.df.at[2, 2] = [3, 4]
    schedule.df.at[3, 2] = [4, 5]
    schedule.df.at[4, 2] = [5, 6]

    return schedule


@pytest.fixture
def two_trains() -> Schedule:
    schedule = Schedule(6, 2)

    schedule.df.at[0, 0] = [0, 1]
    schedule.df.at[2, 0] = [1, 2]
    schedule.df.at[3, 0] = [2, 3]
    schedule.df.at[4, 0] = [3, 4]

    schedule.df.at[1, 1] = [1, 2]
    schedule.df.at[2, 1] = [2, 3]
    schedule.df.at[3, 1] = [3, 4]
    schedule.df.at[5, 1] = [4, 5]

    return schedule


@pytest.fixture
def two_trains_two_blocks_before_dvg() -> Schedule:
    schedule = Schedule(7, 2)

    schedule.df.at[0, 0] = [0, 1]
    schedule.df.at[2, 0] = [1, 2]
    schedule.df.at[3, 0] = [2, 3]
    schedule.df.at[4, 0] = [3, 4]
    schedule.df.at[5, 0] = [4, 5]

    schedule.df.at[1, 1] = [1, 2]
    schedule.df.at[2, 1] = [2, 3]
    schedule.df.at[3, 1] = [3, 4]
    schedule.df.at[4, 1] = [4, 5]
    schedule.df.at[6, 1] = [5, 6]

    return schedule


# Done outside of the fixture function
# because otherwise it would be done each time the fixture is used

built_infra = infra_cvg_dvg()
built_simulation = simulation_cvg_dvg_two_trains(built_infra)

built_infra.save('infra.json')
built_simulation.save('simulation.json')

cvg_dvg = OSRD()
cvg_dvg.run()
for file in ['infra', 'simulation', 'results']:
    os.remove(file+'.json')


@pytest.fixture
def osrd_cvg_dvg_missing_sim():
    return OSRD(
        results_json="missing.json",
        simulation_json="missing.json",
    )


@pytest.fixture
def osrd_cvg_dvg_before_run():
    return OSRD(results_json="missing.json")


@pytest.fixture
def osrd_cvg_dvg() -> OSRD:
    return cvg_dvg


built_infra = infra_two_lanes()
built_simulation = simulation_two_lanes_two_trains(built_infra)

built_infra.save('infra.json')
built_simulation.save('simulation.json')

two_lanes = OSRD()
two_lanes.run()
for file in ['infra', 'simulation', 'results']:
    os.remove(file+'.json')


@pytest.fixture
def osrd_two_lanes() -> OSRD:
    return two_lanes
