import datetime
import pandas as pd


def hour_to_seconds(hour: str) -> int:
    """Converts hour in string format to seconds

    Parameters
    ----------
    hour : str
        Hour in the format 'hh:mm:ss' optionally followed
        by 'am' or 'pm'
    Returns
    -------
    int
        Number of seconds since '00:00:00'

    Examples
    --------
    >>> from pyosrd.import hour_to_seconds
    >>> hour_to_seconds('01:00')
    3600
    >>> hour_to_seconds('08:15:23')
    29723
    >>> hour_to_seconds('8:00')
    28800
    >>> hour_to_seconds('8:00 pm')
    72000
    >>> hour_to_seconds('8:00pm')
    72000
    >>> hour_to_seconds('20:00')
    72000
    """
    return (pd.to_datetime(hour)-pd.to_datetime('0:00')).seconds


def seconds_to_hour(seconds: int) -> str:
    """Converts a number of seconds into an hour string format

    Parameters
    ----------
    seconds : int
        Number of seconds

    Returns
    -------
    str
        Hour in t the format 'hh:mm:ss". If the number of seconds
        corresponds to more than 24 hours, the output format will be
        'n days, hh:mm:ss"

    Examples
    --------
    >>> from pyosrd import seconds_to_hour
    >>> seconds_to_hour(3600)
    '01:00:00'
    >>> seconds_to_hour( 8 * 3600 + 15 * 60 + 23)
    '08:15:23'
    >>> seconds_to_hour( 20 * 3600)
    '20:00:00'
    >>> seconds_to_hour( 24 * 3600)
    '1 day, 0:00:00'
    >>> seconds_to_hour( 24 * 3600 + 8 * 3600 + 15 * 60 + 23)
    '1 day, 8:15:23'
    """
    delta = datetime.timedelta(seconds=seconds)
    return str(delta).zfill(8)
