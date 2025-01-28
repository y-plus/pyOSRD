import shutil

import pytest
import networkx as nx

from pyosrd import OSRD
from pyosrd.groot import Groot


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


@pytest.fixture
def groot_1train():
    g = Groot()

    g.zones = {'A': 'A', 'B': 'B', 'C': 'C'}
    g.times = {
        'train1': {
            'A': (0, 3),
            'B': (2.5, 5.5),
            'C': (5, 8),
        },
    }
    g._zones_graph = nx.DiGraph()
    g._zones_graph.add_edges_from(
        [
            ('A', 'B'),
            ('B', 'C'),
        ]
    )
    g.min_durations = {
        'train1': {
            'A': 2,
            'B': 2,
            'C': 2,
        },
    }
    g.ends_with_a_signal = {
            'A': True,
            'B': True,
            'C': True,
    }
    g.stations = ['A', 'C']
    return g


@pytest.fixture
def groot_2trains():
    g = Groot()

    g.zones = {'A': 'A', 'B': 'B', 'C': 'C'}
    g.times = {
        'train1': {
            'A': (0, 3),
            'B': (2.5, 5.5),
            'C': (5, 8),
        },
        'train2': {
            'A': (4, 7),
            'B': (6.5, 9.5),
            'C': (9, 12),
        },
    }
    g._zones_graph = nx.DiGraph()
    g._zones_graph.add_edges_from(
        [
            ('A', 'B'),
            ('B', 'C'),
        ]
    )
    g.min_durations = {
        'train1': {
            'A': 2,
            'B': 2,
            'C': 2,
        },
        'train2': {
            'A': 2,
            'B': 2,
            'C': 2,
        },
    }
    g.ends_with_a_signal = {
            'A': True,
            'B': True,
            'C': True,
    }
    g.stations = ['A', 'C']
    return g
