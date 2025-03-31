import shutil
from typing import Generator

import pytest

from pyosrd import OSRD

from .groot.fixtures import *
from .groot2.fixtures import *
from .agents.fixtures import *


@pytest.fixture(scope='session')
def osrd_cvg_dvg_missing_sim() -> Generator[OSRD]:
    yield OSRD(
        dir="tmp",
        results_json="missing.json",
        simulation_json="missing.json",
    )
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def osrd_cvg_dvg_before_run() -> Generator[OSRD]:
    yield OSRD(dir="tmp5", results_json="missing.json")
    shutil.rmtree('tmp5', ignore_errors=True)


@pytest.fixture(scope='session')
def simulation_cvg_dvg() -> Generator[OSRD]:
    yield OSRD(dir='tmp', simulation='cvg_dvg')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def simulation_station_builder() -> Generator[OSRD]:
    yield OSRD(
        dir='tmp_station_builder',
        simulation='station_builder_1station_2trains'
    )
    shutil.rmtree('tmp_station_builder', ignore_errors=True)


@pytest.fixture(scope='function')
def modify_sim() -> Generator[OSRD]:
    yield OSRD(dir='tmp', simulation='cvg_dvg')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def simulation_station_capacity2() -> Generator[OSRD]:
    yield OSRD(dir='tmp', simulation='station_capacity2')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def simulation_point_switch() -> Generator[OSRD]:
    yield OSRD(dir='tmp', simulation='point_switch')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def simulation_straight_line() -> Generator[OSRD]:
    yield OSRD(dir='tmp', simulation='straight_line')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def simulation_double_switch() -> Generator[OSRD]:
    yield OSRD(dir='tmp', simulation='double_switch')
    shutil.rmtree('tmp', ignore_errors=True)


@pytest.fixture(scope='session')
def infra_crossing() -> Generator[OSRD]:
    yield OSRD(dir='tmp_crossing', infra='c2x2')
    shutil.rmtree('tmp_crossing', ignore_errors=True)
    shutil.rmtree('tmp_crossing_sub', ignore_errors=True)


@pytest.fixture(scope='session')
def infra_double_slip() -> Generator[OSRD]:
    yield OSRD(dir='tmp_double_slip', infra='c2xx2')
    shutil.rmtree('tmp_double_slip', ignore_errors=True)
    shutil.rmtree('tmp_double_slip_sub', ignore_errors=True)


@pytest.fixture(scope='session')
def infra_point_switch() -> Generator[OSRD]:
    yield OSRD(dir='tmp_point_switch', simulation='point_switch')
    shutil.rmtree('tmp_point_switch', ignore_errors=True)
    shutil.rmtree('tmp_point_switch_sub', ignore_errors=True)


@pytest.fixture(scope='session')
def infra_station_c2() -> Generator[OSRD]:
    yield OSRD(dir='tmp_station_c2', simulation='station_capacity2')
    shutil.rmtree('tmp_station_c2', ignore_errors=True)
    shutil.rmtree('tmp_station_c2_sub', ignore_errors=True)

