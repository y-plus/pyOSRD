import plotly
import plotly.graph_objects as go

from pyosrd.utils import seconds_to_hour, hour_to_seconds
from pyosrd.groot import Groot
from pyosrd.groot.compare import difference_departures_per_zone
from pyosrd.groot.delay_analysis import merge_time_entries, \
    build_dict_difference_departures_per_departure_times, \
    get_latest_non_zero_delay_for_each_train, \
    get_earliest_non_zero_delay_for_each_train, \
    interpolate_entries

from pyosrd.viz.colors import train_colors

def plot_groot_delays(
    disrupted: Groot,
    ref: Groot,
    all_trains: bool = True,
    tmin: float | str | None = None,
    tmax: float | str | None = None,
    dmax: float | str | None = None,
    ref_fig: go.Figure | None = None,
) -> go.Figure:
    """Build a figure showing the cumulated delay of the disrupted groot

    Parameters
    ----------
    disrupted : Groot
        The disrupted or dispatched groot.
    ref : Groot
        THe reference groot.
    all_trains : bool
        true if we want to keep delays for all trains or only for
        trains active at each time point (delay will end at 0 if false)

    Returns
    -------
    go.Figure
        A figure showing the cumulated delays of the disrupted groot.
    """
    diff_departure_time_per_zone = difference_departures_per_zone(
        disrupted,
        ref
    )
    diff_departure_time_per_dep_time = \
        build_dict_difference_departures_per_departure_times(
            disrupted,
            ref,
            diff_departure_time_per_zone,
            not all_trains
        )
    all_entries = merge_time_entries(diff_departure_time_per_dep_time)
    interpolated_diffs = interpolate_entries(
        diff_departure_time_per_dep_time,
        all_entries,
        all_trains
    )

    time = all_entries
    delays = {
        val: [val_time for val_time in key.values()]
        for val, key in interpolated_diffs.items()
    }
    earliest_non_zero_delays = get_earliest_non_zero_delay_for_each_train(
        interpolated_diffs
    )
    sorted_trains = [
        k for k, _ in sorted(
            earliest_non_zero_delays.items(),
            reverse=not all_trains,
            key=lambda item: item[1]
        )
    ]

    if not all_trains:
        latest_non_zero_delays = get_latest_non_zero_delay_for_each_train(
            interpolated_diffs
        )
        time = [t for t in time if t < max(
            [val for val in latest_non_zero_delays.values()]
        )]

    colors = train_colors(disrupted)

    fig = go.Figure(
        data=[
            go.Scatter(
                name=train,
                x=time,
                y=delays[train],
                stackgroup='Delays',
                line={'width': 0},
                fillcolor=colors[train]

            )
            for train in sorted_trains
            if sum(delays[train]) > 0
        ],
        layout={
                "template": "simple_white",
                "hovermode": "x unified",
            },
    )
    if not fig.data:
        return fig

    if ref_fig:
        dmax = ref_fig.layout.yaxis.tickvals[-2]
        tmin = ref_fig.layout.xaxis.tickvals[0]
        tmax = ref_fig.layout.xaxis.tickvals[-2]

    if tmin is not None:
        if isinstance(tmin, str):
            tmin = hour_to_seconds(tmin)
    if tmax is not None:
        if isinstance(tmax, str):
            tmax = hour_to_seconds(tmax)
    if dmax is not None:
        if isinstance(dmax, str):
            dmax = hour_to_seconds(dmax)
    fig.update_xaxes(range=[tmin, tmax])
    fig.update_yaxes(range=[0, dmax])

    if tmin is None:
        tmin = round(min(time))
    if tmax is None:
        tmax = round(max(time))
    xticks = list(range(tmin, tmax + (tmax-tmin) // 5, (tmax-tmin) // 5))

    if dmax:
        ymax = dmax
    else:
        ymax = int(sum(max(v) for v in delays.values())) + 1
    yticks = list(range(0, ymax + ymax // 5, ymax // 5))

    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=yticks,
            ticktext=[seconds_to_hour(ytick) for ytick in yticks]
        ),
        xaxis=dict(
            tickmode='array',
            tickvals=xticks,
            ticktext=[seconds_to_hour(xtick) for xtick in xticks]
        ),
        showlegend=True,
        legend_title_text='Cumulated delays' if all_trains else 'Active delays',
        margin=dict(l=20, r=20, t=30, b=30),
    )

    return fig
