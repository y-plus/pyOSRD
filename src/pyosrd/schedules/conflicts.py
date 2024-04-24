import warnings
import numpy as np
import pandas as pd


def conflicts(self, train: int | str) -> pd.DataFrame:

    if isinstance(train, int):
        train = self.trains[train]

    starts0 = (
        pd.concat([self._df[train, 's']]*self.num_trains, axis=1)
        .set_axis(self.trains, axis=1)
    )
    ends0 = (
        pd.concat([self._df[train, 'e']]*self.num_trains, axis=1)
        .set_axis(self.trains, axis=1)
    )
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        mask1 = self.ends >= starts0

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        mask1 = self.ends >= starts0

    max_starts = (
        pd.concat([starts0, self.starts])
        .rename_axis('index')
        .groupby('index').max()
    )
    min_ends = (
        pd.concat([ends0, self.ends])
        .rename_axis('index')
        .groupby('index').min()
    )
    mask2 = max_starts < min_ends

        conflict_times = self.starts[mask1 & mask2].drop(columns=train)

    return (conflict_times[conflict_times.notna()])


def has_conflicts(self, train: int | str) -> bool:

    if isinstance(train, int):
        train = self.trains[train]

    return ~self.conflicts(train).isna().all().all()


def train_first_conflict(self, train: int | str) -> tuple[int, int]:

    if isinstance(train, int):
        train = self.trains[train]

    c = self.conflicts(train).stack()
    zone, other_train = c.index[np.argmin(c)]
    return zone, other_train


def earliest_conflict(self) -> tuple[int | str, str, int | str]:
    """ Returns the zone where earliest conflict occurs,
    first train in and last in."""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')

        conflicts_times = [
            np.min(self.conflicts(train).stack())
            if not self.conflicts(train).stack().empty
            else np.inf
            for train in self.trains
        ]

        if np.isfinite(np.min(conflicts_times)):

            other_train = np.argmin(conflicts_times)
            other_train = self.trains[other_train]

            return (
                self.train_first_conflict(other_train)[0],
                self.train_first_conflict(other_train)[1],
                other_train
                )
        return None, None, None


def are_conflicted(self, train1: int | str, train2: int | str) -> bool:
    """Is there any conflict between two given trains ?"""

    return first_conflict_zone(self, train1, train2) is not None


def first_conflict_zone(self, train1: int | str, train2: int | str) -> str:

    if isinstance(train1, int):
        train1 = self.trains[train1]

    if isinstance(train2, int):
        train2 = self.trains[train2]

    conflicts = self.conflicts(train1)[train2]
    if conflicts.isna().all():
        return
    return conflicts.idxmin()


def no_conflict(self) -> bool:
    "Is there any conflict in the schedule ?"
    return self.earliest_conflict()[0] is None
