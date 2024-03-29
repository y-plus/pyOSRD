import copy

import matplotlib.pyplot as plt

from matplotlib.axes._axes import Axes


def sort(self):
    """Sort the schedule index by occupancies times"""
    new_schedule = copy.deepcopy(self)
    sorted_idx = self.ends.max(axis=1).sort_values().index
    new_schedule ._df = new_schedule ._df.loc[sorted_idx]
    return new_schedule


def plot(self, alpha: float = .5) -> Axes:
    """Plots a graphical representation of the schedule

    Parameters
    ----------
    alpha : float, optional
        Opacity to distinguish overlapping intervals, by default .5

    Returns
    -------
    Axes
        Matplotlib axes object
    """

    s = copy.copy(self)
    s._df = s.df.dropna(axis=0, how='all')

    _, ax = plt.subplots()
    for train in s.trains:
        ax.barh(
            width=s.durations[train],
            left=s.starts[train],
            y=s._df.index,
            label=str(train),
            height=1,
            alpha=alpha,
        )

    ax.set_xlabel('Time')
    ax.legend()

    return ax
