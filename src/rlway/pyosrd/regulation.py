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
        {"train_id": int, "position": float, "duration": float}
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
