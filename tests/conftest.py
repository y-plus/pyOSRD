import shutil

import pytest
from rlway.schedules import Schedule
from rlway.pyosrd import OSRD


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


@pytest.fixture
def osrd_cvg_dvg_missing_sim():
    return OSRD(
        results_json="missing.json",
        simulation_json="missing.json",
    )


@pytest.fixture
def osrd_cvg_dvg_before_run():
    return OSRD(results_json="missing.json")


cvg_dvg = OSRD(dir='tmp', use_case='cvg_dvg')

@pytest.fixture()
def use_case_cvg_dvg():
    return cvg_dvg


station_capacity2 = OSRD(dir='tmp', use_case='station_capacity2')

@pytest.fixture()
def use_case_station_capacity2():
    return station_capacity2


shutil.rmtree('tmp')
