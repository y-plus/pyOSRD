import matplotlib.pyplot as plt


def test_space_time_chart(simulation_cvg_dvg):

    ax = simulation_cvg_dvg.space_time_chart(0, points_to_show=['station'])

    assert ax.dataLim.xmin == 0.
    assert round(ax.dataLim.ymin) == 0.
    assert round(ax.dataLim.ymax) == (500. - 300.) + 2 * 500. + 490.
    assert (
        [label._text for label in ax.get_yticklabels()]
        == ['station0/T0', 'station1/T4']
    )
    assert ax.get_title() == "train0 (base)"
    plt.close()


def test_space_time_chart_by_label(simulation_cvg_dvg):

    ax = simulation_cvg_dvg.space_time_chart(
        'train0',
        points_to_show=['station'],
    )

    assert ax.dataLim.xmin == 0.
    assert round(ax.dataLim.ymin) == 0.
    assert round(ax.dataLim.ymax) == (500. - 300.) + 2 * 500. + 490.
    assert (
        [label._text for label in ax.get_yticklabels()]
        == ['station0/T0', 'station1/T4']
    )
    assert ax.get_title() == "train0 (base)"
    plt.close()
