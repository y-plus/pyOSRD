import numpy as np
import plotly.graph_objects as go

from pyosrd.delays_between_simulations import calculate_delays_at_points
from pyosrd.utils import seconds_to_hour, hour_to_seconds


def plot_delays(
    self,
    ref_sim,
    eco_or_base: str = 'eco',
    tmin: float | str | None = None,
    tmax: float | str | None = None,
    dmax: float | str | None = None,
) -> go.Figure:

    if not tmin:
        tmin = min(self.departure_times)
    if isinstance(tmin, str):
        tmin = hour_to_seconds(tmin)
    if isinstance(tmax, str):
        tmax = hour_to_seconds(tmax)

    if not tmax:
        tmax = round(max(self.last_arrival_times))
    time_interp = np.linspace(tmin, tmax, int(tmax-tmin)+1)

    data = {'time': time_interp}
    for train in self.trains:
        delay = calculate_delays_at_points(self, ref_sim, train, eco_or_base)
        t = [d[1] for d in delay]
        d = [d[2] for d in delay]
        d_interp = np.interp(
            time_interp,
            t,
            d
        )
        data[train] = [
            d_interp[i] if time > min(t) else 0
            for i, time in enumerate(time_interp)
        ]

    time = data['time']
    delays = {k: v for k, v in data.items() if k != 'time'}

    fig = go.Figure(
        data=[
            go.Scatter(
                name=train,
                x=time,
                y=delays,
                stackgroup='Delays'
            )
            for train, delays in delays.items()
        ],
        layout={
                "title": 'Cumulated delays over time',
                "template": "simple_white",
                "hovermode": "x unified"
            },
    )

    if isinstance(dmax, str):
        dmax = hour_to_seconds(dmax)
    xmax = round(max(time))
    xticks = list(range(0, xmax + xmax // 5, xmax // 5))
    if not dmax:
        ymax = int(sum(v[-1] for v in delays.values())) + 1
    else:
        ymax = int(dmax) + 1

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
        )
    )
    if dmax:
        fig.update_yaxes(range=[0, ymax])
    return fig
