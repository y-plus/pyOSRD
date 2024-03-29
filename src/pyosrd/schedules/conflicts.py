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


def first_conflict(self, train: int | str) -> tuple[int, int]:

    if isinstance(train, int):
        train = self.trains[train]

    c = self.conflicts(train).stack()
    zone, other_train = c.index[np.argmin(c)]
    return zone, other_train


def earliest_conflict(self) -> tuple[int | str, str, int | str]:
    """ Returns the zone where earliest conflict occurs,
    first train in and last in."""
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
            self.first_conflict(other_train)[0],
            self.first_conflict(other_train)[1],
            other_train
            )
    return None, None, None
