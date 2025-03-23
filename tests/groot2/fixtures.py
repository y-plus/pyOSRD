import shutil

import networkx as nx
import pytest


from pyosrd import OSRD
from pyosrd.groot2 import Groot
from pyosrd.groot2 import from_sim


@pytest.fixture
def groot2_1train() -> Groot:
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
def groot2_2trains() -> Groot:
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


@pytest.fixture(scope='session')
def groot2_vu_alternate() -> Groot:
    sim = OSRD(
        dir='voie_unique_alternate',
        simulation="voie_unique_circulations",
        params_use_case={
            "num_stations":3,
            'num_blocks_between_stations': 6,
            'num_trains': 3,
            'alternate': True,
        }
    )
    shutil.rmtree('voie_unique_alternate', ignore_errors=True)
    return from_sim(sim)
    

@pytest.fixture(scope='session')
def groot2_vu_following() -> Groot:
    sim = OSRD(
        dir='voie_unique_following',
        simulation="voie_unique_circulations",
        params_use_case={
            "num_stations":3,
            'num_blocks_between_stations': 6,
            'num_trains': 2,
        }
    )
    shutil.rmtree('voie_unique_following', ignore_errors=True)
    return from_sim(sim)
    

@pytest.fixture(scope='session')
def groot2_crossing() -> Groot:
    sim = OSRD(
        dir='voie_unique_crossing',
        simulation="voie_unique_circulations",
        params_use_case={
            "num_stations":3,
            'num_blocks_between_stations': 6,
            'num_trains': 4,
            'alternate': True,
            'crossing': True
        }
    )
    shutil.rmtree('voie_unique_crossing', ignore_errors=True)
    return from_sim(sim)

   

@pytest.fixture(scope='session')
def groot2_reroute() -> Groot:
    sim = OSRD(
        dir='reroute',
        simulation="c1yy3yy1_3trains",
    )
    shutil.rmtree('reroute', ignore_errors=True)
    return from_sim(sim)
