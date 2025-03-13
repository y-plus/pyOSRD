import matplotlib.pyplot as plt
from matplotlib.axes._axes import Axes
import plotly
from plotly import graph_objects as go

from pyosrd.osrd import Point
from pyosrd.utils import seconds_to_hour


def _data_and_points_to_plot(
    self,
    train: int,
    eco_or_base: str,
    points_to_show: list[str],
) -> tuple[list, dict]:

    data = []
    for i, train_id in enumerate(self.trains):
        t = [
            record['time']
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
            for record in self._head_position(i, eco_or_base)
        ]

        track_sections = self.train_track_sections(train_id)
        track_section_ids = [
            t['id'] for t in track_sections
        ]
        for p in self.points_encountered_by_train(train_id):
            if p ['type'] == 'switch':
                switch = next(
                    s for s in self.infra['switches']
                    if s['id'] == p['id']
                )
                port_key = next(
                    p for p, v in switch['ports'].items()
                    if v['track'] in track_section_ids
                )
                port = switch['ports'][port_key]
                position = 0 if port['endpoint'] == 'BEGIN' else self.track_section_lengths[port['track']]
                t.append(p['t_'+eco_or_base])
                offset.append(
                    self.offset_in_path_of_train(
                        Point(
                            id='',
                            track_section=port['track'],
                            type='record',
                            position=position
                        ),
                        train
                    )
                )
            if p['type'] == 'detector':
                detector = next(
                    d for d in self.infra['detectors']
                    if d['id'] == p['id']
                )
                t.append(p['t_'+eco_or_base])
                offset.append(
                    self.offset_in_path_of_train(
                        Point(
                            id='',
                            track_section=detector['track'],
                            type='record',
                            position=detector['position']
                        ),
                        train
                    )
                )
        tuples = [
            t for t in zip(t, offset)
            if offset is not None
        ]
        tuples.sort(key=lambda t: t[0])
        t_sorted = [t[0] for t in tuples]
        offset_sorted = [t[1] for t in tuples]
       
        if not all(y is None for y in offset_sorted):
            data.append({"x": t_sorted, "y": offset_sorted, "label": train_id})

    points = {
        point['id']: point['offset']
        for point in self.points_encountered_by_train(train)
        if point['type'] in points_to_show
    }

    station_names = dict()
    for point in self.points_encountered_by_train(train):
        if point['type'] == 'station':
            try:
                op = next(
                    o for o in self.infra['operational_points']
                    if o['id'] == point['id']
                )
                name = op['extensions']['identifier']['name']
                station_names[point['id']] = name
            except (StopIteration, KeyError):
                pass

    points_with_station_names = {
        (k if k not in station_names else station_names[k]): v
        for k, v in points.items()
    }

    return data, points_with_station_names


def space_time_chart(
    self,
    train: int | str,
    eco_or_base: str = 'base',
    points_to_show: list[str] =
        ['station', 'switch', 'departure', 'arrival'],
) -> Axes:
    """Draw space-time graph for a given train

    >>> ax = sim.space_time_chart(train=0, ...)

    Parameters
    ----------
    train : int | str
        Train index or label
    eco_or_base : str, optional
        Draw eco or base simulation ?, by default 'base'
    points_to_show : list[str], optional
        list of points types shown on y-axis.
        Possible choices are 'signal', 'detector', 'station', 'switch',
        'arrival', 'departure'.
        by default ['station', 'switch', 'departure', 'arrival']

    Returns
    -------
    Axes
        Matplotlib axe object
    """
    if isinstance(train, str):
        train = self.trains.index(train)

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
        ax.plot(t['x'], t['y'], label=t["label"], linewidth=2)

    ax.legend()

    ax.set_xlim(left=min(self.departure_times))
    ax.set_xticks(
        [
            label._x
            for label in ax.get_xticklabels()
        ],
        [
            seconds_to_hour(int(float(label.get_text())))
            for label in ax.get_xticklabels()
        ]
    )
    plt.locator_params(axis='x', nbins=6)
    # ax.set_xlabel('Time')
    ax.set_title(
        self.trains[train]
        + f" ({eco_or_base})"
    )

    return ax


def space_time_chart_plotly(
    self,
    train: int | str,
    ref = None,
    eco_or_base: str = 'eco',
    points_to_show: list[str] =
        ['station'],
    reverse: bool = False,
) -> go.Figure:
    """Draw space-time graph for a given train

    >>> ax = sim.space_time_chart(train=0, ...)

    Parameters
    ----------
    train : int | str
        Train index or label
    eco_or_base : str, optional
        Draw eco or base simulation ?, by default 'eco'
    points_to_show : list[str], optional
        list of points types shown on y-axis.
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

    if ref:
        ref_data, _ = _data_and_points_to_plot(
        ref,
        train=train,
        eco_or_base=eco_or_base,
        points_to_show=points_to_show,
    )
    else:
        ref_data = data

    ref_data = [
        ref_d
        for ref_d in ref_data
        if ref_d != next(d for d in data if d['label']==ref_d['label'])
    ]

    if isinstance(train, int):
        train_label = self.trains[train]
    else:
        train_label = train

    for d in data + ref_data:
        d['h'] = [seconds_to_hour(x).split('.')[0] for x in d['x']]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=d['x'],
                y=d['y'],
                customdata=d['h'],
                name=d['label'],
                hovertemplate="%{customdata} (%{y:.0f} m)",
                line = dict(color='black', width=3.5) if d['label']==train_label else dict(width=1.5),
                mode='lines',
            )
            for d in data
        ] + [
            go.Scatter(
                x=d['x'],
                y=d['y'],
                customdata=d['h'],
                name=d['label']+'(ref)',
                hovertemplate="%{customdata} (%{y:.0f} m)",
                line = (
                    dict(color='black', width=2.5, dash='dash') 
                    if d['label']==train_label
                    else dict(
                        width=1.5,
                        dash='dash',
                        color=plotly.colors.qualitative.D3[
                            self.trains.index(d['label']) % 10
                        ]
                    )
                ),
                mode='lines',
            )
            for d in ref_data
        ],
        layout={
            "title": f'{train_label} ({eco_or_base})',
            "template": "simple_white",
            # "hovermode": "x unified",
        },
    )

    for offset in points.values():
        fig.add_hline(
            y=offset,
            line_width=.5,
            # line_dash="dash",
            line_color="black"
        )
    xmin = round(min([d['x'][0] for d in data]))
    xmax = round(max([d['x'][-1] for d in data]))
    xticks = list(range(xmin, xmax + xmax // 5, (xmax-xmin) // 5))

    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=[offset for offset in points.values()],
            ticktext=[p for p in points]
        ),
        xaxis=dict(
            tickmode='array',
            tickvals=xticks,
            ticktext=[seconds_to_hour(xtick) for xtick in xticks]
        )
    )
    if reverse:
        fig.update_yaxes(autorange='reversed')

    return fig
