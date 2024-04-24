import pytest

from pandas.testing import assert_frame_equal

from pyosrd.schedules import Schedule


def test_schedules_interlocking_switch_change_delay(two_trains):

    expected = Schedule(6, 2)

    expected.df.at[0, 0] = [0, 1]
    expected.df.at[2, 0] = [1, 2.5]
    expected.df.at[3, 0] = [2, 3.5]
    expected.df.at[4, 0] = [3, 4]

    expected.df.at[1, 1] = [1, 2]
    expected.df.at[2, 1] = [2, 3]
    expected.df.at[3, 1] = [3, 4]
    expected.df.at[5, 1] = [4, 5]

    expected.set_train_labels(['train1', 'train2'])

    assert_frame_equal(
        two_trains.with_interlocking_constraints(switch_change_delay=.5).df,
        expected.df
    )


def test_schedules_interlocking_1_block_btw_trains(two_trains_in_line):

    expected = Schedule(3, 2)

    expected.df.at[0, 0] = [0, 2]
    expected.df.at[1, 0] = [1, 3]
    expected.df.at[2, 0] = [2, 3]

    expected.df.at[0, 1] = [1, 2]
    expected.df.at[1, 1] = [2, 3]
    expected.df.at[2, 1] = [3, 4]

    expected.set_train_labels(['train1', 'train2'])

    assert_frame_equal(
        two_trains_in_line.with_interlocking_constraints().df,
        expected.df
    )


def test_schedules_interlocking_0_block_btw_trains(two_trains_in_line):

    assert_frame_equal(
        two_trains_in_line.with_interlocking_constraints(
            n_blocks_between_trains=0
        ).df,
        two_trains_in_line.df
    )


def test_schedules_interlocking_2_blocks_raise_exception(two_trains_in_line):
    with pytest.raises(NotImplementedError):
        two_trains_in_line.with_interlocking_constraints(
            n_blocks_between_trains=2
        ).df
