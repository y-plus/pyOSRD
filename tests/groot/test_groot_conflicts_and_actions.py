
class TestsAddDelay:

    def test_groot_add_delay_start(self, groot_1train):
        delayed = groot_1train.add_delay('train1', 'A', 1)
        expected_times = {
            'A': (1, 4),
            'B': (3.5, 6.5),
            'C': (6, 9),
        }
        assert delayed.times['train1'] == expected_times


    def test_groot_add_delay(self, groot_1train):
        delayed = groot_1train.add_delay('train1', 'B', 1)
        expected_times = {
            'A': (0, 3),
            'B': (2.5, 6.5),
            'C': (6, 9),
        }
        assert delayed.times['train1'] == expected_times


class TestsConflicts:

    def test_groot_has_conflicts(self, groot_2trains):
        assert not groot_2trains.has_conflicts()
        disrupted = groot_2trains.add_delay('train1', 'A', 2)
        assert disrupted.has_conflicts()

    def test_groot_earliest_conflict(self, groot_2trains):
        disrupted = groot_2trains.add_delay('train1', 'A', 2)
        assert disrupted.earliest_conflict() == ('train1', 'train2', 'A', 2)

    def test_groot_earliest_conflict2(self, groot_2trains):
        disrupted = groot_2trains.add_delay('train1', 'B', 2)
        assert disrupted.earliest_conflict() == ('train1', 'train2', 'B', 2.5)

class TestsMakeTrainWait:

    def test_groot_make_train_wait(self, groot_2trains):
        disrupted = groot_2trains.add_delay('train1', 'A', 2)
        dispatched = disrupted.make_train_wait(
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
        assert dispatched.times['train2'] == expected_times
    
    def test_groot_make_train_wait_inversion(self, groot_2trains):
        disrupted = groot_2trains.add_delay('train1', 'A', 2)
        dispatched = disrupted.make_train_wait(
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
        assert dispatched.times['train1'] == expected_times