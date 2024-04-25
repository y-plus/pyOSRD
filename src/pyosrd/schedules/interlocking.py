import copy

from typing import Protocol

import pandas as pd


class Schedule(Protocol):
    _df: pd.DataFrame
    trains: list[int | str]
    path: list[int | str]
    starts: pd.DataFrame


def with_interlocking_constraints(
    self: Schedule,
    n_blocks_between_trains: int = 1,
    switch_change_delay: float = 120.,
) -> Schedule:
    """Schedule with added delays to represent the interlocking system

    Parameters
    ----------

    n_blocks_between_trains : int, optional
        Number of blocks/zones (not switch) between two trains
    switch_change_delay : float, optional
        Add a delay for the switch to move when two consecutive
        trains do not have the same path before/after
        the siwtch. Delay in seconds, by default 120.

    Returns
    -------
    Schedule
        New schedule with added zone occupation delays

    Raises
    ------
    NotImplementedError
        if n_blocks_between_trains >= 1
    """

    new_schedule = copy.deepcopy(self)

    if n_blocks_between_trains > 1:
        raise NotImplementedError(
            'Current implementation does not allow more than '
            '1 block between trains'
        )

    for train in self.trains:
        zones = self.path(train)

        for zone_idx, zone in enumerate(zones[:-1]):
            next_zone = zones[
                zone_idx + n_blocks_between_trains
                if zone_idx < len(zones) - n_blocks_between_trains
                else -1
            ]

            trains_sorted = (
                self.starts
                .loc[zone]
                .dropna()
                .sort_values()
                .index
            ).tolist()
            train_idx = trains_sorted.index(train)
            next_train = (
                trains_sorted[train_idx+1]
                if train_idx < len(trains_sorted)-1
                else None
            )

            if next_train is not None:
                train_comes_from = self.path(train)[zone_idx-1]
                train_goes_to = self.path(train)[zone_idx+1]
                next_train_comes_from = self.path(next_train)[zone_idx-1]
                next_train_goes_to = self.path(next_train)[zone_idx+1]

                route_modification = (
                    (train_comes_from != next_train_comes_from)
                    or (train_goes_to != next_train_goes_to)
                )
            else:
                route_modification = False

            if route_modification:  # zone occupied until switch is changed
                new_schedule._df.loc[zone, (train, 'e')] =\
                    self._df.loc[zone, (train, 'e')] + switch_change_delay
            elif next_train:  # zone occupied until next zone is free
                new_schedule._df.loc[zone, (train, 'e')] =\
                    self._df.loc[next_zone, (train, 'e')]

    return new_schedule
