import json
import os


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
        {"train": int, "position": float, "duration": float}
    """

    for stop in stops:

        group, idx = self._train_schedule_group[
            self.trains[stop['train']]
        ]

        group_idx = _group_idx(self, group)

        self.simulation['train_schedule_groups'][group_idx]['schedules'][idx]['stops'] += \
            [{'duration': stop['duration'], 'position': stop['position']}]  # noqa

    with open(os.path.join(self.dir, self.simulation_json), "w") as outfile:
        json.dump(self.simulation, outfile)
    self.run()


def add_stop(
    self,
    train: int,
    position: float,
    duration: float,
) -> None:
    """Add a stop  and re-run the simulation

    Parameters
    ----------
    train : int
        Train index
    position : float
        Offset in train's path in m
    duration : float
    Stop duration in seconds
    """
    add_stops(
        self,
        [
            {
                "train": train,
                "position": position,
                "duration": duration
            }
        ]
    )
