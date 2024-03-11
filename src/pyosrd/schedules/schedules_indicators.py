import pandas as pd

from . import Schedule


def compute_ponderated_delays(
    ref_schedule: Schedule,
    delayed_schedule: Schedule,
    weights: pd.DataFrame
) -> float:
    """
    Compute an indicator to evaluate a delayed Schedule.

    Compute an indicator based on the arrival times of the delayed_schedule
    compared to the ref_schedule ponderated by weights.

    The formula used is as follow (s are all steps of the schedules, a step
    being a train in a zone):
        $$sum_s (delayed\_arrival - ref\_arrival)_s \times weight_s$$

    Parameters
    ----------
    ref_schedule: Schedule
        The reference schedule used as the ideal schedule
    delayed_schedule: Schedule
        The delayed schedule, regulated use to compute the metric
    weights: pd.DataFrame
        The weights use to ponderate all delays
    """
    starts = ref_schedule.starts
    delayed_starts = delayed_schedule.starts

    result = (delayed_starts - starts) * weights

    return result.sum().sum()
