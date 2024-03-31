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


def shift_train_after(
    self: Schedule,
    train1: int | str,
    train2: int | str,
    zone: int | str
) -> Schedule:
    """Train1 waits until train 2 has freed the zone"""

    if isinstance(train1, int):
        train1 = self.trains[train1]

    if isinstance(train2, int):
        train2 = self.trains[train2]

    train1_waits_at = self.previous_zone(train1, zone)

    # If the zone is the departure,
    # it has no previous zone
    if train1_waits_at is None:
        train1_waits_at = zone

    # If the conflict occurs at a switch point,
    # train 1 waits until the zone
    # after the switch point is free
    if self.is_a_point_switch(train1, train2, zone):
        zone_shift = \
            self.next_zone(train1, zone)
    else:
        zone_shift = zone

    # if the conflict occurs just after a switch point,
    # train should wait before the switch
    if self.is_just_after_a_point_switch(train1, train2, zone):
        train1_waits_at = \
            self.previous_zone(train1, train1_waits_at)

    train1_wait_time = (
        self.ends.loc[zone_shift, train2]
        - self.starts.loc[zone_shift, train1]
    )

    new_schedule = self.add_delay(
        train1,
        train1_waits_at,
        train1_wait_time
    )

    if not new_schedule.is_a_point_switch(train1, train2, zone):
        new_schedule._df.loc[zone, (train1, 's')] = \
            self.ends.loc[zone, train2]

    return new_schedule


def propagate_delay(self, delayed_train: int | str) -> tuple[Schedule, int]:

    if isinstance(delayed_train, int):
        delayed_train = self.trains[delayed_train]

    new_schedule = copy.deepcopy(self)
    decision = False
    while new_schedule.has_conflicts(delayed_train):
        decision = False
        if new_schedule.has_conflicts(delayed_train):

            zone, other_train = \
                new_schedule.first_conflict(delayed_train)
            decision = new_schedule.is_action_needed(delayed_train)

            if not decision:
                first_in = new_schedule.first_in(
                    delayed_train,
                    other_train,
                    zone
                )
                delayed_train = other_train \
                    if first_in == delayed_train else delayed_train
                new_schedule = new_schedule.shift_train_after(
                    delayed_train,
                    first_in,
                    zone
                )
            else:
                break
    return new_schedule, delayed_train


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
