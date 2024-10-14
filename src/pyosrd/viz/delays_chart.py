
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.axes._axes import Axes
from plotly import graph_objects as go

from pyosrd.utils import seconds_to_hour
from pyosrd.delays_between_simulations import calculate_delay_f_time

def _delays_interp(
    self,
    ref_sim,
    eco_or_base = 'base'

) -> dict[str, list[float]]:
    ...
    tmin, tmax = min(self.departure_times), round(max(self.last_arrival_times))
    time_interp = np.linspace(tmin, tmax, int(tmax-tmin)+1)

    delays_interp = {'time': time_interp}
    for train in self.trains:
        t = [r['time'] for r in self._head_position(train, eco_or_base)]
        delay = calculate_delay_f_time(self, ref_sim, train, eco_or_base)
        delay_interp = np.interp(
            time_interp,
            t,
            delay
        )
        delays_interp[train] = [
            delay_interp[i] if time > min(t) else 0
            for i, time in enumerate(time_interp)
    ]

    return delays_interp


def delays_chart_plotly(
    self,
    ref_sim,
    eco_or_base: str = 'base'
) -> go.Figure:
    
    data = _delays_interp(
        self,
        ref_sim,
        eco_or_base=eco_or_base
    )

    time = data['time']
    delays = {k: v for k, v in data.items() if k != 'time'}

    fig = go.Figure(
        data=[
            go.Scatter(
                name = train,
                x = time,
                y = delays,
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

    xmax = round(max(time))
    xticks = list(range(0, xmax + xmax // 5, xmax // 5))
    ymax = int(sum(v[-1] for v in delays.values()))
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

    return fig


def delays_chart(    
    self,
    ref_sim,
    eco_or_base: str = 'base'
) -> Axes:
    
    data = _delays_interp(
        self,
        ref_sim,
        eco_or_base=eco_or_base
    )
        
    time = data['time']
    delays = {k: v for k, v in data.items() if k != 'time'}

    _, ax = plt.subplots()

    ax.stackplot(
        time,
        *[
            v for v in delays.values()
        ],
        labels=self.trains
    )
    ax.legend(loc='upper left')

    ax.set_xlim(min(time), max(time))

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
    ax.set_yticks(
        [
            label._y
            for label in ax.get_yticklabels()
        ],
        [
            seconds_to_hour(int(float(label.get_text())))
            for label in ax.get_yticklabels()
        ]
    )
    plt.locator_params(axis='x', nbins=6)

    ax.set_title(
        "Cumulated delays over time"
        + f" ({eco_or_base})"
    )

    return ax
