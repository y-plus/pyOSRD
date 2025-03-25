from pyosrd.groot2.actions.utils import head_to_head, is_a_convergence, is_a_divergence


def test_is_a_convergence(groot2_reroute) -> None:

    for tvd in (
        'buffer_stop.0->D0',
        'D0->D1',
        'D1->D4',
        'D4->D7',
        'D1->D3',
        'D3->D6',
        'D0->D2',
        'D2->D5',
        'D9->buffer_stop.6',

    ):
        assert not is_a_convergence(groot2_reroute, tvd)

    for tvd in (
        'D5->D9',
        'D6->D8',
        'D8->D9',
        'D7->D8',
    ):
        assert is_a_convergence(groot2_reroute, tvd)


def test_is_a_divergence(groot2_reroute) -> None:

    for tvd in (
        'buffer_stop.0->D0',
        'D4->D7',
        'D3->D6',
        'D2->D5',
        'D9->buffer_stop.6',
        'D5->D9',
        'D6->D8',
        'D8->D9',
        'D7->D8',

    ):
        assert not is_a_divergence(groot2_reroute, tvd)

    for tvd in (
        'D0->D1',
        'D1->D4',
        'D1->D3',
        'D0->D2',
    ):
        assert is_a_divergence(groot2_reroute, tvd)


def test_groot2_head_to_head(groot_vu_crossing) -> None:

    assert head_to_head(groot_vu_crossing, 'train00', 'train01', 'A/V1')
    assert not head_to_head(groot_vu_crossing, 'train00', 'train02', 'A/V1')