

import json
import os


def time_train_is_at_point_id(
    self,
    train: int,
    point_id: str,
    eco_or_base: str = 'base',
) -> float:
    """At what time a given train arrives at a given encountered point ?"""
    return [
        point[f't_{eco_or_base}']
        for point in self.points_encountered_by_train(train)
        if point['id'] == point_id
    ][0]


def add_delay_in_results(
    self,
    train: int,
    point_id: str,
    delay: float,
    eco_or_base: str = 'base',
) -> None:
    """Add a delay to a train after a given point by updating results & .json

    Warning: route_occupancies are not updated

    Parameters
    ----------
    self : OSRD
       OSRD simulation object
    train : int
        train index
    point_id : str
        Point id
    delay : float
        Delay in seconds
    eco_or_base : str, optional
        Modify eco or base simulation ?, by default 'base'
    """

    time_threshold = time_train_is_at_point_id(self, train, point_id)

    group, idx = self._train_schedule_group[
        self.trains[train]
    ]

    for eco_or_base in ['eco', 'base']:
        sim = f'{eco_or_base}_simulations'

        dict = (
            self.results[group][sim][idx]
            if self.results[group][sim] != [None]
            else {}
        )
        for key, records in dict.items():
            if isinstance(records, list):
                for i, record in enumerate(records):
                    for subkey, value in record.items():
                        if 'time' in subkey and value > time_threshold:
                            self.results[group][sim][idx][key][i][subkey] += \
                                delay

    with open(os.path.join(self.dir, self.results_json), "w") as outfile:
        json.dump(self.results, outfile)


def _group_idx(self, group: str) -> int:
    return [
        group['id']
        for group in self.simulation['train_schedule_groups']
    ].index(group)


def add_stops(
    self,
    stops: list[dict[str, int | str]]
) -> None:
    """Add a list of stops  and re-run the simulation

    Parameters
    ----------
    stops : list[dict[str, float  |  str]]
        List of stops described by a dictionnary with 3 keys:
        {"train_id": int, "position": float, "duration": float}
    """

    for stop in stops:

        group, idx = self._train_schedule_group[
            self.trains[stop['train']]
        ]

        group_idx = _group_idx(self, group)

        self.simulation['train_schedule_groups'][group_idx]['schedules'][idx]['stops'] += \
            [{'duration': stop['duration'], 'position': stop['position']}]

    with open(os.path.join(self.dir, self.simulation_json), "w") as outfile:
        json.dump(self.simulation, outfile)
    self.run()
