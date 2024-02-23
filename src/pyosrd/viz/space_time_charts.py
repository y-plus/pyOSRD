import matplotlib.pyplot as plt
from matplotlib.axes._axes import Axes
from plotly import graph_objects as go

from pyosrd.osrd import Point


def _data_and_points_to_plot(
    self,
    train: int,
    eco_or_base: str,
    points_to_show: str,
) -> tuple[list, dict]:

    data = []
    for i, train_id in enumerate(self.trains):
        t = [
            record['time'] / 60.
            for record in self._head_position(i, eco_or_base)
        ]
        offset = [
            self.offset_in_path_of_train(
                Point(
                    id='',
                    track_section=record['track_section'],
                    type='record',
                    position=record['offset']
                ),
                train
            )
            for record in self._head_position(i)
        ]
        data.append({"x": t, "y": offset, "label": train_id})

    points = {
        point['id']: point['offset']
        for point in self.points_encountered_by_train(train)
        if point['type'] in points_to_show
    }

    return data, points


def space_time_chart(
    self,
    train: int,
    eco_or_base: str = 'base',
    points_to_show: List[str] =
        ['station', 'switch', 'departure', 'arrival'],
) -> Axes:
    """Draw space-time graph for a given train

    >>> ax = sim.space_time_chart(train=0, ...)

    Parameters
    ----------
    train : int
        Train index
    eco_or_base : str, optional
        Draw eco or base simulation ?, by default 'base'
    points_to_show : List[str], optional
        List of points types shown on y-axis.
        Possible choices are 'signal', 'detector', 'station', 'switch',
        'arrival', 'departure'.
        by default ['station', 'switch', 'departure', 'arrival']

    Returns
    -------
    Axes
        Matplotlib axe object
    """

    data, points = _data_and_points_to_plot(
        self,
        train=train,
        eco_or_base=eco_or_base,
        points_to_show=points_to_show,
    )

    _, ax = plt.subplots()

    for offset in points.values():
        ax.axhline(offset, linestyle='-', color='#aaa', linewidth=.5)

    ax.set_yticks(
        [offset for offset in points.values()],
        [id for id in points],
    )

    for t in data:
        ax.plot(t['x'], t['y'], label=t["label"], linewidth=3)

    ax.legend()

    ax.set_xlim(left=0)
    ax.set_xlabel('Time [min]')
    ax.set_title(
        self.trains[train]
        + f" ({eco_or_base})"
    )

    return ax


def space_time_chart_plotly(
    self,
    train: int,
    eco_or_base: str = 'base',
    points_to_show: List[str] =
        ['station', 'switch', 'departure', 'arrival'],
) -> go.Figure:
    """Draw space-time graph for a given train

    >>> ax = sim.space_time_chart(train=0, ...)

    Parameters
    ----------
    train : int
        Train index
    eco_or_base : str, optional
        Draw eco or base simulation ?, by default 'base'
    points_to_show : List[str], optional
        List of points types shown on y-axis.
        Possible choices are 'signal', 'detector', 'station', 'switch',
        'arrival', 'departure'.
        by default ['station', 'switch', 'departure', 'arrival']

    Returns
    -------
    go.Figure
        Plotly Graph Object
    """

    data, points = _data_and_points_to_plot(
        self,
        train=train,
        eco_or_base=eco_or_base,
        points_to_show=points_to_show,
    )

    fig = go.Figure(
        data=[
            go.Scatter(x=t['x'], y=t['y'], name=t['label'])
            for t in data
        ],
        layout={
            "title": f'train {train} ({eco_or_base})',
            "template": "simple_white",
            "xaxis_title": 'Time [min]',
            "hovermode": "x unified"
        },
    )

    for offset in points.values():
        fig.add_hline(
            y=offset,
            line_width=.5,
            # line_dash="dash",
            line_color="black"
        )

    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=[offset for offset in points.values()],
            ticktext=[p for p in points]
        )
    )

    return fig
