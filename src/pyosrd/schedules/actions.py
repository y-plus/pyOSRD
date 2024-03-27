import copy
from typing import Protocol
import pandas as pd


class OSRD(Protocol):
    _df: pd.DataFrame
    starts: pd.DataFrame
    ends: pd.DataFrame


def shift_train_departure(
    self: OSRD,
    train: int,
    time: float
) -> OSRD:
    """Shift the departure by a given time

    All the trajectory is shifted

    Parameters
    ----------
    train : int
        Train index
    time : float
        Departure's delay

    Returns
    -------
    Schedule
        The new schedule
    """

    new_schedule = copy.deepcopy(self)

    new_schedule._df[train] += time

    return new_schedule


def add_delay(
    self: OSRD,
    train: int,
    zone: int | str,
    delay: float
) -> OSRD:

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
    self: OSRD,
    train1: int,
    train2: int,
    zone: int | str
) -> OSRD:
    """Train1 waits until train 2 has freed the zone"""

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


def propagate_delay(self, delayed_train: int) -> tuple[OSRD, int]:

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
