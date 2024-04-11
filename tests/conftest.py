import shutil

import pytest

from pyosrd import OSRD
from pyosrd.schedules import Schedule, schedule_from_osrd


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

    schedule.set_train_labels(['train1', 'train2', 'train3'])
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

    schedule.set_train_labels(['train1', 'train2'])

    return schedule


@pytest.fixture
def two_trains_hours() -> Schedule:
    schedule = Schedule(6, 2)

    schedule._df.at[0, 0] = [0, 1]
    schedule._df.at[2, 0] = [1, 2]
    schedule._df.at[3, 0] = [2, 3]
    schedule._df.at[4, 0] = [3, 4]

    schedule._df.at[1, 1] = [1, 2]
    schedule._df.at[2, 1] = [2, 3]
    schedule._df.at[3, 1] = [3, 4]
    schedule._df.at[5, 1] = [4, 5]

    schedule._df *= 3_600.

    schedule.set_train_labels(['train1', 'train2'])

    return schedule


@pytest.fixture
def two_trains_two_zones_before_dvg() -> Schedule:
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

    schedule.set_train_labels(['train1', 'train2'])

    return schedule


@pytest.fixture(scope='session')
def osrd_cvg_dvg_missing_sim():
    yield OSRD(
        results_json="missing.json",
        simulation_json="missing.json",
    )
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def osrd_cvg_dvg_before_run():
    yield OSRD(results_json="missing.json")
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def use_case_cvg_dvg():
    yield OSRD(dir='tmp', use_case='cvg_dvg')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def use_case_station_builder():
    yield OSRD(dir='tmp', use_case='station_builder_1station_2trains')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='function')
def modify_sim():
    yield OSRD(dir='tmp2', use_case='cvg_dvg')
    shutil.rmtree('tmp2', ignore_errors=True)


@pytest.fixture(scope='session')
def use_case_station_capacity2():
    yield OSRD(dir='tmp', use_case='station_capacity2')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def use_case_point_switch():
    yield OSRD(dir='tmp', use_case='point_switch')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def use_case_straight_line():
    yield OSRD(dir='tmp', use_case='straight_line')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def use_case_double_switch():
    yield OSRD(dir='tmp', use_case='double_switch')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def schedule_station_capacity2(use_case_station_capacity2) -> Schedule:
    return schedule_from_osrd(use_case_station_capacity2)
