def test_schedules_previous_switch(schedule_station_capacity2):

    assert schedule_station_capacity2.previous_switch(
        0,
        'CVG'
    ) == 'DVG'
    assert schedule_station_capacity2.previous_switch(
        'train1', 'CVG'
    ) == 'DVG'


def test_schedules_previous_station(schedule_station_capacity2):

    assert schedule_station_capacity2.previous_station(
        0,
        'CVG'
    ) == 'D1<->D3'
    assert schedule_station_capacity2.previous_station(
        'train1', 'CVG'
    ) == 'D2<->D4'


def test_schedules_previous_signal(schedule_station_capacity2):

    assert schedule_station_capacity2.previous_signal(
        0,
        'CVG'
    ) == 'D1<->D3'
    assert schedule_station_capacity2.previous_signal(
        'train1', 'CVG'
    ) == 'D2<->D4'


def test_schedules_prev_switch_protecting_signal(schedule_station_capacity2):

    assert schedule_station_capacity2.previous_switch_protecting_signal(
        0,
        'CVG'
    ) == 'D1<->D3'
    assert schedule_station_capacity2.previous_switch_protecting_signal(
        'train1', 'CVG'
    ) == 'D2<->D4'
    assert schedule_station_capacity2.previous_switch_protecting_signal(
        0,
        'D1<->D3'
    ) == 'D0<->buffer_stop.0'
    assert schedule_station_capacity2.previous_switch_protecting_signal(
        'train1', 'D2<->D4'
    ) == 'D0<->buffer_stop.0'


def test_schedules_previous_methods_wrong_zone(schedule_station_capacity2):

    assert schedule_station_capacity2.previous_switch(
        0,
        'D2<->D4'
    ) is None
    assert schedule_station_capacity2.previous_station(
        0,
        'D2<->D4'
    ) is None
    assert schedule_station_capacity2.previous_signal(
        0,
        'D2<->D4'
    ) is None
    assert schedule_station_capacity2.previous_switch_protecting_signal(
        0,
        'D2<->D4'
    ) is None


def test_schedules_previous_methods_no_zone_found(schedule_station_capacity2):

    assert schedule_station_capacity2.previous_switch(
        0,
        'D0<->buffer_stop.0'
    ) is None
    assert schedule_station_capacity2.previous_station(
        0,
        'D0<->buffer_stop.0'
    ) is None
    assert schedule_station_capacity2.previous_signal(
        0,
        'D0<->buffer_stop.0'
    ) is None
    assert schedule_station_capacity2.previous_switch_protecting_signal(
        0,
        'D0<->buffer_stop.0'
    ) is None
