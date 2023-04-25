import copy
from pandas.testing import assert_frame_equal
from matplotlib.text import Text
import matplotlib.pyplot as plt


def test_schedules_sort(two_trains):
    random_sorted = copy.deepcopy(two_trains.add_delay(0, 0, .5))
    random_sorted._df = random_sorted.df.sample(frac=1)
    assert_frame_equal(
        random_sorted.sort().df,
        two_trains.add_delay(0, 0, .5).df
    )


def test_schedules_plot(two_trains):
    ax = two_trains.plot()
    assert ax.get_xlabel() == 'Time'
    assert ax.get_ylabel() == 'Track sections'
    assert (
        [text._text for text in ax.get_legend().get_texts()]
        == [str(train) for train in two_trains.trains]
    )
    plt.close()


def test_schedules_draw_graph(two_trains):
    ax = two_trains.draw_graph()
    for node in two_trains.graph.nodes:
        assert str(node) in [
            text._text
            for text in ax.get_children()
            if isinstance(text, Text)
        ]