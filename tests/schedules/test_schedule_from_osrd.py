from pyosrd.schedules import schedule_from_osrd


def test_schedule_from_osrd(use_case_cvg_dvg):
    s = schedule_from_osrd(use_case_cvg_dvg)
    assert set(s.zones) == set([
        'D0<->buffer_stop.0',
        'CVG',
        'D2<->D3',
        'D1<->buffer_stop.1',
        'DVG',
        'D4<->buffer_stop.2',
        'D5<->buffer_stop.3',
    ])
    assert list(s._df.columns.levels[0]) == ['train0', 'train1']
    assert s.trains == use_case_cvg_dvg.trains


def test_schedule_from_osrd_merge(use_case_double_switch):
    s = schedule_from_osrd(use_case_double_switch)
    print(s)
    assert len(s.zones) == 5
    assert 'SW0+SW1' in s.zones
