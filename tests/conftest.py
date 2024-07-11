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
def two_trains_in_line() -> Schedule:
    schedule = Schedule(3, 2)

    schedule.df.at[0, 0] = [0, 1]
    schedule.df.at[1, 0] = [1, 2]
    schedule.df.at[2, 0] = [2, 3]

    schedule.df.at[0, 1] = [1, 2]
    schedule.df.at[1, 1] = [2, 3]
    schedule.df.at[2, 1] = [3, 4]

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
        dir="tmp",
        results_json="missing.json",
        simulation_json="missing.json",
    )
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def osrd_cvg_dvg_before_run():
    yield OSRD(dir="tmp5", results_json="missing.json")
    shutil.rmtree('tmp5', ignore_errors=True)


@pytest.fixture(scope='session')
def simulation_cvg_dvg():
    yield OSRD(dir='tmp', simulation='cvg_dvg')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def simulation_station_builder():
    yield OSRD(
        dir='tmp_station_builder',
        simulation='station_builder_1station_2trains'
    )
    shutil.rmtree('tmp_station_builder', ignore_errors=True)


@pytest.fixture(scope='function')
def modify_sim():
    yield OSRD(dir='tmp', simulation='cvg_dvg')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def simulation_station_capacity2():
    yield OSRD(dir='tmp', simulation='station_capacity2')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def simulation_point_switch():
    yield OSRD(dir='tmp', simulation='point_switch')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def simulation_straight_line():
    yield OSRD(dir='tmp', simulation='straight_line')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def simulation_double_switch():
    yield OSRD(dir='tmp', simulation='double_switch')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def schedule_cvg_dvg(simulation_cvg_dvg) -> Schedule:
    return schedule_from_osrd(simulation_cvg_dvg)


@pytest.fixture(scope='session')
def schedule_station_capacity2(simulation_station_capacity2) -> Schedule:
    return schedule_from_osrd(simulation_station_capacity2)


@pytest.fixture(scope='session')
def schedule_straight_line(simulation_straight_line) -> Schedule:
    return schedule_from_osrd(simulation_straight_line)


@pytest.fixture(scope='session')
def schedule_double_switch(simulation_double_switch) -> Schedule:
    return schedule_from_osrd(simulation_double_switch)


@pytest.fixture(scope='session')
def infra_crossing():
    yield OSRD(dir='tmp_crossing', infra='c2x2')
    shutil.rmtree('tmp_crossing', ignore_errors=True)
    shutil.rmtree('tmp_crossing_sub', ignore_errors=True)


@pytest.fixture(scope='session')
def infra_double_slip():
    yield OSRD(dir='tmp_double_slip', infra='c2xx2')
    shutil.rmtree('tmp_double_slip', ignore_errors=True)
    shutil.rmtree('tmp_double_slip_sub', ignore_errors=True)

@pytest.fixture(scope='session')
def infra_point_switch():
    yield OSRD(dir='tmp_point_switch', simulation='point_switch')
    shutil.rmtree('tmp_point_switch', ignore_errors=True)
    shutil.rmtree('tmp_point_switch_sub', ignore_errors=True)


@pytest.fixture(scope='session')
def infra_station_c2():
    yield OSRD(dir='tmp_station_c2', simulation='station_capacity2')
    shutil.rmtree('tmp_station_c2', ignore_errors=True)
    shutil.rmtree('tmp_station_c2_sub', ignore_errors=True)
