import networkx as nx
import numpy as np
import PIL

from networkx.utils import edges_equal, nodes_equal

from pyosrd.schedules.graph import _mermaid_graph


def test_schedule_graph(two_trains):

    G = nx.DiGraph([
        (0, 2),
        (1, 2),
        (2, 3),
        (3, 4),
        (3, 5)
    ])

    nx.set_node_attributes(
        G,
        {
            0: np.array([0, 1, 0, 0]),
            1: np.array([0, 0, 1, 2]),
            2: np.array([1, 2, 2, 3]),
            3: np.array([2, 3, 3, 4]),
            4: np.array([3, 4, 0, 0]),
            5: np.array([0, 0, 4, 5]),
        },
        'times'
    )

    assert nodes_equal(G.nodes, two_trains.graph.nodes)
    assert edges_equal(G.edges, two_trains.graph.edges)


def test_schedules_mermaid_graph(two_trains):
    assert _mermaid_graph(two_trains) == \
        'graph LR;2-->3;3-->4;3-->5;0-->2;1-->2'


def test_schedules_draw_graph_returns_image(two_trains):
    print(type(two_trains.draw_graph()))
    assert isinstance(
        two_trains.draw_graph(),
        PIL.JpegImagePlugin.JpegImageFile
    )
