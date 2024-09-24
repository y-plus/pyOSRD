import pandas as pd
from pyosrd.schedules import Schedule


def _times_spent_by_head(
    schedule: Schedule,
    train_label: str
) -> pd.Series:
       
    head_enters_at = (
        schedule.df.loc[:, (train_label, 's')]
        .dropna()
        .sort_values()
    )
    last_time = schedule.df.loc[
        head_enters_at.index[-1],
        (train_label, 'e')
    ]
    head_leaves_at = head_enters_at.shift(
        -1,
        fill_value=last_time
    )
    return head_leaves_at - head_enters_at


def delays_between_schedules(
    schedule: Schedule,
    ref_schedule: Schedule,
) -> dict[str, dict[str, float]]:
    """How much longer or shorter does trains spend in zones wrt a reference

    Parameters
    ----------
    schedule : Schedule
        Delayed schedule
    ref_schedule : Schedule
        Reference schedule

    Returns
    -------
    dict[str, dict[str, float]]
        Dict with format {train_label: {zone: delay [s], ...}, ...}
    """

    delays = dict()

    for train in ref_schedule.trains:
        delays_train = (
            _times_spent_by_head(schedule, train)
            - _times_spent_by_head(ref_schedule, train)
        ).round().to_dict()
        delays[train] = {
            k: v
            for k, v in delays_train.items()
            if v != 0
        }

    return {k: v for k, v in delays.items() if v}


def departure_shift_between_schedules(
    schedule: Schedule,
    ref_schedule: Schedule,
) -> dict[str, float]:

    departure_shift = dict()
    for train in schedule.trains:
        dep = schedule.df[train].min().min()
        dep_ref = ref_schedule.df[train].min().min()
        if dep != dep_ref:
            departure_shift[train] = dep - dep_ref
    return departure_shift