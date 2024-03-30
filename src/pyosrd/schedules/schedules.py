import copy

import pandas as pd

from pyosrd.utils import hour_to_seconds


class Schedule(object):

    from .trajectories import (
        trajectory,
        previous_zone,
        next_zone,
        is_a_point_switch,
        is_just_after_a_point_switch,
        first_in,
    )
    from .plot import sort, plot
    from .conflicts import (
        conflicts,
        has_conflicts,
        first_conflict,
        earliest_conflict,
    )
    from .actions import (
        add_delay,
        shift_train_after,
        shift_train_departure,
        propagate_delay,
        is_action_needed,
    )
    from .graph import graph, draw_graph
    from .delays import (
        delays,
        total_delay_at_stations,
        compute_weighted_delays,
        train_delay,
    )

    def __init__(self, num_zones: int, num_trains: int):

        self._num_zones = num_zones
        self._num_trains = num_trains
        self._df = pd.DataFrame(
            columns=pd.MultiIndex.from_product(
                [range(self._num_trains), ['s', 'e']]
            ),
            index=range(num_zones)
        )

    def __repr__(self) -> str:
        return str(self._df)

    @property
    def num_zones(self) -> int:
        """Number of zones"""
        return len(self._df)

    @property
    def zones(self) -> list[int]:
        """list of zones"""
        return self._df.index.to_list()

    @property
    def num_trains(self) -> int:
        """Number of trains"""
        return len(self._df.columns.levels[0])

    @property
    def trains(self) -> list[int]:
        """list of trains"""
        return getattr(
            self,
            '_trains',
            list(self._df.columns.levels[0])
        )

    def set_train_labels(self, labels: list[str]) -> None:
        self._df.columns = pd.MultiIndex.from_product(
            [labels, ['s', 'e']]
        )

    @property
    def df(self) -> pd.DataFrame:
        """ Schedule as a pandas DataFrame"""
        return self._df

    def set(self, train, zone, interval):
        """Set times for a train at a given zone"""
        self._df.at[zone, train] = interval

    @property
    def starts(self) -> pd.DataFrame:
        """Times when the trains enter the zones"""
        return self._df.loc[
                pd.IndexSlice[:],
                pd.IndexSlice[:, 's']
            ].set_axis(self._df.columns.levels[0], axis=1).astype(float)

    @property
    def ends(self) -> pd.DataFrame:
        """Times when the trains leave the zones"""
        return self._df.loc[
                pd.IndexSlice[:],
                pd.IndexSlice[:, 'e']
            ].set_axis(self._df.columns.levels[0], axis=1).astype(float)

    @property
    def durations(self) -> pd.DataFrame:
        """How much time do the trains occupy the zones"""
        return self.ends - self.starts

    def start_from(
        self,
        time: float | str,
    ) -> "Schedule":
        """Make a schedule start at a given time"

        Parameters
        ----------
        time : float | str
           Start time, given either in seconds or
           in string format 'hh:mm:ss'

        Returns
        -------
        Schedule
            New schedule startinf from the given time
        """

        if isinstance(time, str):
            time = hour_to_seconds(time)

        new_schedule = copy.copy(self)
        new_schedule._df = new_schedule._df.where(
            new_schedule._df > time,
            time
        )
        check = pd.DataFrame(
            columns=self.df.columns,
            index=self.df.index
        )
        for i, col in enumerate(check.columns):
            if i % 2 == 0:
                check[col] = (
                    new_schedule._df[col]
                    != new_schedule._df[new_schedule._df.columns[i+1]]
                )
            else:
                check[col] = (
                    new_schedule._df[col]
                    != new_schedule._df[new_schedule._df.columns[i-1]]
                )

        new_schedule._df = new_schedule._df[check].dropna(how='all')
        return new_schedule
