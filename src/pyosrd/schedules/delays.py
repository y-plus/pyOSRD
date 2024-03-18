
from typing import Protocol

import pandas as pd


class OSRD(Protocol):
    _df: pd.DataFrame


def delays(self, ref_schedule: OSRD) -> pd.DataFrame:

    delta = self._df - ref_schedule._df

    return (
        delta.loc[pd.IndexSlice[:], pd.IndexSlice[:, 's']]
        .set_axis(self._df.columns.levels[0], axis=1)
        .astype(float)
    )


def train_delay(self, train: int | str, ref_schedule: OSRD) -> pd.DataFrame:

    if isinstance(train, int):
        train = self.trains[train]

    return self.delays(ref_schedule).max().loc[train]


def compute_weighted_delay(
    self,
    ref_schedule,
    weights: pd.DataFrame
) -> float:
    """Compute an indicator to evaluate this Schedule.

    Compute an indicator based on the arrival times of the self
    compared to the ref_schedule ponderated by weights.

    The formula used is as follow ($s$ are all steps of the schedules,
    a step being a train in a zone):
        $$\sum_s [(delayed\_arrival - ref\_arrival)_s \times weight_s]$$

    Parameters
    ----------
    self: Schedule
        The delayed schedule, regulated use to compute the metric
    ref_schedule: Schedule
        The reference schedule used as the ideal schedule
    weights: pd.DataFrame
        The weights use to ponderate all delays

    Returns
    -------
    float
        The computed weighted delay
    """

    weighted_delays = self.delays(ref_schedule) * weights

    return weighted_delays.sum().sum()


def total_delay_at_stations(
    self,
    ref_schedule: OSRD,
    stations: list[int | str]
) -> float:

    weights = (
        self._df.loc[pd.IndexSlice[:], pd.IndexSlice[:, 's']]
        .set_axis(self._df.columns.levels[0], axis=1)
        .astype(float)
    ) * 0
    weights[weights.index.isin(stations)] = 1

    return self.compute_weighted_delays(ref_schedule, weights)
