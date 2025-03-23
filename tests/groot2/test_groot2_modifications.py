import copy


class TestsAddDelay:

    def test_groot2_add_delay_start(self, groot2_1train):
        groot = copy.deepcopy(groot2_1train)
        original_times = {'train1': groot2_1train.times['train1']}
        modified_times = groot.add_delay('train1', 'A', 1)
        expected_times = {
            'A': (1, 4),
            'B': (3.5, 6.5),
            'C': (6, 9),
        }
        assert groot.times['train1'] == expected_times
        assert modified_times == original_times

    def test_groot2_add_delay(self, groot2_1train):
        groot = copy.deepcopy(groot2_1train)
        original_times = {'train1': groot2_1train.times['train1']}
        modified_times = groot.add_delay('train1', 'B', 1)
        expected_times = {
            'A': (0, 3),
            'B': (2.5, 6.5),
            'C': (6, 9),
        }
        assert groot.times['train1'] == expected_times
        assert modified_times == original_times


class TestsMakeTrainWait:

    def test_groot2_make_train_wait(self, groot2_2trains):
        groot = copy.deepcopy(groot2_2trains)
        groot.add_delay('train1', 'A', 2)
        original_times = {'train2': copy.deepcopy(groot.times['train2'])}

        modified_times = groot.make_train_wait(
            waiting_train='train2',
            priority_train='train1',
            wait_at='A',
            conflict_zone='A'
        )
        expected_times = {
            'A': (5, 8),
            'B': (7.5, 10.5),
            'C': (10, 13),
        }
        assert groot.times['train2'] == expected_times
        assert modified_times == original_times
    
    def test_groot2_make_train_wait_inversion(self, groot2_2trains):
        groot = copy.deepcopy(groot2_2trains)
        groot.add_delay('train1', 'A', 2)
        original_times = {'train1': copy.deepcopy(groot.times['train1'])}
        modified_times = groot.make_train_wait(
            waiting_train='train1',
            priority_train='train2',
            wait_at='A',
            conflict_zone='A'
        )
        expected_times = {
            'A': (7, 10),
            'B': (9.5, 12.5),
            'C': (12, 15),
        }
        assert groot.times['train1'] == expected_times
        assert modified_times == original_times