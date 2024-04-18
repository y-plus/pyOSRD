from pyosrd.utils import hour_to_seconds, seconds_to_hour


def test_time_conversions_hour_to_seconds():
    assert hour_to_seconds('01:00') == 3600
    assert hour_to_seconds('08:15:23') == 8 * 3600 + 15 * 60 + 23
    assert hour_to_seconds('8:00') == 8 * 3600
    assert hour_to_seconds('8:00 pm') == 3600 * 20
    assert hour_to_seconds('8:00pm') == 3600 * 20
    assert hour_to_seconds('20:00') == 3600 * 20


def test_time_conversions_reciprocity():
    assert seconds_to_hour(hour_to_seconds('01:00')) == '01:00:00'
    assert hour_to_seconds(seconds_to_hour(3600)) == 3600


def test_time_conversions_seconds_to_hour():
    assert seconds_to_hour(3600) == '01:00:00'
    assert seconds_to_hour(8 * 3600 + 15 * 60 + 23) == '08:15:23'
    assert seconds_to_hour(20 * 3600) == '20:00:00'
    assert seconds_to_hour(24 * 3600) == '1 day, 0:00:00'
    assert seconds_to_hour(24 * 3600 + 8 * 3600 + 15 * 60 + 23) == \
        '1 day, 8:15:23'
