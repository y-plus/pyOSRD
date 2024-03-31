import copy
from typing import Protocol
import pandas as pd


class Schedule(Protocol):
    _df: pd.DataFrame
    starts: pd.DataFrame
    ends: pd.DataFrame


def shift_train_departure(
    self: Schedule,
    train: int | str,
    time: float
) -> Schedule:
    """Shift the departure by a given time

    All the trajectory is shifted

    Parameters
    ----------
    train : int | str
        Train index or label
    time : float
        Departure's delay

    Returns
    -------
    Schedule
        The new schedule
    """

    if isinstance(train, int):
        train = self.trains[train]

    new_schedule = copy.deepcopy(self)

    new_schedule._df[train] += time

    return new_schedule


def add_delay(
    self: Schedule,
    train: int | str,
    zone: int | str,
    delay: float
) -> Schedule:

    if isinstance(train, int):
        train = self.trains[train]

    start = self._df.loc[zone, (train, 's')]
    new_schedule = copy.deepcopy(self)

    # extend duration in a given zone
    new_schedule._df.loc[zone, (train, 'e')] += delay

    # Add delay to all subsequent zones
    new_schedule._df.loc[
        self._df[pd.IndexSlice[train, 's']] > start,
        pd.IndexSlice[train, :]
    ] += delay

    return new_schedule


def is_action_needed(self, train: int) -> bool:

    action_needed = False
    if self.has_conflicts(train):
        zone, other_train = self.first_conflict(train)
        action_needed = (
            self.is_a_point_switch(train, other_train, zone)
            or
            self.is_just_after_a_point_switch(
                train,
                other_train,
                zone
            )
        )
    return action_needed


def set_priority_train(
    self: Schedule,
    priority_train: int | str,
    train_decelerating: int | str,
    decelerates_in_zone: str,
    until_zone_is_free: str,
 ) -> Schedule:
    """Give the priority to a train on another one

    Parameters
    ----------
    priority_train : int | str
        Priority train index or label
    train_decelerating : int | str
        Other train index or label
    decelerates_in_zone : str
        In which zone should the other train declerates/stops
    until_zone_is_free : str
        Which zone has to be free for the other train to stop decelerating

    Returns
    -------
    Schedule
       The new schedule
    """

    if isinstance(priority_train, int):
        priority_train = self.trains[priority_train]

    if isinstance(train_decelerating, int):
        train_decelerating = self.trains[train_decelerating]

    other_train_wait_time = (
        self.ends.loc[until_zone_is_free, priority_train]
        - self.starts.loc[until_zone_is_free, train_decelerating]
    )

    new_schedule = self.add_delay(
        train_decelerating,
        decelerates_in_zone,
        other_train_wait_time
    )

    return new_schedule
