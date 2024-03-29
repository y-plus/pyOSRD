import pandas as pd


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
