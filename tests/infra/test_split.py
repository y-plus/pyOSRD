from pyosrd.infra.split import filter_by_track_section_ids


def test_split_point_switch(infra_point_switch):
    sub = filter_by_track_section_ids(infra_point_switch, ['T0', 'T1', 'T2'])
    switches = [switch['id'] for switch in sub.infra['switches']]
    assert 'CVG' not in switches
    dvg = next(sw for sw in sub.infra['switches'] if sw['id'] == 'DVG')
    assert dvg['switch_type'] == 'point_switch'


def test_split_point_switch_2(infra_point_switch):
    sub = filter_by_track_section_ids(infra_point_switch, ['T0', 'T1'])
    switches = [switch['id'] for switch in sub.infra['switches']]
    assert 'CVG' not in switches
    dvg = next(sw for sw in sub.infra['switches'] if sw['id'] == 'DVG')
    assert dvg['switch_type'] == 'link'


def test_split_crossing_1(infra_crossing):
    sub = filter_by_track_section_ids(infra_crossing, ['T1'])
    switches = [switch['id'] for switch in sub.infra['switches']]
    assert not switches


def test_split_crossing_2(infra_crossing):
    sub = filter_by_track_section_ids(infra_crossing, ['T0', 'T1'])
    switches = [switch['id'] for switch in sub.infra['switches']]
    assert not switches


def test_split_crossing_3(infra_crossing):
    sub = filter_by_track_section_ids(infra_crossing, ['T0', 'T2'])
    switches = [switch['id'] for switch in sub.infra['switches']]
    assert not switches


def test_split_crossing_4(infra_crossing):
    sub = filter_by_track_section_ids(infra_crossing, ['T0', 'T3'])
    sw = next(sw for sw in sub.infra['switches'] if sw['id'] == 'SW')
    assert sw['switch_type'] == 'link'


def test_split_crossing_5(infra_crossing):
    sub = filter_by_track_section_ids(infra_crossing, ['T1', 'T2'])
    sw = next(sw for sw in sub.infra['switches'] if sw['id'] == 'SW')
    assert sw['switch_type'] == 'link'


def test_split_crossing_6(infra_crossing):
    sub = filter_by_track_section_ids(infra_crossing, ['T0', 'T1', 'T2'])
    sw = next(sw for sw in sub.infra['switches'] if sw['id'] == 'SW')
    assert sw['switch_type'] == 'link'


def test_split_crossing_7(infra_crossing):
    sub = filter_by_track_section_ids(infra_crossing, ['T0', 'T1', 'T3'])
    sw = next(sw for sw in sub.infra['switches'] if sw['id'] == 'SW')
    assert sw['switch_type'] == 'link'


def test_split_crossing_8(infra_crossing):
    sub = filter_by_track_section_ids(infra_crossing, ['T0', 'T2', 'T3'])
    sw = next(sw for sw in sub.infra['switches'] if sw['id'] == 'SW')
    assert sw['switch_type'] == 'link'


def test_split_crossing_9(infra_crossing):
    sub = filter_by_track_section_ids(infra_crossing, ['T1', 'T2', 'T3'])
    sw = next(sw for sw in sub.infra['switches'] if sw['id'] == 'SW')
    assert sw['switch_type'] == 'link'


def test_split_crossing_10(infra_crossing):
    sub = filter_by_track_section_ids(infra_crossing, ['T0', 'T1', 'T3', 'T2'])
    sw = next(sw for sw in sub.infra['switches'] if sw['id'] == 'SW')
    assert sw['switch_type'] == 'crossing'


def test_split_double_slip_1(infra_double_slip):
    sub = filter_by_track_section_ids(infra_double_slip, ['T1'])
    switches = [switch['id'] for switch in sub.infra['switches']]
    assert not switches


def test_split_double_slip_2(infra_double_slip):
    sub = filter_by_track_section_ids(infra_double_slip, ['T0', 'T1'])
    switches = [switch['id'] for switch in sub.infra['switches']]
    assert not switches


def test_split_double_slip_3(infra_double_slip):
    sub = filter_by_track_section_ids(infra_double_slip, ['T2', 'T3'])
    switches = [switch['id'] for switch in sub.infra['switches']]
    assert not switches


def test_split_double_slip_4(infra_double_slip):
    sub = filter_by_track_section_ids(infra_double_slip, ['T0', 'T2'])
    sw = next(sw for sw in sub.infra['switches'] if sw['id'] == 'SW')
    assert sw['switch_type'] == 'link'


def test_split_double_slip_5(infra_double_slip):
    sub = filter_by_track_section_ids(infra_double_slip, ['T0', 'T3'])
    sw = next(sw for sw in sub.infra['switches'] if sw['id'] == 'SW')
    assert sw['switch_type'] == 'link'


def test_split_double_slip_6(infra_double_slip):
    sub = filter_by_track_section_ids(infra_double_slip, ['T0', 'T1', 'T2'])
    sw = next(sw for sw in sub.infra['switches'] if sw['id'] == 'SW')
    assert sw['switch_type'] == 'point_switch'


def test_split_double_slip_7(infra_double_slip):
    sub = filter_by_track_section_ids(infra_double_slip, ['T0', 'T1', 'T3'])
    sw = next(sw for sw in sub.infra['switches'] if sw['id'] == 'SW')
    assert sw['switch_type'] == 'point_switch'


def test_split_double_slip_8(infra_double_slip):
    sub = filter_by_track_section_ids(infra_double_slip, ['T0', 'T2', 'T3'])
    sw = next(sw for sw in sub.infra['switches'] if sw['id'] == 'SW')
    assert sw['switch_type'] == 'point_switch'


def test_split_double_slip_9(infra_double_slip):
    sub = filter_by_track_section_ids(infra_double_slip, ['T1', 'T2', 'T3'])
    sw = next(sw for sw in sub.infra['switches'] if sw['id'] == 'SW')
    assert sw['switch_type'] == 'point_switch'


def test_split_double_slip_10(infra_double_slip):
    sub = filter_by_track_section_ids(infra_double_slip, ['T0', 'T1', 'T3', 'T2'])
    sw = next(sw for sw in sub.infra['switches'] if sw['id'] == 'SW')
    assert sw['switch_type'] == 'double_slip_switch'


def test_split_missing_track(infra_station_c2):

    sub = filter_by_track_section_ids(
        infra_station_c2,
        ['T0',  'T3', 'T5'],
    )
    track_sections = [t['id'] for t in sub.infra['track_sections']]
    assert 'T1' in track_sections
